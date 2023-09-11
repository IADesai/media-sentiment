"""Contains the unit tests for main.py.

Unit tests are designed to be run with pytest."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from main import convert_html_to_pdf, create_email_message, send_email


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
