FROM python

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY extract.py .

COPY transform.py .

COPY load.py .

COPY pipeline.py .

CMD python3 pipeline.py

