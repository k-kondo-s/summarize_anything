import pytest

from router import Router


@pytest.mark.parametrize(
    "comment, expected_output",
    [
        (
            "This is a test comment",
            {"summary_required": False, "url": "", "method": "None"},
        ),
        (
            "Check out this video: https://www.youtube.com/watch?v=123456",
            {
                "summary_required": True,
                "url": "https://www.youtube.com/watch?v=123456",
                "method": "YouTube",
            },
        ),
        (
            "Here's a presentation: https://speakerdeck.com/snoozer05/software-architecture-metrics-in-a-nutshell",
            {
                "summary_required": True,
                "url": "https://speakerdeck.com/snoozer05/software-architecture-metrics-in-a-nutshell",
                "method": "Web",
            },
        ),
        (
            "I wrote an article: https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",
            {
                "summary_required": True,
                "url": "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",
                "method": "Web",
            },
        ),
        (
            "This is a good paper: https://arxiv.org/abs/2202.12493",
            {
                "summary_required": True,
                "url": "https://arxiv.org/abs/2202.12493",
                "method": "arXiv",
            },
        ),
    ],
)
def test_judge(comment, expected_output):
    """Routing が期待した通りになっているか"""
    router = Router()
    assert router.judge(comment) == expected_output
