# PDF Visualisation Reports

The code in this directory creates a PDF containing charts using the most recent data. These are sent as attachments in emails using the AWS email service.

## Required environment variables

The following environment variables must be supplied in a `.env` file.

- `ACCESS_KEY`
- `SECRET_KEY`
- `EMAIL_SENDER`
- `EMAIL_RECIPIENT`
