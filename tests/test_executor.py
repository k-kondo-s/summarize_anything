"""CAUTION: お金がしっかりかかるので注意。テストケースは最小限に。"""

import pytest

from executor import ExecutorBuilder


@pytest.mark.parametrize(
    "comment",
    [
        # # お金がかかるので、必要なやつだけコメントアウトする
        # "https://qiita.com/jw-automation/items/045917be7b558509fdf2",  # Qiita: RAGの実装戦略まとめ
        # "http://arxiv.org/abs/2202.12493",  # スーパーカミオカンデの論文
        # "https://www.youtube.com/watch?v=Rb7xxfRRpQY",  # あやしい集中法の動画
        # "エラー",  # 何も返してほしくないコメント
        # "https://m.youtube.com/watch?v=sal78ACtGTc",  # 中国語になってしまってたやつ
        "https://www.youtube.com/watch?v=wM5837pVh1g",  # Andrew Ng の Agentic Workflow の動画
    ],
)
def test_Excecutor(comment):
    """正常終了すること。あるいは出力を確かめたいときに使う。"""
    executor = ExecutorBuilder.build()
    print(executor.execute(comment))
