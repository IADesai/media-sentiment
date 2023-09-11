## Keyword Tagging Pipeline 

### Setup 
Create Python virtual environment and install the required packages.
```
python3 -m venv venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_lg 
```

### Environment
Create a .env file to store following environment variables:
```
ACCESS_KEY_ID=XXXX
SECRET_ACCESS_KEY=XXX
DATABASE_NAME=XXXX
DATABASE_USERNAME=XXXX
DATABASE_PASSWORD=XXXX
DATABASE_ENDPOINT=XXXX
DB_PORT=XXXX
OPENAI_API_KEY=XXXX
```

### Build a Docker Image
Build a Docker image using:
```
docker build -t tagging_pipeline . --platform "linux/amd64"
```
Run the Docker Image using
```
docker run -it --env-file .env tagging_pipeline
```