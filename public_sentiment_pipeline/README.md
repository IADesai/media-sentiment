# Public Sentiment Pipeline

## What it does

This pipeline extracts information from a subreddit using the Reddit API and extracts all the comments across a defined range of pages. The comments
are then cleaned by removing markdown formatting and also comments that have been removed by Reddit themselves, this was primarily done using RegEx.
Sentiment analysis is performed on this using NLTK's VADER model with the compound score calculated. All of this
information is then loaded onto the remote database.

## Configure development environment

Create a Python [virtual environment](https://docs.python.org/3/library/venv.html) and install necessary packages:

```sh
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

## Required environment variables

The following environment variables must be supplied in a .env file in order to run the code in this directory.

- `REDDIT_TOPIC`
- `REDDIT_JSON_BUCKET_NAME`
- `ACCESS_KEY`
- `SECRET_KEY`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_SECRET_KEY`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`
- `DATABASE_NAME`
- `DATABASE_USERNAME`
- `DATABASE_IP`
- `DATABASE_PASSWORD`

## Running the pipeline

Execute the public sentiment pipeline by running:

```sh
python3 load.py
```

## Archiving

JSON files fetched from Reddit for each page are archived in an S3 bucket. They are named after the time they are created followed by the title.

## Design decisions

The pipeline processes 40 pages from a selected subreddit. The subreddit is chosen using the environment variable `REDDIT_TOPIC`. The number of pages to process is controlled from the global variable `MAX_REDDIT_PAGES` in `extract.py`. From each page 500 comments are processed. This value is set by the global variable `MAX_REDDIT_COMMENTS` in `extract.py`.

Formatting in comments that cannot be recognised by Vader is removed. `£`, `'`, `"` and `&` are kept in the comments. Other characters such as new lines or hyphens are removed. Markdown formatting such as web links are also removed, however, the text for the link is retained. Additionally, comments that do not contain the original intended text, such as `"**Removed/warning**"`, are removed entirely. This influences the parameter `included_comment_count`.

For a Reddit page to be added to the database the number of processed comments must be greater than or equal to 5. This is set by `MIN_PROCESSED_COMMENTS` in `extract.py`. This minimum is set to ensure that readings taken from the database produce a representative sample, and that stories with few comments do not sway the findings made from the data interpretation.

## Docker image

Build a Docker image.

```sh
docker build -t reddit-pipeline . --platform "linux/amd64"
```

Run the Docker image.

```sh
docker run -t --env-file .env reddit-pipeline
```
