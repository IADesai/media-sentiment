"""Contains the unit tests for extract.py.

Unit tests are designed to be run with pytest."""

# pylint: skip-file

from unittest.mock import MagicMock, patch
from re import match

import pytest

from reddit_conftest import FakeGet, FakePost, fake_subreddit_json, fake_subreddit_json_missing_entries, fake_json_content_1, fake_json_content_2
from extract import get_subreddit_json, get_reddit_access_token, create_pages_list, create_json_filename, get_json_from_request, get_comments_list, process_each_reddit_page, remove_unrecognised_formatting


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


@patch("extract.create_json_filename")
@patch("extract.get_json_from_request")
@patch("extract.save_json_to_file")
@patch("extract.upload_json_s3")
@patch("extract.get_comments_list")
def test_correct_calls_made_by_process_reddit_page(fake_comments_list, fake_upload, fake_save, fake_get_json, fake_create_filename):
    """Tests the correct function calls are made by process_each_reddit_page()."""
    pages_list = [{"title": "a", "subreddit_url": "r/a"}, {"title": "b",
                                                           "subreddit_url": "r/b"}, {"title": "c", "subreddit_url": "r/c"}]
    reddit_access_token = "12345"
    configuration = {"REDDIT_CLIENT_SECRET": "54321",
                     "REDDIT_SECRET_KEY": "12345",
                     "REDDIT_USERNAME": "12345_54321",
                     "REDDIT_PASSWORD": "54321_12345"}

    res = process_each_reddit_page(
        pages_list, reddit_access_token, configuration)

    assert fake_comments_list.call_count == 3
    assert fake_upload.call_count == 3
    assert fake_save.call_count == 3
    assert fake_get_json.call_count == 3
    assert fake_create_filename.call_count == 3


@patch("extract.create_json_filename")
@patch("extract.get_json_from_request")
@patch("extract.save_json_to_file")
@patch("extract.upload_json_s3")
@patch("extract.get_comments_list")
def test_list_returned_by_process_reddit_page(fake_comments_list, fake_upload, fake_save, fake_get_json, fake_create_filename):
    """Tests a list is returned by process_each_reddit_page()."""
    pages_list = [{"title": "a", "subreddit_url": "r/a"}, {"title": "b",
                                                           "subreddit_url": "r/b"}, {"title": "c", "subreddit_url": "r/c"}]
    reddit_access_token = "12345"
    configuration = {"REDDIT_CLIENT_SECRET": "54321",
                     "REDDIT_SECRET_KEY": "12345",
                     "REDDIT_USERNAME": "12345_54321",
                     "REDDIT_PASSWORD": "54321_12345"}

    fake_comments_list.return_value = ["Comment 1", "Comment 2"]

    res = process_each_reddit_page(
        pages_list, reddit_access_token, configuration)

    assert isinstance(res, list)
    assert res == [{"title": "a", "subreddit_url": "r/a", "comments": ["Comment 1", "Comment 2"], "included_comment_count": 2}, {"title": "b",
                                                                                                                                 "subreddit_url": "r/b", "comments": ["Comment 1", "Comment 2"], "included_comment_count": 2}, {"title": "c", "subreddit_url": "r/c", "comments": ["Comment 1", "Comment 2"], "included_comment_count": 2}]


@patch("extract.create_json_filename")
@patch("extract.get_json_from_request")
@patch("extract.save_json_to_file")
@patch("extract.upload_json_s3")
@patch("extract.get_comments_list")
def test_no_list_returned_if_exception_by_process_reddit_page(fake_comments_list, fake_upload, fake_save, fake_get_json, fake_create_filename):
    """Tests no list is returned if exceptions are raised during process_each_reddit_page()."""
    pages_list = [{"title": "a", "subreddit_url": "r/a"}, {"title": "b",
                                                           "subreddit_url": "r/b"}, {"title": "c", "subreddit_url": "r/c"}]
    reddit_access_token = "12345"
    configuration = {"REDDIT_CLIENT_SECRET": "54321",
                     "REDDIT_SECRET_KEY": "12345",
                     "REDDIT_USERNAME": "12345_54321",
                     "REDDIT_PASSWORD": "54321_12345"}

    fake_comments_list.return_value = ["Comment 1", "Comment 2"]
    fake_get_json.side_effect = ConnectionError()

    res = process_each_reddit_page(
        pages_list, reddit_access_token, configuration)

    assert isinstance(res, list)
    assert res == []


@pytest.mark.parametrize("comment,cleaned_comment",
                         [("\\n This contains single new lines \\n .", " This contains single new lines  ."),
                          ("\\\n This contains double new lines \\\n .",
                           " This contains double new lines  ."),
                          ("&gt;comment&gt;", "comment"),
                          ("\\\n&gt;", ""),
                          ("wasn\\u2019t", "wasnt"),
                          ("\\u2019,\\u2019", ","),
                          ("&amp;", "&"),
                          ("h&amp;s", "h&s"),
                          ("#x200B;", ""),
                          ("this#x200B; is#x200B; a#x200B; comment",
                           "this is a comment"),
                          ("They start just under \\u00a38k, most people can afford that. \\n\\n[Citroen Ami \\u2013 from \\u00a37,695](https://parkers-images.bauersecure.com/pagefiles/308460/citroen_ami_001.jpg)",
                           "They start just under 38k, most people can afford that. Citroen Ami from 37,695"),
                          ("[Text](link)", "Text")])
def test_formatting_removed_from_comments(comment, cleaned_comment):
    """Tests formatting is removed from comments."""
    res = remove_unrecognised_formatting(comment)

    assert res == cleaned_comment
