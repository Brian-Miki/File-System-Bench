from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv()


def get_news() -> str:
    articles = ""

    folder = Path("data/games")
    for file_path in folder.iterdir():
        with file_path.open("r", encoding="utf-8") as f:
            contents = f.read()
            articles += contents
    return articles


def get_questions() -> list[str]:
    questions = []
    with open("data/tests/tests.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for question in data["questions_and_answers"]:
            questions.append(question["question"])
    return questions


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
