"""Contains the unit tests for send_email.py.

Unit tests are designed to be run with pytest."""

from unittest.mock import patch

import pytest

from send_email import create_email_message, send_email


@patch("send_email.send_email")
def test_create_email_message(fake_create_email):
    """Checks a TypeError is raised if MIMEMultipart is not returned from create_email_message()."""
    fake_create_email.return_value = "Not an email message"
    config = {"a": "b"}

    with pytest.raises(TypeError):
        create_email_message(config, send_email())
