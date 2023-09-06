import requests
from bs4 import BeautifulSoup
import requests
import pandas as pd


def get_daily_mail_full_article_text(url: str):
    response = requests.get(url)

    html = BeautifulSoup(response.text, 'html.parser')

    # Find the tag with the article body
    article_body = html.find('div', itemprop='articleBody')

    if article_body:
        article_content = article_body.get_text()
        return article_content
    return None


def get_bbc_full_article_text(url: str):
    html = requests.get(url)
    bsobj = BeautifulSoup(html.content, "lxml")

    bbc_jargon = ["This video can not be played"]

    article_contents_list = []
    for link in bsobj.find_all("p"):
        if "Paragraph" in str(link):
            article_contents_list.append(link.get_text())

    for element in bbc_jargon:
        while element in article_contents_list:
            article_contents_list.remove(element)

    if len(article_contents_list) >= 4:
        article_contents_list = article_contents_list[:-4]
    return " ".join(article_contents_list)


if __name__ == "__main__":
    bbc_df = pd.read_csv("bbc_uk_news.csv")
    bbc_urls_list = bbc_df['url'].values.tolist()

    bbc_df['url_text'] = bbc_df['url'].apply(get_bbc_full_article_text)

    bbc_df.to_csv("BBCTESTINGURLS.csv")
