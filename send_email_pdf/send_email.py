"""Python code for sending emails with attachments via AWS."""

from os import environ
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import boto3
from dotenv import load_dotenv

PDF_FILE_NAME = "example.pdf"


def create_email_attachment() -> MIMEApplication:  # pragma: no cover
    """Loads a .pdf file as an email attachment."""
    print("Loading .pdf attachment")
    with open(PDF_FILE_NAME, "rb") as pdf_file:
        pdf_attachment = MIMEApplication(pdf_file.read(), _subtype="pdf")
        pdf_attachment.add_header("content-disposition", "attachment",
                                  filename=PDF_FILE_NAME)
    print(".pdf attachment loaded.")
    return pdf_attachment


def create_email_message() -> MIMEMultipart:  # pragma: no cover
    """Creates an email message."""
    print("Creating email message.")
    message = MIMEMultipart()
    message["Subject"] = "Media Sentiment PDF Report"
    message.attach(create_email_attachment())
    print("Email message created.")
    return message


def send_email(config: dict, email_message: MIMEMultipart) -> None:  # pragma: no cover
    """Sends an email with an attachment."""
    print("Sending email.")
    if not isinstance(email_message, MIMEMultipart):
        raise TypeError("Email message not supplied as expected.")
    ses_client = boto3.client("ses", aws_access_key_id=config["ACCESS_KEY"],
                              aws_secret_access_key=config["SECRET_KEY"])
    ses_client.send_raw_email(Source=config["EMAIL_SENDER"],
                              Destinations=[config["EMAIL_RECIPIENT"]],
                              RawMessage={"Data": email_message.as_string()})
    print("Email sent.")


if __name__ == "__main__":  # pragma: no cover
    load_dotenv()
    configuration = environ
    send_email(configuration, create_email_message())
