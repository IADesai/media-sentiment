"""Contains the unit tests for extract.py.

Unit tests are designed to be run with pytest."""

from unittest.mock import MagicMock, patch

import pytest

from conftest import FakeGet, FakePost
from extract import get_subreddit_json, get_reddit_access_token


@patch("requests.get")
@patch("extract.REDDIT_URL", "https://www.reddit.com/r/")
def test_non_200_raises_connection_error(fake_get):
    """Tests a ConnectionError is raised if a GET request does not return a 200 status code."""
    configuration = {"REDDIT_TOPIC": "unitedkingdom"}
    access_token = "1234567890"
    fake_request = FakeGet()
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
    fake_get.return_value = FakeGet()

    res = get_subreddit_json(configuration, access_token)

    assert isinstance(res, dict)


@patch("requests.post")
@patch("extract.REDDIT_ACCESS_TOKEN_URL", "https://www.reddit.com/api/v1/access_token")
def test_non_200_raises_connection_error_access_token(fake_get):
    """Tests a ConnectionError is raised if a GET request does not return a 200 status code."""
    configuration = {"REDDIT_CLIENT_SECRET": "54321",
                     "REDDIT_SECRET_KEY": "12345",
                     "REDDIT_USERNAME": "12345_54321",
                     "REDDIT_PASSWORD": "54321_12345"}
    fake_request = FakePost()
    fake_request.status_code = 403
    fake_get.return_value = fake_request

    with pytest.raises(ConnectionError):
        get_reddit_access_token(configuration)


@patch("requests.post")
@patch("extract.REDDIT_ACCESS_TOKEN_URL", "https://www.reddit.com/api/v1/access_token")
def test_200_status_code_returns_string_access_token(fake_get):
    """Tests access token string is returned with a 200 status code."""
    configuration = {"REDDIT_CLIENT_SECRET": "54321",
                     "REDDIT_SECRET_KEY": "12345",
                     "REDDIT_USERNAME": "12345_54321",
                     "REDDIT_PASSWORD": "54321_12345"}
    fake_get.return_value = FakePost()

    res = get_reddit_access_token(configuration)

    assert isinstance(res, str)
