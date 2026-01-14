from pathlib import Path
import json


def get_news() -> str:
    articles = ""

    folder = Path("data/games")
    for file_path in folder.iterdir():
        with file_path.open("r", encoding="utf-8") as f:
            contents = f.read()
            articles += contents
    return articles


def get_summaries() -> str:
    with open("data/summary/combined_news.txt", "r", encoding="utf-8") as f:
        text = f.read()
    return text


def get_questions() -> list[str]:
    questions = []
    with open("data/tests/tests.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for question in data["questions_and_answers"]:
            questions.append(question["question"])
    return questions
