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
以下の文章の要点を抽出して、それぞれに対して詳細に説明をして。

制約条件:
- 要約以外の情報は不要
- bullet に数字は使わない

品質を上げるヒント:
- 本文の中に具体例がある場合はそれを含めると良い。必要に応じてそのまま引用する。
---
{input}
"""


class TextSummarizer:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(PROMPT_TEXT_SUMMARIER)
        # max_tokens_to_sample は、default の 1024 だと文章が切れることがあるみたいなので 2000 に設定する。
        # 2000 以下にしないと Discord のメッセージ上限に引っかかる。
        self.model = ChatAnthropic(
            model="claude-3-opus-20240229", temperature=0, max_tokens_to_sample=4096
        )
        self.output_parser = StrOutputParser()
        self.chain = self.prompt | self.model | self.output_parser

    def summarize(self, input):
        return self.chain.invoke({"input": input})


class BaseSummarizer(ABC):
    @abstractmethod
    def summarize(self, url: str) -> str:
        pass


class WebSummarizer(BaseSummarizer):
    def __init__(self, text_summarizer: TextSummarizer) -> None:
        self.text_summrizer = text_summarizer

    def _reqest_get(self, url: str) -> str:
        """Send a GET request to the given URL and retrieve the body of the page."""
        response = requests.get(url)
        html_content = response.text

        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_content, "html.parser")

        # Get the body text
        body_text = soup.get_text()

        return body_text

    def summarize(self, url: str) -> str:
        body_text = self._reqest_get(url)
        return self.text_summrizer.summarize(body_text)


class YouTubeSummarizer(BaseSummarizer):
    def __init__(self, text_summarizer: TextSummarizer) -> None:
        self.text_summrizer = text_summarizer

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
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["ja", "en"]
        )
        content = ""
        for i in transcript:
            content += i["text"]
        return content

    def summarize(self, url: str) -> str:
        content = self._get_youtube_content(url)
        return self.text_summrizer.summarize(content)


class ArXivSummarizer(BaseSummarizer):
    def __init__(self, text_summarizer: TextSummarizer) -> None:
        self.text_summrizer = text_summarizer

    def _modify_arxiv_url(self, url: str) -> str:
        """
        https://ar5iv.labs.arxiv.org/
        に習って、 arXiv の URL を変換して HTML のページを見られるようにする

           https://arxiv.org/abs/1910.06709
        -> https://ar5iv.org/abs/1910.06709
        """
        return url.replace("arxiv.org", "ar5iv.org")

    def _get_arxiv_content(self, url: str) -> str:
        response = requests.get(url)
        html_content = response.text

        # BeautifulSoupオブジェクトを作成
        soup = BeautifulSoup(html_content, "html.parser")

        # ボディテキストを取得
        body_text = soup.get_text()

        return body_text

    def summarize(self, url: str) -> str:
        modified_url = self._modify_arxiv_url(url)
        body_text = self._get_arxiv_content(modified_url)
        return self.text_summrizer.summarize(body_text)


class SummarizerBuilder:
    def build_summarizer(self, method: str) -> BaseSummarizer | None:
        text_summarizer = TextSummarizer()
        summerizer_map = {
            MethodType.WEB.value: WebSummarizer(text_summarizer),
            MethodType.YOUTUBE.value: YouTubeSummarizer(text_summarizer),
            MethodType.ARXIV.value: ArXivSummarizer(text_summarizer),
            MethodType.NONE.value: None,
        }
        return summerizer_map[method]
