import pytest

from summarizer import TextSummarizer, WebSummarizer


@pytest.mark.parametrize(
    ("url"),
    [
        "https://sakana.ai/evolutionary-model-merge-jp/",
        "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",
    ],
)
def test_request_get(url):
    # Arrange
    summarizer = WebSummarizer(TextSummarizer())

    # Act
    result = summarizer._reqest_get(url)

    # Assert
    assert len(result) > 0


def test_arxiv_summarizer():
    """ArXivSummarizer の summarize が正常終了するか"""
    # Arrange
    summarizer = WebSummarizer(TextSummarizer())

    # Act
    result = summarizer.summarize("https://arxiv.org/abs/2202.12493")
    print(result)

    # Assert
    assert len(result) > 0
