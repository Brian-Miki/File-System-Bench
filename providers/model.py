from openai import OpenAI
import os
from dotenv import load_dotenv
from data_loader import get_questions, get_news


load_dotenv()


def openai_call() -> list[str]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    questions = get_questions()
    news = get_news()
    output = []
    for question in questions:
        response = client.responses.create(
            model="gpt-5-nano",
            input=f"Answer the question concisely in 1 - 2 sentences with the following information sources:{news}\n\nQuestion: {question}",
        )
        print(response.output_text)
        output.append(response.output_text)
    return output


openai_call()
