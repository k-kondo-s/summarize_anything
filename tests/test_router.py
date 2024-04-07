import pytest

from router import Dispatcher, URLExtractor


@pytest.mark.parametrize(
    "description, comment, expected_output",
    [
        ("no_url", "エラー", None),  # URL が含まれていない
        (
            "no_url_long",
            "URL の文字列も LLM に任せるのがいいな。空白をマージしてくれたり、改行を買ってに結合してくれたり。そういう「人間が意外と細かくやっているやつ」みたいなのは、まさに LLM のほうが正規表現よりも正確にやってくれる。",
            None,
        ),  # URL なしの長いコメント
        (
            "youtube",
            "https://www.youtube.com/watch?v=123456",  # 正常系
            "https://www.youtube.com/watch?v=123456",
        ),
        (
            "included_newline",
            "このプレゼン面白い\nhttps://speakerdeck.com/snoozer05/software-architecture-metrics-in-a-nutshell",  # 改行
            "https://speakerdeck.com/snoozer05/software-architecture-metrics-in-a-nutshell",
        ),
        (
            "no_space_before_url",
            "記事書いたhttps://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",  # URLの前に空白なし
            "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",
        ),
        (
            "no_space_after_url",
            "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7記事書いた",  # URLのあとに空白なし
            "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",
        ),
        (
            "query_parameter",
            "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7?v=記事書いた",  # 上と似てるけど、クエリパラメータがある
            "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7?v=記事書いた",
        ),
        (
            "space_in_url",
            "https://arxiv.o rg/abs/2202.12493",  # 空白が誤って入ってしまっている
            "https://arxiv.org/abs/2202.12493",
        ),
        (
            "newline_in_url",
            "https://arxiv.org/abs/22\n02.12493",  # 改行が誤って入ってしまっている
            "https://arxiv.org/abs/2202.12493",
        ),
    ],
)
def test_URLExtractor(description, comment, expected_output):
    """URLExtractor が期待した通りになっているか"""
    extractor = URLExtractor()
    assert extractor.extract(comment) == expected_output


@pytest.mark.parametrize(
    "url, expected_output",
    [
        ("https://www.youtube.com/watch?v=123456", "YouTube"),  # YouTube
        (
            "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",  # 一般的な Web
            "Web",
        ),
        ("https://arxiv.org/abs/2202.12493", "arXiv"),  # arXiv の論文
    ],
)
def test_Dispatcher(url, expected_output):
    """Dispatcher が期待した通りになっているか"""
    dispatcher = Dispatcher()
    assert dispatcher.dispatch(url) == expected_output
