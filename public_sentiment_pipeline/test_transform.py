"""Contains the unit tests for transform.py.

Unit tests are designed to be run with pytest."""

from unittest.mock import patch

import pytest
import nltk

from reddit_conftest import fake_page_response_list
from transform import calculate_sentiment_score, calculate_sentiment_for_each_comment, calculate_sentiment_statistics, add_sentiment_to_page_dict


@pytest.fixture(scope="session", autouse=True)
def download_nltk():
    """Download the required library before running the unit tests."""
    nltk.download("vader_lexicon")


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


def test_list_returned_for_sentiment_values():
    """Checks a list is returned from calculate_sentiment_for_each_comment()."""
    comments = ["a", "b", "c"]

    res = calculate_sentiment_for_each_comment(comments)

    assert isinstance(res, list)
    assert len(res) == 3
    assert isinstance(res[0], float)
    assert isinstance(res[1], float)
    assert isinstance(res[2], float)


@pytest.mark.parametrize("fake_scores,mean,stdev,median",
                         [([1, 1, 1], 1, 0, 1),
                          ([-1, 0, 1], 0, 0.8164965, 0),
                          ([-1, -1, 0], -2/3, 0.4714045, -1),
                          ([0.5], 0.5, 0, 0.5),
                          ([], None, None, None)])
@patch("transform.calculate_sentiment_for_each_comment")
def test_sentiment_statistics_calculated_correctly(fake_calculate, fake_scores, mean, stdev, median):
    """Checks the sentiment statistics are calculated correctly."""
    fake_calculate.return_value = fake_scores

    res_mean, res_stdev, res_median = calculate_sentiment_statistics([
                                                                     "a", "b", "c"])

    assert res_mean == pytest.approx(mean)
    assert res_stdev == pytest.approx(stdev)
    assert res_median == pytest.approx(median)


@patch("transform.calculate_sentiment_statistics")
def test_sentiment_scores_added_to_dictionary(fake_statistics, fake_page_response_list):
    """Checks the sentiment scores are added to the page dictionary."""
    fake_statistics.return_value = (1, 0, 1)

    res = add_sentiment_to_page_dict(fake_page_response_list)

    assert isinstance(res, list)
    assert res == [{"title": "a", "subreddit_url": "b", "article_url": "c", "article_domain": "d", "comments": ["a", "b"], "mean_sentiment": 1, "st_dev_sentiment": 0, "median_sentiment": 1}, {
        "title": "e", "subreddit_url": "f", "article_url": "g", "article_domain": "h", "comments": ["c", "d"], "mean_sentiment": 1, "st_dev_sentiment": 0, "median_sentiment": 1}]
