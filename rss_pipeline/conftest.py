"""Fixtures for testing the load script"""

import pytest


@pytest.fixture
def fake_valid_source_url():
    """Returns a fake url with a valid source"""
    return 'https://www.bbc.co.uk'


@pytest.fixture
def fake_invalid_source_url():
    """Returns a fake url with an invalid source"""
    return 'https://www.theguardian.co.uk'
