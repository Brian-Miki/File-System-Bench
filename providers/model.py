from dotenv import load_dotenv
from data_loader import get_questions, get_news, get_summaries
from tools import grep_file, tool_description
from openai_client import get_openai_client
import json


load_dotenv()


def agent_openai_call() -> list[str]:
    with open("logs.txt", "a",encoding='utf-8') as f:
        tools = tool_description()
        questions = get_questions()
        summaries = get_summaries()
        output = []
        client = get_openai_client()
        f.write(f"Summary: {summaries}")

        for question in questions:
            input_list = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Answer the question concisely in 1–2 sentences using the following information sources and the related GREP tool call. You MUST send off various calls to ensure all information and context is stored.\n"
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
                reasoning={"effort": "minimal"},
            )
            f.write(f"Question: {question}\n")
            input_list += response.output
            for item in response.output:
                if item.type == "function_call" and item.name == "grep_file":
                    args = json.loads(item.arguments)

                    info = grep_file(pattern=args["pattern"])
                    print(args["pattern"])
                    print(args["path"])

                    f.write(f"Tool Call Pattern: {args['pattern']}\n")
                    f.write(f"Tool Call Path: {args['path']}\n")
                    f.write(f"Tool Call Summary: {info}\n")

                    input_list.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps({"summary": info}),
                        }
                    )

            response = client.responses.create(
                model="gpt-5-nano",
                tools=tools,
                input=input_list,
                reasoning={"effort": "low"},
            )
            output.append(response.output_text)
            print(f"Final answer:{response.output_text}")
            f.write(f"Final response: {response.output_text}\n\n\n")

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
            reasoning={"effort": "low"},
        )
        output.append(response.output_text)
    return output


# print(oneshot_openai_call())
print(agent_openai_call())
