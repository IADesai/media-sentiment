# Public Sentiment Pipeline

## Configure development environment

Create a Python virtual environment and install necessary packages.

```sh
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

## Run the code

Run the extract script.

```sh
python3 extract.py
```

## Required environment variables

The following environment variables must be supplied in a .env file in order to run the code in this directory.

- `REDDIT_TOPIC`
