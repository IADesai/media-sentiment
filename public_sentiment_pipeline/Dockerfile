FROM python

WORKDIR /reddit-pipeline

COPY requirements.txt .

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

COPY extract.py .

COPY transform.py .

COPY load.py .

CMD python3 load.py