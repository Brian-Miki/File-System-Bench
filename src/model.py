from dotenv import load_dotenv
from data_loader import get_questions, get_news, get_summaries, get_answers
from tools import grep_file, tool_description, research_complete, cat_file
from openai_client import get_openai_client
import json
import time

current_time = time.ctime()
load_dotenv()


def agent_openai_call() -> list[str]:
    tools = tool_description()
    questions = get_questions()
    summaries = get_summaries()
    answers = get_answers()
    buffer = []
    client = get_openai_client()
    for i, question in enumerate(questions):
        input_list = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are an autonomous research agent operating over a local file system. "
                            "You have access to tools that allow you to search file contents and read files. "
                            "Your goal is to gather only the minimum necessary evidence needed to answer the user's question accurately.\n\n"
                            "Rules:\n"
                            "- Use tools deliberately and efficiently\n"
                            "- Do not exceed 5 total tool calls\n"
                            "- Prefer targeted keyword searches over broad scans\n"
                            "- When you are confident you have enough information, call research_complete\n"
                            "- Do NOT answer the question until explicitly instructed to do so\n"
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "<instructions>\n"
                            "Search the provided files to gather evidence needed to answer the question.\n"
                            "You must determine relevant keywords yourself; the answer may not appear verbatim.\n"
                            "Use GREP to locate candidate files and CAT to read specific files.\n"
                            "Stop searching once sufficient evidence is found.\n"
                            "</instructions>\n\n"
                            "<constraints>\n"
                            "- Maximum of 5 tool calls total\n"
                            "- Use precise keyword searches\n"
                            "- Do NOT answer the question yet\n"
                            "</constraints>\n\n"
                            "<context>\n"
                            f"{summaries}\n"
                            "</context>\n\n"
                            "<question>\n"
                            f"{question}\n"
                            "</question>"
                        ),
                    }
                ],
            },
        ]

        research_done = False
        counter = 0

        while research_done is False and counter < 10:
            response = client.responses.create(
                model="gpt-5-nano",
                tools=tools,
                tool_choice="required",
                input=input_list,
                reasoning={"effort": "minimal"},
            )
            input_list += response.output
            for item in response.output:
                if item.type == "function_call" and item.name == "grep_file":
                    args = json.loads(item.arguments)

                    info = grep_file(pattern=args["pattern"])

                    input_list.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps({"summary": info}),
                        }
                    )
                elif item.type == "function_call" and item.name == "cat_file":
                    args = json.loads(item.arguments)

                    info = cat_file(path=args["path"])

                    input_list.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps({"file output": info}),
                        }
                    )

                elif item.type == "function_call" and item.name == "research_complete":
                    info = research_complete()
                    input_list.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps({"Final instruction": info}),
                        }
                    )
                    research_done = True

                else:
                    counter += 1

        input_list.append(
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are now switching from RESEARCH MODE to ANSWER MODE.\n"
                            "Your task is to produce a final answer using only the evidence already gathered.\n"
                            "Do not mention tools, searches, or file names unless necessary for clarity.\n"
                            "Do not speculate or add new information.\n"
                        ),
                    }
                ],
            }
        )

        response = client.responses.create(
            model="gpt-5-nano",
            input=input_list,
            reasoning={"effort": "low"},
        )
        record = {"question": f"{question}", "response": f"{response.output_text}", "answer": f"{answers[i]}"}
        buffer.append(json.dumps(record, ensure_ascii=False))
    with open(f"logs/agent/logs_agent_{current_time}.json", "a", encoding="utf-8") as f:
        f.write("\n".join(buffer) + "\n")

    return


def oneshot_openai_call():
    questions = get_questions()
    news = get_news()
    client = get_openai_client()
    answers = get_answers()
    buffer = []

    for i, question in enumerate(questions):
        response = client.responses.create(
            model="gpt-5-nano",
            input="Answer the question concisely in 1 sentences using the following information sources.\n"
            f"News: {news}\n\nQuestion: {question}",
            reasoning={"effort": "low"},
        )

        record = {"question": f"{question}", "response": f"{response.output_text}", "answer": f"{answers[i]}"}

        buffer.append(json.dumps(record, ensure_ascii=False))
    with open(
        f"logs/oneshot/logs_oneshot_{current_time}.json", "a", encoding="utf-8"
    ) as f:
        f.write("\n".join(buffer) + "\n")

    return


#oneshot_openai_call()
agent_openai_call()
