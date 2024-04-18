import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


PROMPT_URL_EXTRACTOR = """
以下のコメントから、「人間が URL だと認識する文字列」を抽出して。
例えば、不自然に URL 文字列が途切れているならば、それを修正して抽出すること。
クエリパラメータが含まれている場合は、それを含めて抽出すること。
そうしたものが存在しなければ ”NONE” と返して。
---
{comment}
"""


class URLExtractor:
    def __init__(self, system_prompt: str = PROMPT_URL_EXTRACTOR) -> None:
        outputparser = StrOutputParser()
        context = {
            "comment": RunnablePassthrough(),
        }
        prompt = ChatPromptTemplate.from_messages([("user", system_prompt)])
        model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
        self.chain = context | prompt | model | outputparser

    def extract(self, comment: str) -> str | None:
        extracted_url = self.chain.invoke(comment)
        if extracted_url == "NONE":
            logger.info("No URL extracted")
            return None
        logger.info(f"Extracted URL: {extracted_url}")
        return extracted_url


PROMPT_DISPATCHER = """
以下に与えられた URL が、以下のどれにカテゴライズするかを判定して、その結果を文字列で返して。
返すのは文字列だけで、それ以外の情報は不要。
何にも当てはまらない場合は ”Web” と返して。
- "YouTube": YouTube 動画
- "arXiv": arXiv の論文
- "Web": 一般的な Web ページ
---
{url}
"""


class Dispatcher:
    def __init__(self, system_prompt: str = PROMPT_DISPATCHER) -> None:
        outputparser = StrOutputParser()
        prompt = ChatPromptTemplate.from_messages([("user", system_prompt)])
        model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125")
        self.chain = prompt | model | outputparser

    def dispatch(self, url: str) -> str:
        method = self.chain.invoke(url)
        logger.info(f"Dispatched method: {method}")
        return method
