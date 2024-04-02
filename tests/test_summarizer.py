import pytest

from summarizer import HTTPClient, TextSummarizer, WebSummarizer, YouTubeSummarizer
from tests.data import long_long_text


@pytest.mark.parametrize(
    ("url", "expected_included_str"),
    [
        (
            "https://sakana.ai/evolutionary-model-merge-jp/",
            "進化的モデルマージという手法",
        ),
        (
            "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",
            "この推論は原点を中心とした回転の操作に対して同様に成立する",
        ),
        (
            # arXiv の HTML5 バージョンにちゃんとアクセスできるか
            "https://ar5iv.org/abs/2202.12493",
            "I am grateful to Teresa Montaruli",
        ),
        (
            # これは Javascript で動的に生成されるサイトなので、普通の requests では取得できない
            "https://towardsdatascience.com/the-math-behind-neural-networks-a34a51b93873",
            "LeCun, Yann, Yoshua Bengio, and Geoffrey Hinton",
        ),
        # (
        #     # これはまだ成功しない: Twitter の URL
        #     "https://x.com/kondokenjibai/status/1774132215703830577?s=20",
        #     "記事を投稿しました! #けんじのブログ",
        # ),
        # (
        #     # これはまだ成功しない: "Just a moment...Enable JavaScript and cookies to continue" となる
        #     "https://www.axios.com/2024/03/27/ai-chatbot-letdown-hype-reality",
        #     "This isn't the end of the road for generative AI",
        # ),
    ],
)
def test_request_get(url, expected_included_str):
    # Arrange
    http_client = HTTPClient()

    # Act
    result = http_client.get(url)
    print(result)

    # Assert: expected_included_str が含まれているか
    assert expected_included_str in result


def test_arxiv_summarizer():
    """ArXivSummarizer の summarize が正常終了するか"""
    # Arrange
    summarizer = WebSummarizer(TextSummarizer(), HTTPClient())

    # Act
    result = summarizer.summarize("https://arxiv.org/abs/2202.12493")
    print(result)

    # Assert
    assert len(result) > 0


def test_youtube_summarizer():
    """YouTubeSummarizer の summarize が正常終了するか"""
    # Arrange
    summarizer = YouTubeSummarizer(TextSummarizer())

    # Act
    result = summarizer.summarize("https://www.youtube.com/watch?v=Rb7xxfRRpQY")
    print(result)

    # Assert
    assert len(result) > 0


def test_summarize_at_the_end():
    """最後まで途切れないか"""
    # Arrange
    summarizer = TextSummarizer()

    # Act
    result = summarizer.summarize(long_long_text)

    # Assert。とりあえず今は 1024 であるかどうか。
    # ここは LLM を用いて「文章が途中で切れてないか」を確かめさせるのがいいだろうな。
    assert len(result) > 1024
