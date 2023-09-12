"""Contains the unit tests for main.py.

Unit tests are designed to be run with pytest."""

from unittest.mock import patch

import pytest

from main import convert_html_to_pdf, create_email_message, send_email, choose_line_color, get_titles


def test_ensure_html_is_string():
    """Test that checks that if the html template is not a string, an exception is raised"""
    with pytest.raises(ValueError) as not_string:
        convert_html_to_pdf(0)
    assert "The HTML template should be provided as a string" in str(
        not_string)


@patch("main.send_email")
def test_create_email_message(fake_create_email):
    """Checks a TypeError is raised if MIMEMultipart is not returned from create_email_message()."""
    fake_create_email.return_value = "Not an email message"

    with pytest.raises(TypeError):
        create_email_message(send_email())


def test_gauge_colour_returns_str():
    """Checks that a string is returned from choose_line_color()."""
    score = 0.5

    res = choose_line_color(score)

    assert isinstance(res, str)


@patch("main.GREEN", "green")
@patch("main.RED", "red")
@pytest.mark.parametrize("score,colour",
                         [(0, "green"),
                          (0.2, "green"),
                          (1, "green"),
                          (-0.2, "red"),
                          (-1, "red")])
def test_check_correct_gauge_colour_returned(score, colour):
    """Tests the correct colour is returned according to the sentiment score."""
    res = choose_line_color(score)

    assert res == colour


def test_get_titles_returns_string():
    """Checks get_titles() returns a string."""
    titles = ["First", "Second", "Third"]

    res = get_titles(titles)

    assert isinstance(res, str)


def test_correct_html_string_returned_for_get_titles():
    """Checks the correct string is returned for a set of titles."""
    titles = ["First Title", "Second title."]

    res = get_titles(titles)

    assert res == "<ul>" + \
        "<li>First Title</li>" + \
        "<li>Second title.</li>" + \
        "</ul>"
