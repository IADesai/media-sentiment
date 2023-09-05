"""Contains the functions required to calculate the average sentiment score from a page on Reddit."""

import statistics

from dotenv import dotenv_values
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize


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


if __name__ == "__main__":  # pragma: no cover
    configuration = dotenv_values()

    list_of_page_dict = run_extract()

    nltk.download('vader_lexicon')
