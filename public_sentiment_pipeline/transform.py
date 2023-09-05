"""Contains the functions required to calculate the average sentiment score from a page on Reddit."""

import statistics

from dotenv import dotenv_values
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

from extract import save_json_to_file


from extract import run_extract


def calculate_sentiment_score(text: str) -> float:
    """Calculates the (compound) sentiment score from a string."""
    vader = SentimentIntensityAnalyzer()
    sentiment_score = vader.polarity_scores(text)["compound"]

    return sentiment_score


def calculate_sentiment_statistics(comments: list[str]) -> tuple[float]:
    """Calculates the mean, median and standard deviation of the sentiment from a list of comments."""
    scores = []
    for comment in comments:
        scores.append(calculate_sentiment_score(comment))

    if len(scores) > 0:
        mean_sentiment = statistics.mean(scores)
        st_dev_sentiment = statistics.stdev(scores)
        median_sentiment = statistics.median(scores)
    else:
        mean_sentiment = None
        st_dev_sentiment = None
        median_sentiment = None
    return mean_sentiment, st_dev_sentiment, median_sentiment


def add_sentiment_to_page_dict(page_response_list: list[dict]) -> list[dict]:
    """Adds the sentiment values to the dictionary for each page."""
    for page in page_response_list:
        mean_sentiment, st_dev_sentiment, median_sentiment = calculate_sentiment_statistics(
            page["comments"])
        page["mean_sentiment"] = mean_sentiment
        page["st_dev_sentiment"] = st_dev_sentiment
        page["median_sentiment"] = median_sentiment
    return page_response_list


if __name__ == "__main__":  # pragma: no cover
    configuration = dotenv_values()

    list_of_page_dict = run_extract()

    nltk.download('vader_lexicon')

    list_of_page_dict = add_sentiment_to_page_dict(list_of_page_dict)
    print(list_of_page_dict)

    save_json_to_file(list_of_page_dict, "with_sentiment_score.json")
