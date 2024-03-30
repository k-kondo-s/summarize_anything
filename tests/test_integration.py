"""CAUTION: お金がしっかりかかるので注意。テストケースは最小限に。"""

import pytest

from executor import ExecutorBuilder


@pytest.mark.parametrize(
    "comment",
    [
        # "https://youtu.be/MdnmXc5JBjc",
        # "https://t.co/xjHmAohfqg"
        # "https://www.technologyreview.com/2024/03/04/1089403/large-language-models-amazing-but-nobody-knows-why/"
        # "https://qiita.com/jw-automation/items/045917be7b558509fdf2"
        # "https://t.co/EAnnqjBjJG",
        # "https://t.co/YCQdN1m961",
        "https://www.youtube.com/watch?v=Rb7xxfRRpQY"
    ],
)
def test_integration(comment):
    """正常終了すること"""
    executor = ExecutorBuilder.build()
    print(executor.execute(comment))
