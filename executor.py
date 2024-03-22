import logging

from router import Router
from summarizer import SummarizerBuilder

logger = logging.getLogger(__name__)


class Executor:
    def __init__(self, builder: SummarizerBuilder, router: Router) -> None:
        self.builder = builder
        self.router = router

    def execute(self, comment: str) -> str | None:
        judge_result = self.router.judge(comment)
        logger.info("Judge result: %s", judge_result)

        if judge_result["summary_required"]:
            summarizer = self.builder.build_summarizer(judge_result["method"])
            summarized_text = summarizer.summarize(judge_result["url"])
            logger.info("Summarized text: %s", summarized_text)
            return summarized_text
        return None


class ExecutorBuilder:
    @staticmethod
    def build() -> Executor:
        return Executor(SummarizerBuilder(), Router())
