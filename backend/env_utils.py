import os
from dotenv import load_dotenv

load_dotenv(override=True)

LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME')
LLM_MODEL_URL = os.getenv('LLM_MODEL_URL')




