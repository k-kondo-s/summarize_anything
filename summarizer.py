import logging
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi

from method_type import MethodType

logger = logging.getLogger(__name__)

PROMPT_TEXT_SUMMARIER = """
文章を日本語で要約して。要約の仕方は、複数のポイントに対してそれぞれ詳しく説明するかんじ。
「ポイント1」「ポイント2」という具合に:
---
{input}
"""


class _TextSummarizer:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(PROMPT_TEXT_SUMMARIER)
        self.model = ChatAnthropic(model="claude-3-opus-20240229", temperature=0)
        self.output_parser = StrOutputParser()
        self.chain = self.prompt | self.model | self.output_parser

    def summarize(self, input):
        return self.chain.invoke({"input": input})


class BaseSummarizer(ABC):
    @abstractmethod
    def summarize(self, url: str) -> str:
        pass


class WebSummarizer(BaseSummarizer):
    def __init__(self, text_summarizer: _TextSummarizer) -> None:
        self.text_summrizer = text_summarizer

    def _reqest_get(self, url: str) -> str:
        """与えられた URL に GET リクエストを送りそのページの body を取得する"""
        response = requests.get(url)
        html_content = response.text

        # BeautifulSoupオブジェクトを作成
        soup = BeautifulSoup(html_content, "html.parser")

        # ボディテキストを取得
        body_text = soup.body.get_text(strip=True)

        return body_text

    def summarize(self, url: str) -> str:
        body_text = self._reqest_get(url)
        return self.text_summrizer.summarize(body_text)


class YouTubeSummarizer(BaseSummarizer):
    def __init__(self, text_summrizer: _TextSummarizer) -> None:
        self.text_summrizer = text_summrizer

    def _get_video_id(self, url: str) -> str:
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

    def _get_youtube_content(self, url: str) -> str:
        video_id = self._get_video_id(url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ja", "en"])
        content = ""
        for i in transcript:
            content += i["text"]
        return content

    def summarize(self, url: str) -> str:
        content = self._get_youtube_content(url)
        return self.text_summrizer.summarize(content)


class SummarizerBuilder:

    def build_summarizer(self, method: str) -> BaseSummarizer | None:
        text_summarizer = _TextSummarizer()
        summerizer_map = {
            MethodType.WEB.value: WebSummarizer(text_summarizer),
            MethodType.YOUTUBE.value: YouTubeSummarizer(text_summarizer),
            MethodType.NONE.value: None,
        }
        return summerizer_map[method]
