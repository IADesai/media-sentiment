# PDF Visualisation Reports

The code in this directory creates a PDF containing charts using the most recent data. These are sent as attachments in emails using the AWS email service and uploaded to an s3 bucket as a pdf archive.

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
