import logging

from router import Dispatcher, URLExtractor
from summarizer import SummarizerBuilder, TextSummarizer

logger = logging.getLogger(__name__)


class Executor:
    def __init__(
        self,
        builder: SummarizerBuilder,
        url_extractor: URLExtractor,
        dispatcher: Dispatcher,
    ) -> None:
        self.builder = builder
        self.url_extractor = url_extractor
        self.dispatcher = dispatcher

    def execute(self, comment: str) -> str | None:
        extracted_url = self.url_extractor.extract(comment)
        if extracted_url is None:
            logger.info("No URL extracted")
            return None

        category = self.dispatcher.dispatch(extracted_url)
        logger.info(f"Category: {category}")

        summarizer = self.builder.build_summarizer(category)
        summarized_text = summarizer.summarize(extracted_url)
        logger.info(f"Summarized text: {summarized_text}")
        return summarized_text


class SimpleExecutor:
    def __init__(self, summerizer: TextSummarizer) -> None:
        self.summerizer = summerizer

    def execute(self, text: str) -> str:
        return self.summerizer.summarize(text)


class ExecutorBuilder:
    @staticmethod
    def build() -> Executor:
        return Executor(SummarizerBuilder(), URLExtractor(), Dispatcher())

    @staticmethod
    def build_simple() -> SimpleExecutor:
        return SimpleExecutor(TextSummarizer())
