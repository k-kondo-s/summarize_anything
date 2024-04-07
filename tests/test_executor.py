"""CAUTION: お金がしっかりかかるので注意。テストケースは最小限に。"""

import pytest

from executor import ExecutorBuilder


@pytest.mark.parametrize(
    "comment",
    [
        # # お金がかかるので、必要なやつだけコメントアウトする
        # "https://youtu.be/MdnmXc5JBjc",
        # "https://t.co/xjHmAohfqg"
        # "https://www.technologyreview.com/2024/03/04/1089403/large-language-models-amazing-but-nobody-knows-why/"
        # "https://qiita.com/jw-automation/items/045917be7b558509fdf2"  # Qiita: RAGの実装戦略まとめ
        # "https://t.co/EAnnqjBjJG",
        # "http://arxiv.org/abs/2202.12493",  # スーパーカミオカンデの論文
        # "https://www.youtube.com/watch?v=Rb7xxfRRpQY",
        "エラー"
    ],
)
def test_Excecutor(comment):
    """正常終了すること。あるいは出力を確かめたいときに使う。"""
    executor = ExecutorBuilder.build()
    print(executor.execute(comment))
