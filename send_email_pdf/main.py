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


def join_all_info(conn: connection) -> pd.DataFrame:
    "Function that joins all SQL tables."
    query = """SELECT * 
            FROM stories 
            JOIN sources ON sources.source_id = stories.source_id
            JOIN story_keyword_link ON story_keyword_link.story_id = stories.story_id
            JOIN keywords ON keywords.keyword_id = story_keyword_link.keyword_id
            JOIN reddit_keyword_link ON reddit_keyword_link.keyword_id = keywords.keyword_id
            JOIN reddit_article ON reddit_article.re_article_id = reddit_keyword_link.re_article_id;"""
    with conn.cursor() as cur:
        cur.execute(query)
        tuples_list = cur.fetchall()
    columns_list = ["story_id", "source_id", "title", "description",
                    "url", "pub_date", "media_sentiment",
                    "source_id", "source_name",
                    "link_id", "keyword_id", "story_id",
                    "keyword_id", "keyword",
                    "re_link_id", "keyword_id", "re_article_id",
                    "re_article_id", "re_domain", "re_title", "re_article_url", "re_url", "re_sentiment_mean",
                    "re_sentiment_st_dev", "re_sentiment_median", "re_vote_score", "re_upvote_ratio", "re_post_comments",
                    "re_processed_comments", "re_created_timestamp"
                    ]
    complete_df = pd.DataFrame(tuples_list, columns=columns_list)
    return complete_df


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
        title={'text': f"{source} Sentiment", "font": {"family": "Arial", "size": 32}}))
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
    y_list = list(data.keys())
    x_list = list(data.values())
    horizontal_fig = go.Figure(go.Bar(
        x=x_list,
        y=y_list,
        orientation='h'))
    horizontal_fig.update_layout(font={"family": "Arial"})
    horizontal_fig.write_image(file_name)


def get_last_24_hours_of_data(all_data: pd.DataFrame) -> pd.DataFrame:
    """Function that filters out all data to the data from the
    last 24 hours only"""
    all_data["article_datetime"] = pd.to_datetime(
        all_data['pub_date'])
    all_data["reddit_datetime"] = pd.to_datetime(
        all_data['re_created_timestamp'])

    now = datetime.now()
    one_day = timedelta(days=1)

    stories_in_last_24_hours = all_data[
        (now - all_data["article_datetime"] < one_day) &
        (now - all_data["reddit_datetime"] < one_day)]

    return stories_in_last_24_hours


def create_report(recent_data: pd.DataFrame, all_data: pd.DataFrame) -> str:  # pragma: no cover
    """Creates the HTML template for the report, including all visualizations as
    images within the HTML wrapper.
    """

    sorted_article_data = recent_data.sort_values(
        by='average_sentiment', ascending=False)

    top_5_titles = sorted_article_data.head(3)["title"]

    lowest_5_titles = sorted_article_data.tail(3)["title"]

    stories_sources_average = all_data.groupby(
        "source_name")["media_sentiment"].mean().__round__(2)

    bbc_sentiment_score = stories_sources_average.iloc[0]
    daily_mail_sentiment_score = stories_sources_average.iloc[1]

    bbc_line_color = choose_line_color(bbc_sentiment_score)
    daily_mail_line_color = choose_line_color(daily_mail_sentiment_score)

    create_gauge_figure(
        bbc_sentiment_score, "BBC", "/tmp/bbc_plot.svg", bbc_line_color)

    create_gauge_figure(
        daily_mail_sentiment_score, "Daily Mail", "/tmp/daily_mail_plot.svg", daily_mail_line_color)

    most_popular_topics = recent_data["keyword"].value_counts().head(
        5).sort_values(
        ascending=True).to_dict()

    create_most_popular_topics_bar_chart(
        most_popular_topics, "/tmp/most_popular_plot.svg")

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
    <img src="media-sentiment-report-header.png" alt="Media Sentiment Report" class=title-container/>
</div>

<div class="widget">
    <div class="sentiment-container">
        <img style="width: 300px; height: 200px" src = "/tmp/bbc_plot.svg" alt="BBC"/>
        <img style="width: 300px; height: 200px" src = "/tmp/daily_mail_plot.svg" alt="Daily Mail"/>
    </div>
</div>

<div class="widget">
    <h1>Highest Sentiment Stories</h1>
    {get_titles(top_5_titles)}
</div>

<div class="widget">
    <h1>Lowest Sentiment Stories</h1>
    {get_titles(lowest_5_titles)}
</div>

<div class="widget">
    <img style="width: 300px; height: 200px" src = "/tmp/most_popular_plot.svg" alt="Most Popular"/>
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

    complete_df = join_all_info(db_conn)
    complete_df["average_sentiment"] = (
        complete_df["media_sentiment"] + complete_df["re_sentiment_mean"])/2
    complete_df.to_csv("joined_all.csv")
    print("joined_all_works")

    last_24_hour_data = get_last_24_hours_of_data((complete_df))

    report_template = create_report(last_24_hour_data, complete_df)
    print("report_template_works")

    convert_html_to_pdf(report_template)
    print("convert_to_pdf_works")

    upload_to_s3()

    send_email(create_email_message())

    return {
        "status": "success"
    }


handler(0, 0)
