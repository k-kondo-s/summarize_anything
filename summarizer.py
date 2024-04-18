import logging
import os
from abc import ABC, abstractmethod

import cloudscraper
from bs4 import BeautifulSoup
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from pydub import AudioSegment
from pydub.utils import make_chunks
from youtube_transcript_api import YouTubeTranscriptApi
from yt_dlp import YoutubeDL

from method_type import MethodType

logger = logging.getLogger(__name__)


class HTTPClient:
    def __init__(self) -> None:
        self.client = cloudscraper.create_scraper()

    def get(self, url: str) -> str:
        html_content = self.client.get(url).text
        body_text = BeautifulSoup(html_content, "html.parser").get_text()
        return body_text


PROMPT_WRITER_TEXT_SUMMARIER = """
以下の文章の要点を抽出して、それぞれに対して詳細に説明をして。

制約条件:
- 冒頭にタイトルを記載する
- 要約以外の情報は不要
- bullet に数字は使わない
- 可能な限り日本語で記述する

品質を上げるヒント:
- 本文の中に具体例がある場合はそれを含めると良い。必要に応じてそのまま引用する。
---
{input}
"""

PROMPT_REVISER_TEXT_SUMMARIER = """
{target_text}
---

上の文章が要約として適切かどうかを判断し、適切ではない場合は【資料】に基づいて修正して。

- 要点に対して、もっと詳細に説明する。
- 本文の中に具体例がある場合はそれを含める。必要に応じてそのまま引用する。
- 修正する際は、【資料】に基づいて正確な情報を提供すること。
- 可能な限り日本語で記述されているか。
---
【資料】
{input}
"""


class TextSummarizer:
    def __init__(self):
        self.writer_chain = self.build_writer_chain()
        self.reviser_chain = self.build_reviser_chain()

    def build_writer_chain(self) -> BaseChatModel:
        self.prompt = ChatPromptTemplate.from_template(PROMPT_WRITER_TEXT_SUMMARIER)
        # max_tokens_to_sample は、default の 1024 だと文章が切れることがあるみたいなので 2000 に設定する。
        # 2000 以下にしないと Discord のメッセージ上限に引っかかる。
        self.model = ChatAnthropic(
            model="claude-3-opus-20240229", temperature=0, max_tokens_to_sample=4096
        )
        self.output_parser = StrOutputParser()
        return self.prompt | self.model | self.output_parser

    def build_reviser_chain(self) -> BaseChatModel:
        self.prompt = ChatPromptTemplate.from_template(PROMPT_REVISER_TEXT_SUMMARIER)
        # max_tokens_to_sample は、default の 1024 だと文章が切れることがあるみたいなので 2000 に設定する。
        # 2000 以下にしないと Discord のメッセージ上限に引っかかる。
        self.model = ChatAnthropic(
            model="claude-3-opus-20240229", temperature=0, max_tokens_to_sample=4096
        )
        self.output_parser = StrOutputParser()
        return self.prompt | self.model | self.output_parser

    def summarize(self, input):
        target_text = self.writer_chain.invoke({"input": input})
        return self.reviser_chain.invoke({"target_text": target_text, "input": input})


class BaseSummarizer(ABC):
    @abstractmethod
    def summarize(self, url: str) -> str:
        pass


class WebSummarizer(BaseSummarizer):
    def __init__(
        self, text_summarizer: TextSummarizer, http_client: HTTPClient
    ) -> None:
        self.text_summrizer = text_summarizer
        self.http_client = http_client

    def summarize(self, url: str) -> str:
        body_text = self.http_client.get(url)
        return self.text_summrizer.summarize(body_text)


class YouTubeSummarizer(BaseSummarizer):
    def __init__(self, text_summarizer: TextSummarizer) -> None:
        self.text_summrizer = text_summarizer

    def _get_video_id(self, url: str) -> str:
        """deprecated"""
        # いくつか異なる形式の URL に対応する
        # まず https://www.youtube.com/watch?v=xxxxx 形式の URL から video_id を取得する
        if "v=" in url:
            return url.split("v=")[1]
        # 次に https://youtu.be/xxxxx 形式の URL から video_id を取得する
        if "youtu.be" in url:
            return url.split("/")[-1]
        # どちらの形式でもない場合は例外を発生させる
        logger.error(f"Invalid URL format: {url}")
        raise ValueError(f"Invalid URL format: {url}")

    def _get_youtube_content(self, video_id: str) -> str:
        """deprecated"""
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["ja", "en"]
        )
        content = ""
        for i in transcript:
            content += i["text"]
        return content

    def transcribe_with_youtube_transcript_api(self, url: str) -> str:
        video_id = self._get_video_id(url)
        content = self._get_youtube_content(video_id)
        return content

    def _download_audio(self, url: str) -> str:
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": "audio",
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "audio.mp3"

    def transcribe_with_whisper(self, url: str) -> str:
        audio_file = self._download_audio(url)
        # 10 分ごとに分割する
        audio_files = self._split_audio(audio_file)
        content = ""
        for audio_file in audio_files:
            content += self._transcribe(audio_file)
        self._post_processing(audio_files)
        return content

    def _transcribe(self, audio_file: str) -> str:
        # Whisper を使う理由は、文字起こしの性能が普通より高いことと、たまに日本語の subtitle に対応していない
        # 動画も存在するから。デメリットは遅くなること。
        client = OpenAI()
        audio_file = open(audio_file, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        logger.info("Transcripted.")
        return transcription.text

    def _split_audio(self, audio_file: str) -> list[str]:
        audio = AudioSegment.from_file(audio_file, format="mp3")
        chunk_length_ms = 10 * 60 * 1000
        chunks = make_chunks(audio, chunk_length_ms)
        audio_files = []
        for i, chunk in enumerate(chunks):
            chunk.export(f"audio_{i}.mp3", format="mp3")
            audio_files.append(f"audio_{i}.mp3")
        return audio_files

    def _post_processing(self, audio_files) -> None:
        """ダウンロードした audio ファイルを削除する"""
        os.remove("audio.mp3")
        for audio_file in audio_files:
            os.remove(audio_file)
        logger.info("Removed audio files.")

    def summarize(self, url: str) -> str:
        try:
            logger.info("Try to transcribe with YouTubeTranscriptAPI.")
            content = self.transcribe_with_youtube_transcript_api(url)
        except Exception:
            logger.info("Failed to transcribe with YouTubeTranscriptAPI. Use Whisper.")
            content = self.transcribe_with_whisper(url)
        return self.text_summrizer.summarize(content)


class ArXivSummarizer(BaseSummarizer):
    def __init__(
        self, text_summarizer: TextSummarizer, http_client: HTTPClient
    ) -> None:
        self.text_summrizer = text_summarizer
        self.http_client = http_client

    def _modify_arxiv_url(self, url: str) -> str:
        """
        https://ar5iv.labs.arxiv.org/
        に習って、 arXiv の URL を変換して HTML のページを見られるようにする

           https://arxiv.org/abs/1910.06709
        -> https://ar5iv.org/abs/1910.06709
        """
        return url.replace("arxiv.org", "ar5iv.org")

    def summarize(self, url: str) -> str:
        modified_url = self._modify_arxiv_url(url)
        body_text = self.http_client.get(modified_url)
        return self.text_summrizer.summarize(body_text)


class SummarizerBuilder:
    def build_summarizer(self, method: str) -> BaseSummarizer | None:
        text_summarizer = TextSummarizer()
        http_client = HTTPClient()
        summerizer_map = {
            MethodType.WEB.value: WebSummarizer(text_summarizer, http_client),
            MethodType.YOUTUBE.value: YouTubeSummarizer(text_summarizer),
            MethodType.ARXIV.value: ArXivSummarizer(text_summarizer, http_client),
            MethodType.NONE.value: None,
        }
        return summerizer_map[method]
