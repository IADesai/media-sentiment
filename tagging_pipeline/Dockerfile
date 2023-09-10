FROM public.ecr.aws/lambda/python

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY extract.py .

COPY transform.py .

COPY load.py .

COPY pipeline.py .

CMD ["pipeline.lambda_handler"]

