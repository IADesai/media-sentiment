"""Test code for send_email_pdf main.py"""
from unittest.mock import MagicMock
import pytest
from main import convert_html_to_pdf

def test_ensure_html_is_string():
    """Test that checks that if the html template is not a string, an exception is raised"""
    with pytest.raises(ValueError) as not_string:
        convert_html_to_pdf(0, "fake_file")
    assert "The HTML template should be provided as a string" in str(not_string)


def test_ensure_file_name_is_string():
    """Test that checks that if the file name is not a string, an exception is raised"""
    with pytest.raises(ValueError) as not_string:
        convert_html_to_pdf("fake_html", 0)
    assert "The file name should be provided as a string" in str(not_string)