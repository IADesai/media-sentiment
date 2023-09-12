"""File that creates the visualizations for a report pdf of the media-sentiment findings,
then uploads the pdf to an s3 bucket and sends an email of the pdf."""


import sys
from os import environ
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import re

from dotenv import load_dotenv
from psycopg2.extensions import connection
from psycopg2 import connect, Error
import pandas as pd
import plotly.graph_objects as go
from xhtml2pdf import pisa
from boto3 import client


PDF_FILE_NAME = "Media-Sentiment.pdf"
PDF_FILE_PATH = "/tmp/Media-Sentiment.pdf"
GREEN = "#199988"
RED = "#e15759"


def join_all_stories_info(conn: connection) -> pd.DataFrame:   # pragma: no cover
    "Function that joins the stories and story sources SQL tables."
    query = """SELECT story_id, title, description,url, pub_date, media_sentiment,
    source_name FROM stories JOIN sources ON stories.source_id = sources.source_id"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    stories_df = pd.DataFrame(tuples_list, columns=[
        "story_id", "title", "description", "url", "pub_date",
        "article_sentiment", "source_name"])
    return stories_df


def join_all_reddit_info(conn: connection) -> pd.DataFrame:   # pragma: no cover
    "Function that joins all reddit sources SQL tables."
    query = """SELECT * FROM reddit_article"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    columns_list = ["article_id", "domain", "title", "article_url",
                    "url", "re_sentiment_mean", "re_sentiment_st_dev",
                    "re_sentiment_median", "re_vote_score", "re_upvote_ratio",
                    "re_post_comments", "re_processed_comments", "re_created_timestamp"]
    reddit_df = pd.DataFrame(tuples_list, columns=columns_list)
    return reddit_df


def get_db_connection():   # pragma: no cover
    """Establishes a connection with the PostgreSQL database."""
    try:
        conn = connect(
            user=environ.get("DATABASE_USERNAME"),
            password=environ.get("DATABASE_PASSWORD"),
            host=environ.get("DATABASE_IP"),
            port=environ.get("DATABASE_PORT"),
            database=environ.get("DATABASE_NAME"),)
        print("Database connection established successfully.")
        return conn
    except Error as err:
        print("Error connecting to database: ", err)
        sys.exit()


def get_titles(titles) -> str:
    """Function that takes out all the title names from the top stories
    and returns them as a HTML ready string.
    """
    title_str = "<ul>"
    for title in titles:
        title_str += f"<li>{title}</li>"
    title_str += "</ul>"
    return title_str


def create_gauge_figure(data, source: str, filename: str, line_color: str) -> None:  # pragma: no cover
    """Creates a formatted gauge figure saved as a .svg file."""
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=data,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [-1, 1], 'tickfont': {"family": "Arial", "size": 24}},
               'bar': {'color': line_color,
                       'line': {"color": "white",
                                "width": 3}},
               'bgcolor': "white"},
        title={'text': f"{source} Average Sentiment", "font": {"family": "Arial", "size": 32}}))
    gauge_fig.update_layout(font={"family": "Arial"})
    gauge_fig.write_image(filename)


def choose_line_color(score: float) -> str:
    """Returns the color of the gauge plot according to a sentiment score."""
    if score >= 0:
        return GREEN
    if score < 0:
        return RED


def create_report(stories_data: pd.DataFrame, reddit_data: pd.DataFrame) -> str:  # pragma: no cover
    """Creates the HTML template for the report, including all visualizations as
    images within the HTML wrapper.
    """
    # Sort the stories_data DataFrame by article_sentiment in descending order
    sorted_article_data = stories_data.sort_values(
        by='article_sentiment', ascending=False)

    top_5_stories_titles = sorted_article_data.head(5)["title"]

    lowest_5_stories_titles = sorted_article_data.tail(5)["title"]

    sorted_reddit_data = reddit_data.sort_values(
        by='re_sentiment_mean', ascending=False)

    top_5_reddit_titles = sorted_reddit_data.head(5)["title"]

    lowest_5_reddit_titles = sorted_reddit_data.tail(5)["title"]

    stories_sources_average = stories_data.groupby(
        "source_name")["article_sentiment"].mean().__round__(2)

    bbc_sentiment_score = stories_sources_average.iloc[0]
    daily_mail_sentiment_score = stories_sources_average.iloc[1]

    bbc_line_color = choose_line_color(bbc_sentiment_score)
    daily_mail_line_color = choose_line_color(daily_mail_sentiment_score)

    create_gauge_figure(
        bbc_sentiment_score, "BBC", "/tmp/bbc_plot.svg", bbc_line_color)

    create_gauge_figure(
        daily_mail_sentiment_score, "Daily Mail", "/tmp/daily_mail_plot.svg", daily_mail_line_color)

    template = f'''
<html>
<head>
<style>
    /* Define the CSS styles for your dashboard here */

    .title-container {{
        display: flex;
        flex-direction: row;
    }}

    
    .widget {{
        background-color: #fff;
        padding: 9px;
        margin-bottom: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}

    .sentiment-container {{
        display: flex;
        justify-content: center;
    }}
    /* Add more styles as needed */
</style>
</head>
<body>
<div class="title-container">
    <img style="width: 50px; height: 50px; margin-bottom: 10px;" src="SL_Favicon-45.png" alt="Logo" class=title-container/>
    <span style="text-align:center;font-size:250%;">Media Sentiment Daily Quarter Report</span>
</div>

<div class="widget">
    <div class="sentiment-container">
        <img style="width: 300px; height: 200px" src = "/tmp/bbc_plot.svg" alt="BBC"/>
        <img style="width: 300px; height: 200px" src = "/tmp/daily_mail_plot.svg" alt="Daily Mail"/>
    </div>
</div>

<div class="widget">
    <h1>Highest article sentiment stories</h1>
    {get_titles(top_5_stories_titles)}
</div>

<div class="widget">
    <h1>Lowest article sentiment stories</h1>
    {get_titles(lowest_5_stories_titles)}
</div>

<div class="widget">
    <h1>Highest Reddit sentiment stories</h1>
    {get_titles(top_5_reddit_titles)}
</div>

<div class="widget">
    <h1>Lowest Reddit sentiment stories</h1>
    {get_titles(lowest_5_reddit_titles)}
</div>

<!-- Add more widgets as needed -->
</body>
</html>
'''
    return template


def convert_html_to_pdf(html_template: str) -> bool:   # pragma: no cover
    """Converts the HTML template provided into a pdf report file."""
    # open output file for writing (truncated binary)
    if not isinstance(html_template, str):
        raise ValueError("The HTML template should be provided as a string")

    with open(PDF_FILE_PATH, "w+b") as pdf:
        pisa_status = pisa.CreatePDF(html_template, dest=pdf)

    # return True on success and False on errors
    return pisa_status.err


def create_filename_for_s3_pdf() -> str:
    """Returns a filename for the uploaded pdf using the current date and time."""
    filename = re.sub(r"(.+)\.pdf", "\\1", PDF_FILE_NAME)
    date_time = datetime.now().strftime("%Y_%m_%d-%H_%M_%S_")
    return date_time + filename + ".pdf"


def upload_to_s3() -> None:   # pragma: no cover
    """Function that uploads the created pdf to an S3 bucket."""
    print("Establishing connection to AWS.")
    s3_client = client("s3", aws_access_key_id=environ.get("ACCESS_KEY"),
                       aws_secret_access_key=environ.get("SECRET_KEY"))
    print("Connection established.")
    file_name_with_date_and_time = create_filename_for_s3_pdf()
    print("Uploading .pdf file.")
    s3_client.upload_file(
        PDF_FILE_PATH, environ.get("BUCKET_NAME"), file_name_with_date_and_time)
    print(".pdf file uploaded.")


def create_email_attachment() -> MIMEApplication:  # pragma: no cover
    """Loads a .pdf file as an email attachment."""
    print("Loading .pdf attachment")
    with open(PDF_FILE_PATH, "rb") as pdf_file:
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


def send_email(email_message: MIMEMultipart) -> None:  # pragma: no cover
    """Sends an email with an attachment."""
    print("Sending email.")
    if not isinstance(email_message, MIMEMultipart):
        raise TypeError("Email message not supplied as expected.")
    ses_client = client("ses", aws_access_key_id=environ.get("ACCESS_KEY"),
                        aws_secret_access_key=environ.get("SECRET_KEY"))
    ses_client.send_raw_email(Source=environ.get("EMAIL_SENDER"),
                              Destinations=[environ.get("EMAIL_RECIPIENT")],
                              RawMessage={"Data": email_message.as_string()})
    print("Email sent.")


def handler(event, context):  # pragma: no cover
    """Lambda handler function."""

    load_dotenv()
    db_conn = get_db_connection()

    joined_stories_df = join_all_stories_info(db_conn)
    print("joined_stories_works")

    joined_reddit_df = join_all_reddit_info(db_conn)
    print("joined_reddit_works")

    report_template = create_report(joined_stories_df, joined_reddit_df)
    print("report_template_works")

    convert_html_to_pdf(report_template)
    print("convert_to_pdf_works")

    upload_to_s3()

    send_email(create_email_message())

    return {
        "status": "success"
    }
