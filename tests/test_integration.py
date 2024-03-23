"""CAUTION: お金がしっかりかかるので注意。テストケースは最小限に。
"""

import pytest

from executor import ExecutorBuilder


@pytest.mark.parametrize(
    "comment",
    [
        "https://youtu.be/MdnmXc5JBjc",
    ],
)
def test_integration(comment):
    """正常終了すること"""
    executor = ExecutorBuilder.build()
    print(executor.execute(comment))
