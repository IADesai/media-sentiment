"""Contains the unit tests for extract.py.

Unit tests are designed to be run with pytest."""

from unittest.mock import MagicMock, patch
from re import match

import pytest

from conftest import FakeGet, FakePost
from extract import get_subreddit_json, get_reddit_access_token, create_pages_list, create_json_filename, get_json_from_request, get_comments_list, process_each_reddit_page


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


def test_pages_list_returns_correct_type(fake_subreddit_json):
    """Tests a list of dictionaries is returned by create_pages_list()."""
    res = create_pages_list(fake_subreddit_json)

    assert isinstance(res, list)
    assert isinstance(res[0], dict)


def test_pages_list_skips_missing_data(fake_subreddit_json_missing_entries):
    """Tests entries missing keys are not returned by create_pages_list()."""
    res = create_pages_list(fake_subreddit_json_missing_entries)

    assert len(res) == 2


@pytest.mark.parametrize("reddit_title,expected_title_end",
                         [("ValidTitle", "ValidTitle"),
                          ("Replace Space", "Replace_Space"),
                          (" Replace All Spaces ", "_Replace_All_Spaces_"),
                          ("-Remove-Hyphen-", "_Remove_Hyphen_"),
                          ("\"Remove\"Quotation\"", "_Remove_Quotation_"),
                          ("Remove.FullStop", "Remove_FullStop"),
                          ("Remove,Comma", "Remove_Comma"),
                          (" m\"ulti.ple  inva,l-id", "_m_ulti_ple__inva_l_id"),
                          ("ThisTitleIsFarTooLongAndWillBeReducedInLength", "ThisTitleIsFarTooLongAndWillBe")])
def test_json_filename_title_formatting(reddit_title, expected_title_end):
    """Tests the filename is correctly formatted by removing invalid characters."""
    res = create_json_filename(reddit_title)

    assert res.endswith(expected_title_end + ".json")


def test_file_date_format_correct():
    """Tests the date is correctly formatted when creating the JSON filename."""
    reddit_title = ""

    res = create_json_filename(reddit_title)

    assert match(r"\d{4}_\d{2}_\d{2}-\d{2}_\d{2}-\.json", res)


@patch("requests.get")
def test_json_returned_from_successful_request(fake_get):
    subreddit_url = "www.reddit.com"
    reddit_access_token = "12345"
    fake_get.return_value = FakeGet()

    res = get_json_from_request(subreddit_url, reddit_access_token)

    assert isinstance(res, dict)


@patch("requests.get")
def test_connection_error_raised_successful_request(fake_get):
    """Tests a Connection error is raised if a non-200 status code is returned."""
    subreddit_url = "www.reddit.com"
    reddit_access_token = "12345"
    fake_request = FakeGet()
    fake_request.status_code = 500
    fake_get.return_value = fake_request

    with pytest.raises(ConnectionError):
        get_json_from_request(subreddit_url, reddit_access_token)


@patch("extract.read_json_as_text")
def test_list_of_comments_returned(fake_read_json, fake_json_content_1):
    """Tests a list of comment strings is returned by get_comments_list()."""
    fake_read_json.return_value = fake_json_content_1
    res = get_comments_list("file.json")

    assert isinstance(res, list)
    assert isinstance(res[0], str)


@patch("extract.read_json_as_text")
def test_only_comments_extracted_from_json(fake_read_json, fake_json_content_1):
    """Tests only comment lines are extracted from the JSON."""
    fake_read_json.return_value = fake_json_content_1
    res = get_comments_list("file.json")

    assert len(res) == 2
    assert res == ["This is the first comment.", "This is the second comment."]


@patch("extract.read_json_as_text")
def test_comment_lines_removed(fake_read_json, fake_json_content_2):
    """Tests invalid comment lines are not returned."""
    fake_read_json.return_value = fake_json_content_2
    res = get_comments_list("file.json")

    assert len(res) == 2
    assert res == ["This is the third comment.", "This is the fourth comment."]
