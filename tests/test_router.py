from router import Router


def test_judge():
    router = Router()

    # Test case 1: Comment without URL
    comment = "This is a test comment"
    expected_output = {"summary_required": False, "url": "", "method": "None"}
    assert router.judge(comment) == expected_output

    # Test case 2: Comment with YouTube URL
    comment = "Check out this video: https://www.youtube.com/watch?v=123456"
    expected_output = {"summary_required": True, "url": "https://www.youtube.com/watch?v=123456", "method": "YouTube"}
    assert router.judge(comment) == expected_output

    # Test case 3: Comment with Speaker Deck URL
    comment = "Here's a presentation: https://speakerdeck.com/snoozer05/software-architecture-metrics-in-a-nutshell"
    expected_output = {
        "summary_required": True,
        "url": "https://speakerdeck.com/snoozer05/software-architecture-metrics-in-a-nutshell",
        "method": "Web",
    }
    assert router.judge(comment) == expected_output

    # Test case 4: Comment with Qiita URL
    comment = "I wrote an article: https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7"
    expected_output = {
        "summary_required": True,
        "url": "https://qiita.com/kenji-kondo/items/91ae417ad858ec4652e7",
        "method": "Web",
    }
    assert router.judge(comment) == expected_output
