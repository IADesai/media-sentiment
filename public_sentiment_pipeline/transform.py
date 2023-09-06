"""Contains the functions required to calculate the average sentiment score from a page on Reddit."""

import statistics
import time

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from extract import run_extract, save_json_to_file

REDDIT_COMMENTS = "comments"
REDDIT_SENTIMENT_MEAN = "mean_sentiment"
REDDIT_SENTIMENT_ST_DEV = "st_dev_sentiment"
REDDIT_SENTIMENT_MEDIAN = "median_sentiment"


def calculate_sentiment_score(text: str) -> float:
    """Calculates the (compound) sentiment score from a string."""
    vader = SentimentIntensityAnalyzer()
    sentiment_score = vader.polarity_scores(text)["compound"]

    return sentiment_score


def calculate_sentiment_for_each_comment(comments: list[str]) -> list[float]:
    """Returns a list with the sentiment score for each comment."""
    scores = []
    for comment in comments:
        scores.append(calculate_sentiment_score(comment))
    return scores


def calculate_sentiment_statistics(comments: list[str]) -> tuple[float]:
    """Calculates the mean, median and standard deviation of the sentiment from a list of comments."""
    scores = calculate_sentiment_for_each_comment(comments)
    if len(scores) > 0:
        mean_sentiment = statistics.mean(scores)
        st_dev_sentiment = statistics.pstdev(scores)
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
            page[REDDIT_COMMENTS])
        page[REDDIT_SENTIMENT_MEAN] = mean_sentiment
        page[REDDIT_SENTIMENT_ST_DEV] = st_dev_sentiment
        page[REDDIT_SENTIMENT_MEDIAN] = median_sentiment
    return page_response_list


def run_transform() -> list[dict]:  # pragma: no cover
    """Returns a list of dictionaries for each Reddit page with sentiment scores."""
    start = time.time()
    list_of_page_dict = run_extract()
    print(f"Time to run extract: {(time.time()-start):.2f} seconds.")
    start = time.time()
    nltk.download('vader_lexicon')
    list_of_page_dict = add_sentiment_to_page_dict(list_of_page_dict)
    print(f"Time to run transform: {(time.time()-start):.2f} seconds.")
    return list_of_page_dict


if __name__ == "__main__":  # pragma: no cover
    nltk.download('vader_lexicon')

    list_of_page_dict = run_extract()

    list_of_page_dict = add_sentiment_to_page_dict(list_of_page_dict)
    print(list_of_page_dict)

    save_json_to_file(list_of_page_dict, "with_sentiment_score.json")
