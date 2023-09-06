# Public Sentiment Pipeline

## Configure development environment

Create a Python virtual environment and install necessary packages.

```sh
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

## Run the code

Run the pipeline script.

```sh
python3 load.py
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

## Archiving

JSON files fetched from Reddit for each page are archived in an S3 bucket. They are named after the time they are created followed by the title.

## Docker image

Build a Docker image.

```sh
docker build -t reddit-pipeline . --platform "linux/amd64"
```

Run the Docker image.

```sh
docker run -t --env-file .env reddit-pipeline
```
