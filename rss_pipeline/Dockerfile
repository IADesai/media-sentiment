FROM python

#Copy over requirements file
COPY requirements.txt .

#Install the requirements
RUN pip3 install -r requirements.txt


#Transfer over Python files
COPY extract_rss.py .
COPY transform_rss.py .
COPY load.py .
COPY deploy_pipeline.py .

#Run the script
CMD python3 deploy_pipeline.py 