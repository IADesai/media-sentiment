# PDF Visualisation Reports

## What it does

This pipeline reads in information that has been loaded on the remote database and extracts relevant information relating to the last 24 hours. A PDF containing charts and information blocks is then created and formatted in a way in which resembles a newsletter. This PDF file is then sent as an attachment within the email using the AWS email service and also uploaded to an S3 bucket for archiving purposes.

## Required environment variables

The following environment variables must be supplied in a `.env` file.

- `DATABASE_USERNAME`
- `DATABASE_PASSWORD`
- `DATABASE_IP`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `ACCESS_KEY`
- `SECRET_KEY`
- `BUCKET_NAME`
- `EMAIL_SENDER`
- `EMAIL_RECIPIENT`

## Docker image

Build a Docker image.

```sh
docker build -t media-sentiment-email-ecr . --platform "linux/amd64"
```

Run the Docker image.

```sh
docker run --env-file .env -p 9000:8080 media-sentiment-email-ecr
```
