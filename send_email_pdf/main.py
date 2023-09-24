"""File that creates the visualizations for a report pdf of the media-sentiment findings,
then uploads the pdf to an s3 bucket and sends an email of the pdf."""


import sys
from os import environ
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
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


def get_top_stories(conn: connection) -> pd.DataFrame:   # pragma: no cover
    "Function that joins all SQL tables."
    query = """SELECT title from stories WHERE stories.pub_date BETWEEN NOW() - INTERVAL '24 HOURS'
    AND NOW() ORDER BY media_sentiment DESC LIMIT 3;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    columns_list = ["title"]
    top_df = pd.DataFrame(tuples_list, columns=columns_list)
    return top_df


def get_bottom_stories(conn: connection) -> pd.DataFrame:   # pragma: no cover
    "Function that joins all SQL tables."
    query = """SELECT title from stories WHERE stories.pub_date BETWEEN NOW() - INTERVAL '24 HOURS'
    AND NOW() ORDER BY media_sentiment ASC LIMIT 3;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    columns_list = ["title"]
    bottom_df = pd.DataFrame(tuples_list, columns=columns_list)
    return bottom_df


def get_media_averages(conn: connection) -> pd.DataFrame:   # pragma: no cover
    "Function that gets the averages of media sentiment for different media outlets"
    query = """SELECT source_name, AVG(media_sentiment)
FROM stories
JOIN sources ON sources.source_id = stories.source_id
WHERE stories.pub_date BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()
GROUP BY source_name ORDER BY source_name;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    stories_df = pd.DataFrame(tuples_list, columns=[
        "source_name", "average_media_sentiment"])
    return stories_df


def get_topic_counts(conn: connection) -> pd.DataFrame:   # pragma: no cover
    "Function that gets the count of topics discussed in last 24 hours"
    query = """WITH top_keywords AS (
    SELECT
        keywords.keyword,
        (
            COUNT(DISTINCT stories.story_id) + COUNT(DISTINCT ra.re_article_id)
        ) AS total_count
    FROM
        keywords
    JOIN story_keyword_link ON keywords.keyword_id = story_keyword_link.keyword_id
    JOIN stories ON story_keyword_link.story_id = stories.story_id
    JOIN reddit_keyword_link rl ON keywords.keyword_id = rl.keyword_id
    JOIN reddit_article ra ON ra.re_article_id = rl.re_article_id
    WHERE
        stories.pub_date >= (CURRENT_TIMESTAMP - INTERVAL '24 hours')
        AND ra.re_created_timestamp >= (CURRENT_TIMESTAMP - INTERVAL '24 hours')
    GROUP BY
        keywords.keyword
    ORDER BY
        total_count DESC
    LIMIT 5
)
SELECT *
FROM top_keywords ORDER BY total_count ASC;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    topics_df = pd.DataFrame(tuples_list, columns=[
        "keyword", "total_count"])
    return topics_df


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
        title_str += f"<li style='font-size:12px';><b>{title}</b></li>"
    title_str += "</ul>"
    return title_str


def create_gauge_figure(data, source: str, filename: str, line_color: str) -> None:  # pragma: no cover
    """Creates a formatted gauge figure saved as a .svg file."""
    layout = go.Layout(
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=50,  # top margin
        )
    )
    gauge_fig = go.Figure(layout=layout, data=[go.Indicator(
        mode="gauge+number+delta",
        value=data,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={'axis': {'range': [-1, 1], 'tickfont': {"family": "Arial", "size": 24}},
               'bar': {'color': line_color,
                       'line': {"color": "white",
                                "width": 3}},
               'bgcolor': "white"},
        title={'text': f"{source} Sentiment", "font": {"family": "Arial", "size": 40}})])
    gauge_fig.update_layout(font={"family": "Arial"})
    gauge_fig.write_image(filename)


def choose_line_color(score: float) -> str:
    """Returns the color of the gauge plot according to a sentiment score."""
    if score >= 0:
        return GREEN
    if score < 0:
        return RED


def create_most_popular_topics_bar_chart(data, file_name: str) -> None:    # pragma: no cover
    """Creates a formatted horizontal bar chart saved as a .svg file."""
    layout = go.Layout(
        margin=go.layout.Margin(
            l=0,  # left margin
            r=0,  # right margin
            b=0,  # bottom margin
            t=0,  # top margin
        )
    )
    y_list = list(data["keyword"])
    x_list = list(data["total_count"])
    horizontal_fig = go.Figure(layout=layout, data=[go.Bar(
        x=x_list,
        y=y_list,
        orientation='h')])
    horizontal_fig.update_layout(font={"family": "Arial", "size": 16})
    horizontal_fig.write_image(file_name)


def create_report(top: pd.DataFrame, bottom: pd.DataFrame, media_average_data: pd.DataFrame,
                  count_of_topics: pd.DataFrame) -> str:  # pragma: no cover
    """Creates the HTML template for the report, including all visualizations as
    images within the HTML wrapper.
    """

    top_5_titles = top.head(3)["title"]

    lowest_5_titles = bottom.tail(3)["title"]

    stories_sources_average = media_average_data["average_media_sentiment"]

    bbc_sentiment_score = stories_sources_average.iloc[0]
    daily_mail_sentiment_score = stories_sources_average.iloc[1]

    bbc_line_color = choose_line_color(bbc_sentiment_score)
    daily_mail_line_color = choose_line_color(daily_mail_sentiment_score)

    create_gauge_figure(
        bbc_sentiment_score, "BBC", "/tmp/bbc_plot.svg", bbc_line_color)

    create_gauge_figure(
        daily_mail_sentiment_score, "Daily Mail", "/tmp/daily_mail_plot.svg", daily_mail_line_color)

    create_most_popular_topics_bar_chart(
        count_of_topics, "/tmp/most_popular_plot.svg")

    template = f'''
<html>
<head>
<style>
    /* Define the CSS styles for your dashboard here */

    html {{ -webkit-print-color-adjust: exact; }}

    body{{
    background-color: #292929;
    font-family: Rockwell;
    }}
    
    .widget {{
        background-color: #fff;
        padding: 2px;
        border-radius: 2px;
    }}

    /* Add more styles as needed */
</style>
</head>
<body style="background: #292929;">

<div class="title-container">
    <img src="media-sentiment-report-header.png" alt="Media Sentiment Report" class=title-container/>
</div>

<table border="0" style="width:100%;text-align:center">
<tr>
<td><img style="width: 260px; height: 160px" src = "/tmp/bbc_plot.svg" alt="BBC"/></td>
<td><img style="width: 260px; height: 160px" src = "/tmp/daily_mail_plot.svg" alt="Daily Mail"/></td>
</tr>
</table>

<h1 style='text-align:center;color:#fff;padding-top:10px;'>Most Popular Topics</h1>

<div class="widget">
    <img style="width:600px;height: 300px;text-align:center" src = "/tmp/most_popular_plot.svg" alt="Most Popular"/>
</div>

<h1 style='text-align:center;color:#88C180;padding-top:10px;'>Highest Sentiment Stories</h1>

<div class="widget">
    {get_titles(top_5_titles)}
</div>

<h1 style='text-align:center;color:#EA898B;padding-top:10px;'>Lowest Sentiment Stories</h1>

<div class="widget">
    {get_titles(lowest_5_titles)}
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

    media_averages = get_media_averages(db_conn)
    print("joined_stories_works")

    topic_counts = get_topic_counts(db_conn)

    top_stories = get_top_stories(db_conn)

    bottom_stories = get_bottom_stories(db_conn)

    report_template = create_report(
        top_stories, bottom_stories, media_averages, topic_counts)
    print("report_template_works")

    convert_html_to_pdf(report_template)
    print("convert_to_pdf_works")

    upload_to_s3()

    send_email(create_email_message())

    return {
        "status": "success"
    }


handler(0, 0)
