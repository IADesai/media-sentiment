import unittest
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
from unittest.mock import mock_open, patch
from transform_rss import (
    extract_info_from_bbc_articles,
    extract_info_from_daily_mail_articles,
    convert_pubdate_to_timestamp,
    remove_headline_tags,
    get_sentiment_score,
)


def test_extract_info_from_bbc_articles():
    xml_data = """
        <root>
            <item>
                <title>Test Article</title>
                <description> Test Description</description>
                <guid>URL</guid>
                <pubDate>Tue, 05 Sep 2023 12:00:00 UTC</pubDate>
            </item>
            <item>
                <title>Another Article</title>
                <description>Test Description 2</description>
                <guid>URL</guid>
                <pubDate>Mon, 04 Sep 2023 12:00:00 UTC</pubDate>
            </item>
        </root>
    """

    mock_file = mock_open(read_data=xml_data)

    with patch('builtins.open', mock_file):
        df = extract_info_from_bbc_articles('mock_news.xml')

    assert isinstance(df, pd.DataFrame)
    assert "title" in df.columns
    assert "description" in df.columns
    assert "url" in df.columns
    assert "pubdate" in df.columns


def test_extract_info_from_daily_mail_articles():
    xml_data = """
        <root>
            <item>
                <title>Test Article</title>
                <description> Test Description</description>
                <guid>URL</guid>
                <pubDate>Tue, 05 Sep 2023 12:00:00 UTC</pubDate>
            </item>
            <item>
                <title>Another Article</title>
                <description>Test Description 2</description>
                <guid>URL</guid>
                <pubDate>Mon, 04 Sep 2023 12:00:00 UTC</pubDate>
            </item>
        </root>
    """

    mock_file = mock_open(read_data=xml_data)

    with patch('builtins.open', mock_file):
        df = extract_info_from_daily_mail_articles('mock_news.xml')

    assert isinstance(df, pd.DataFrame)
    assert "title" in df.columns
    assert "description" in df.columns
    assert "url" in df.columns
    assert "pubdate" in df.columns


def test_convert_pubdate_to_timestamp():
    pubdate = "Tue, 05 Sep 2023 12:00:00 UTC"
    timestamp = convert_pubdate_to_timestamp(pubdate)
    assert isinstance(timestamp, datetime)


def test_remove_headline_tags():
    headline = "BREAKING Twitter is renamed to X"
    cleaned_headline = remove_headline_tags(headline)
    assert cleaned_headline == "Twitter is renamed to X"


def test_remove_headline_tags_different_case():
    headline = "breaking Twitter is renamed to X"
    cleaned_headline = remove_headline_tags(headline)
    assert cleaned_headline == "Twitter is renamed to X"


def test_get_sentiment_score():
    text = "I am happy, joyful, excited."
    score = get_sentiment_score(text)
    assert isinstance(score, float)
