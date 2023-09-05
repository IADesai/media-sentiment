"""Contains the unit tests for transform.py.

Unit tests are designed to be run with pytest."""

from transform import calculate_sentiment_score


def test_sentiment_score_returns_float():
    """Tests a float is returned from calculate_sentiment_score()."""
    comment = "Hello, World!"

    res = calculate_sentiment_score(comment)

    assert isinstance(res, float)


def test_sentiment_score_empty_string():
    """Tests a value of 0 is returned for an empty string in calculate_sentiment_score()."""
    comment = ""

    res = calculate_sentiment_score(comment)

    assert res == 0
