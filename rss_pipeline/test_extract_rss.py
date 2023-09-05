from unittest.mock import patch, mock_open
from extract_rss import download_bbc_uk_news_xml, download_daily_mail_uk_news_xml


@patch("builtins.open", new_callable=mock_open, create=True)
def test_download_bbc_uk_news_xml(mock_file_open):

    with patch("requests.get") as mock_get:
        fake_response = mock_get.return_value
        fake_response.status_code = 200
        fake_response.content = b"Fake XML Content"

        download_bbc_uk_news_xml()

        mock_get.assert_called_once_with(
            "http://feeds.bbci.co.uk/news/uk/rss.xml", timeout=10)
        mock_file_open.assert_called_once_with("bbc_uk_news.xml", "wb")
        mock_file_open().write.assert_called_once_with(b"Fake XML Content")


@patch("builtins.open", new_callable=mock_open, create=True)
def test_download_daily_mail_uk_news_xml(mock_file_open):

    with patch("requests.get") as mock_get:
        fake_response = mock_get.return_value
        fake_response.status_code = 200
        fake_response.content = b"Fake XML Content"

        download_daily_mail_uk_news_xml()

        mock_get.assert_called_once_with(
            "https://www.dailymail.co.uk/home/index.rss", timeout=10)
        mock_file_open.assert_called_once_with("daily_mail_uk_news.xml", "wb")
        mock_file_open().write.assert_called_once_with(b"Fake XML Content")
