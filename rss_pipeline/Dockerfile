FROM amazon/aws-lambda-python

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy over required dependencies
COPY requirements.txt .
COPY vader_lexicon.txt .
COPY download_nltk_vader.py .

# Install the dependencies
RUN pip3 install -r requirements.txt
RUN python3 download_nltk_vader.py

COPY extract_rss.py .
COPY transform_rss.py .
COPY load.py .

COPY lambda_function.py .

CMD [ "lambda_function.handler" ]