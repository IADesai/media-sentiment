"""File that creates the visualizations for a report pdf of the media-sentiment findings"""
import sys
import base64
from os import environ

from dotenv import load_dotenv
from psycopg2.extensions import connection
from psycopg2 import connect, Error
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from xhtml2pdf import pisa

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

def create_report(db_connection: connection) -> str:
    """Creates the HTML template for the report, including all visualizations as
    images within the html wrapper"""
    img_bytes = px.scatter([1, 2, 3], [4, 5, 6]).to_image()
    img = base64.b64encode(img_bytes).decode("utf-8")
    template = f'''
    <h1>Media Sentiment</h1>
    <p>Latest report</p>
    <img style="width: 400; height: 600" src="data:image/png;base64,{img}">
    '''
    return template

def convert_html_to_pdf(html_template: str, file: str) -> None:
    """Converts the HTML template provided into a pdf report file"""
    # open output file for writing (truncated binary)
    if not isinstance(html_template, str):
        raise ValueError("The HTML template should be provided as a string")
    if not isinstance(file, str):
        raise ValueError("The file name should be provided as a string")
    result_file = open(file, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.CreatePDF(
            html_template,                # the HTML to convert
            dest=result_file)           # file handle to receive result

    # close output file
    result_file.close()

    # return True on success and False on errors
    return pisa_status.err

if __name__ == "__main__":
    load_dotenv()
    connection = get_db_connection()
    report_template = create_report(connection)
    convert_html_to_pdf(report_template, environ.get("REPORT_FILE"))