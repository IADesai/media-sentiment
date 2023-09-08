FROM amazon/aws-lambda-python

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements.txt
COPY requirements.txt .
COPY vader_lexicon.txt .
COPY download_nltk_vader.py .

# Install the specified packages
RUN pip3 install -r requirements.txt
RUN python3 download_nltk_vader.py



COPY extract_rss.py .
COPY transform_rss.py .
COPY load.py .

# Copy lambda function
COPY lambda_function.py .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_function.handler" ]