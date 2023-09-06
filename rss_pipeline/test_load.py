from unittest.mock import MagicMock, patch
import pytest

from load import *


def test_extract_source_from_url_returns_valid_source_for_bbc():
    url = "https://www.bbc.co.uk/news/uk-northern-ireland-66715623"
    assert extract_source_from_url(url) == 'bbc'


def test_extract_source_from_url_returns_valid_source_for_dailymail():
    url = "https://www.dailymail.co.uk/news/uk-northern-ireland-66715623"
    assert extract_source_from_url(url) == 'dailymail'


def test_extract_source_from_url_returns_valid_source_for_independent():
    url = "https://www.independent.co.uk/life-style/royal-family/prince-andrew-files-royal-family-b2404639.html?utm_source=reddit.com"
    assert extract_source_from_url(url) == 'independent'


def test_extract_source_from_url_returns_valid_source_for_guardian():
    url = "https://www.theguardian.com/society/2023/sep/05/birmingham-city-council-financial-distress-budget-section-114?CMP=Share_AndroidApp_Other"
    assert extract_source_from_url(url) == 'theguardian'


def test_extract_source_from_url_returns_valid_source_for_mirror():
    url = "https://www.mirror.co.uk/news/uk-news/rare-proof-copy-first-harry-30865794"
    assert extract_source_from_url(url) == 'mirror'


def test_get_source_id_returns_source_id_if_source_found(fake_valid_source_url):
    fake_connection = MagicMock()
    fake_fetch = fake_connection.cursor().__enter__().fetchone
    fake_fetch.return_value = {
        'source_id': 1}
    result = get_source_id(fake_connection, fake_valid_source_url)
    assert isinstance(result, int)
    assert result == 1


def test_get_source_id_returns_None_if_source_not_found(fake_invalid_source_url):
    fake_connection = MagicMock()
    fake_fetch = fake_connection.cursor().__enter__().fetchone
    fake_fetch.return_value = None
    result = get_source_id(fake_connection, fake_invalid_source_url)
    assert result == None


# def test_insert_articles_table_calls_appropriate_functions(fake_dataframe):
#     fake_connection = MagicMock()
#     fake_get_source_id = MagicMock()
#     fake_execute = fake_get_source_id.cursor().__enter__().execute
#     result = insert_articles_into_rds(fake_connection, fake_dataframe)
#     assert fake_execute.call_count == 1
