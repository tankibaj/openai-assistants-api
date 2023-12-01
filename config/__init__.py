import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
openweathermap_key = os.getenv("OPENWEATHERMAP_KEY")
