"""File that creates the visualizations for a report pdf of the media-sentiment findings,
then uploads the pdf to an s3 bucket and sends an email of the pdf."""


import sys
from os import environ
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime

from dotenv import load_dotenv
from psycopg2.extensions import connection
from psycopg2 import connect, Error
import pandas as pd
import plotly.graph_objects as go
from xhtml2pdf import pisa
from boto3 import client


PDF_FILE_NAME = "Media-Sentiment.pdf"


def join_all_stories_info(conn: connection) -> pd.DataFrame:
    "Function that joins the stories and story sources SQL tables"
    query = """SELECT story_id, title, description,url, pub_date, media_sentiment,
    source_name FROM stories JOIN sources ON stories.source_id = sources.source_id"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    stories_df = pd.DataFrame(tuples_list, columns=[
        "story_id", "title", "description", "url", "pub_date",
        "article_sentiment", "source_name"])
    return stories_df


def join_all_reddit_info(conn: connection) -> pd.DataFrame:
    "Function that joins all reddit sources SQL tables"
    query = """SELECT * FROM reddit_article"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    reddit_df = pd.DataFrame(tuples_list, columns=["article_id", "domain", "title", "article_url",
                                                   "url", "re_sentiment_mean", "re_sentiment_st_dev",
                                                   "re_sentiment_median", "re_vote_score", "re_upvote_ratio", "re_post_comments",
                                                   "re_processed_comments", "re_created_timestamp"])
    return reddit_df


def get_db_connection():
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
    and returns them as a html ready string"""
    title_str = "<ul>"
    for title in titles:
        title_str += f"<li>{title}</li>"
    title_str += "</ul>"
    return title_str


def create_report(stories_data: pd.DataFrame, reddit_data: pd.DataFrame) -> str:
    """Creates the HTML template for the report, including all visualizations as
    images within the html wrapper"""

    # Sort the stories_data DataFrame by article_sentiment in descending order
    sorted_article_data = stories_data.sort_values(
        by='article_sentiment', ascending=False)

    top_5_stories_data = sorted_article_data.head(5)
    top_5_stories_titles = top_5_stories_data["title"]

    lowest_5_stories_data = sorted_article_data.tail(5)
    lowest_5_stories_titles = lowest_5_stories_data["title"]

    sorted_reddit_data = reddit_data.sort_values(
        by='re_sentiment_mean', ascending=False)

    top_5_reddit_data = sorted_reddit_data.head(5)
    top_5_reddit_titles = top_5_reddit_data["title"]

    lowest_5_reddit_data = sorted_reddit_data.tail(5)
    lowest_5_reddit_titles = lowest_5_reddit_data["title"]

    stories_sources_average = stories_data.groupby(
        "source_name")["article_sentiment"].mean().__round__(2)

    if stories_sources_average.iloc[0] > 0:
        bbc_line_color = "lightgreen"
    if stories_sources_average.iloc[0] < 0:
        bbc_line_color = "#FF7276"

    if stories_sources_average.iloc[1] > 0:
        daily_mail_line_color = "lightgreen"
    if stories_sources_average.iloc[1] < 0:
        daily_mail_line_color = "#FF7276"

    bbc_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=stories_sources_average.iloc[0],
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [-1, 1]},
               'bar': {'color': bbc_line_color,
                       'line': {"color": "white",
                                "width": 3}},
               'bgcolor': "white"},
        title={'text': "BBC Average Sentiment"}))
    bbc_fig.write_image("bbc_plot.svg")

    daily_mail_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=stories_sources_average.iloc[1],
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [-1, 1]},
               'bar': {'color': daily_mail_line_color,
                       'line': {"color": "white",
                                "width": 3}},
               'bgcolor': "white"},
        title={'text': "Daily Mail Average Sentiment"}))
    daily_mail_fig.write_image("daily_mail_plot.svg")

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
        <img style="width: 300px; height: 200px" src = "bbc_plot.svg" alt="BBC"/>
        <img style="width: 300px; height: 200px" src = "daily_mail_plot.svg" alt="Daily Mail"/>
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
    <h1>Highest reddit sentiment stories</h1>
    {get_titles(top_5_reddit_titles)}
</div>

<div class="widget">
    <h1>Lowest reddit sentiment stories</h1>
    {get_titles(lowest_5_reddit_titles)}
</div>

<!-- Add more widgets as needed -->
</body>
</html>
'''
    return template


def convert_html_to_pdf(html_template: str) -> None:
    """Converts the HTML template provided into a pdf report file"""
    # open output file for writing (truncated binary)
    if not isinstance(html_template, str):
        raise ValueError("The HTML template should be provided as a string")
    if not isinstance(PDF_FILE_NAME, str):
        raise ValueError("The file name should be provided as a string")
    result_file = open(PDF_FILE_NAME, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
        html_template,                # the HTML to convert
        dest=result_file)           # file handle to receive result

    # close output file
    result_file.close()

    # return True on success and False on errors
    return pisa_status.err


def upload_to_s3() -> None:
    """Function that uploads the created pdf to an s3 bucket"""
    print("Establishing connection to AWS.")
    s3_client = client("s3", aws_access_key_id=environ.get("ACCESS_KEY"),
                       aws_secret_access_key=environ.get("SECRET_KEY"))
    print("Connection established.")
    file_split = PDF_FILE_NAME.split(".")
    date_time = datetime.now().strftime("%d\%m\%Y, %H:%M:%S")
    file_split[0] += f"({date_time})"
    file_name_with_date_and_time = ".".join(file_split)
    print("Uploading .pdf file.")
    s3_client.upload_file(
        PDF_FILE_NAME, environ.get("BUCKET_NAME"), file_name_with_date_and_time)
    print(".pdf file uploaded.")


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


def handler(event, context):
    """Lambda handler function"""

    load_dotenv()
    db_conn = get_db_connection()

    joined_stories_df = join_all_stories_info(db_conn)

    joined_reddit_df = join_all_reddit_info(db_conn)

    report_template = create_report(joined_stories_df, joined_reddit_df)

    convert_html_to_pdf(report_template)

    upload_to_s3()

    send_email(create_email_message())

    return {
        "status": "success"
    }
