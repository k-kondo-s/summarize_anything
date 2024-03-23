import logging

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from method_type import MethodType

logger = logging.getLogger(__name__)

PROMPT = """
{comment}
---
このコメントがサマリを必要としているかを判定したい。サマリを必要としている場合は、サマル対象の URL とサマリの方法を返す。

例:
comment: ブログ書いたよ
output: False, "", "None"

comment: https://www.youtube.com/watch?v=123456
output: True, "https://www.youtube.com/watch?v=123456", YouTube

comment: 良い論文だ https://arxiv.org/abs/2202.12493
output: True, "https://arxiv.org/abs/2202.12493", arXiv

comment: https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7 これは僕が書いたやつ
output: True, "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7", Web


{format_instruction}
"""


class Router:

    class OutputFormat(BaseModel):
        """Output format of the router"""

        summary_required: bool = Field(description="Summary Required if URL string is included in the comment")
        url: str = Field(description="URL")
        method: MethodType = Field(description="Kind of method to summarize the URL")

    def __init__(self):
        json_outputparser = JsonOutputParser(pydantic_object=self.OutputFormat)
        context = {
            "format_instruction": lambda x: json_outputparser.get_format_instructions(),
            "comment": RunnablePassthrough(),
        }
        prompt = ChatPromptTemplate.from_messages([("user", PROMPT)])

        model = ChatOpenAI(temperature=0, model="gpt-4-0125-preview")
        self.chain = context | prompt | model | json_outputparser

    def judge(self, comment: str) -> dict:
        judge_result = self.chain.invoke(comment)
        logger.info(f"Judge result: {judge_result}")
        return judge_result
