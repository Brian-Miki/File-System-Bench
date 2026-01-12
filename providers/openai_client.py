from openai import OpenAI
import os
from dotenv import load_dotenv
from data_loader import get_questions, get_news, get_summaries
from tools import grep_file, tool_description
import json





def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)