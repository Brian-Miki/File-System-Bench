from openai import OpenAI
import os
from dotenv import load_dotenv
from data_loader import get_questions, get_news, get_summaries
from tools import grep_file, tool_description
from openai_client import get_openai_client
import json


load_dotenv()


def agent_openai_call() -> list[str]:
    tools = tool_description()
    questions = get_questions()
    summaries = get_summaries()
    output = []
    client = get_openai_client()

    for question in questions:
        input_list = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Answer the question concisely in 1–2 sentences using the following information sources and the related GREP tool call. We reccomend sending off various calls to ensure all information and context is stored.\n"
                            f"Summaries: {summaries}\n\nQuestion: {question}"
                        ),
                    }
                ],
            }
        ]

        response = client.responses.create(
            model="gpt-5-nano",
            tools=tools,
            input=input_list,
        )
        input_list += response.output
        for item in response.output:
            if item.type == "function_call" and item.name == "grep_file":
                args = json.loads(item.arguments)

                info = grep_file(pattern=args["pattern"])
                print(args["pattern"])

                # Provide function call results to the model
                input_list.append(
                    {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({"grep_result": info}),
                    }
                )

        response = client.responses.create(
            model="gpt-5-nano",
            tools=tools,
            input=input_list,
        )
        output.append(response.output_text)
        print(response.output_text)

    return output


def oneshot_openai_call()->list[str]:
    output = []
    questions = get_questions()
    news = get_news()
    client = get_openai_client()
    for question in questions:
        response = client.responses.create(
            model="gpt-5-nano",
            input="Answer the question concisely in 1 sentences using the following information sources.\n"
                            f"News: {news}\n\nQuestion: {question}",
        )
        output.append(response.output_text)
        print(response.output_text)

    return output

print(oneshot_openai_call())
print(agent_openai_call())
