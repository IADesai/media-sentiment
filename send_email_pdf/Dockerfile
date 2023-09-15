FROM amazon/aws-lambda-python

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy over required dependencies
COPY requirements.txt .
COPY media-sentiment-report-header.png .

# Install the dependencies
RUN pip3 install -r requirements.txt

COPY main.py .

CMD [ "main.handler" ]