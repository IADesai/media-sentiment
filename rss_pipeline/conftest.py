"""Fixtures for testing the load script"""

import pytest
import pandas as pd


@pytest.fixture
def fake_valid_source_url():
    """Returns a fake url with a valid source"""
    return 'https://www.bbc.co.uk'


@pytest.fixture
def fake_invalid_source_url():
    """Returns a fake url with an invalid source"""
    return 'https://www.theguardian.co.uk'


@pytest.fixture
def fake_dataframe():
    """Returns a fake dataframe"""

    return pd.DataFrame([["test", 1], ["test2", 2], ["test3", 3], ["test4", 4], ["test5", 5]],
                        columns=['title', 'description', 'url', 'pubdate', 'sentiment_score'], index=[1, 2, 3, 4, 5])
