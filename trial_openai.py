from os import environ
import openai
from dotenv import load_dotenv

load_dotenv()
config = environ

openai.api_key=config["OPENAI_KEY"]

# curl https://api.openai.com/v1/chat/completions \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer $OPENAI_API_KEY" \
#   -d '{
#      "model": "gpt-3.5-turbo",
#      "messages": [{"role": "user", "content": "Say this is a test!"}],
#      "temperature": 0.7
#    }'