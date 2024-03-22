from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi

from method_type import MethodType


class _TextSummarizer:
    def __init__(self):
        self.prompt = ChatPromptTemplate.from_template(
            """文章を日本語で要約して。要約の仕方は、複数のポイントに対してそれぞれ詳しく説明するかんじ:\n{input}"""
        )
        self.model = ChatAnthropic(model="claude-3-opus-20240229")
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

    def _get_youtube_content(self, url: str) -> str:
        video_id = url.split("v=")[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ja", "en"])
        content = ""
        for i in transcript:
            content += i["text"]
        return content

    def summarize(self, url: str) -> str:
        content = self._get_youtube_content(url)
        return self.summarize_chain.summarize(content)


class SummarizerBuilder:

    def build_summarizer(self, method: str) -> BaseSummarizer | None:
        text_summarizer = _TextSummarizer()
        summerizer_map = {
            MethodType.WEB.value: WebSummarizer(text_summarizer),
            MethodType.YOUTUBE.value: YouTubeSummarizer(text_summarizer),
            MethodType.NONE.value: None,
        }
        return summerizer_map[method]
