# RSS (Media Sentiment) Pipeline

## What it does

This pipeline extracts information from the news site's RSS feeds and cleans the data by removing unnecessary information
such as headline tags and converting data types. The full article is then web scraped using the URLs provided in the RSS feed
and sentiment analysis is performed on this using NLTK's VADER model with the compound score calculated. All of this
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

- `ACCESS_KEY_ID`
- `SECRET_ACCESS_KEY`
- `DATABASE_NAME`
- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_IP`
- `DATABASE_PORT`

## Running the pipeline

Execute the media sentiment pipeline by running:

```sh
python3 deploy_pipeline.py
```

## Docker image

Building a Docker image for AWS Lambda.

```sh
docker build -t media-sentiment-pipeline . --platform "linux/amd64"
```

Run the Docker image.

```sh
docker run -t --env-file .env media-sentiment-pipeline
```
