"""Contains the unit tests for extract.py.

Unit tests are designed to be run with pytest."""

from unittest.mock import MagicMock, patch

import pytest

from conftest import FakeRequest
from extract import get_subreddit_json


@patch("requests.get")
@patch("extract.REDDIT_URL", "https://www.reddit.com/r/")
def test_non_200_raises_connection_error(fake_get):
    """Tests a ConnectionError is raised if a GET request does not return a 200 status code."""
    configuration = {"REDDIT_TOPIC": "unitedkingdom"}
    access_token = "1234567890"
    fake_request = FakeRequest()
    fake_request.status_code = 404
    fake_get.return_value = fake_request

    with pytest.raises(ConnectionError):
        get_subreddit_json(configuration, access_token)


@patch("requests.get")
@patch("extract.REDDIT_URL", "https://www.reddit.com/r/")
def test_200_status_code_returns_json(fake_get):
    """Tests JSON data is returned with a 200 status code."""
    configuration = {"REDDIT_TOPIC": "unitedkingdom"}
    access_token = "1234567890"
    fake_get.return_value = FakeRequest()

    res = get_subreddit_json(configuration, access_token)

    assert isinstance(res, dict)
