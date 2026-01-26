from dotenv import load_dotenv
from data_loader import get_questions, get_news, get_summaries
from tools import grep_file, tool_description, research_complete, cat_file
from openai_client import get_openai_client
import json


load_dotenv()


def agent_openai_call() -> list[str]:
    with open("logs/logs.txt", "a", encoding="utf-8") as f:
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
                                "Answer the question concisely in 1–2 sentences using the following information sources and the related GREP and CAT tool calls. Don't do over 5 function calls. It is better to share your answer once you are fairly certain it is correct.\n"
                                f"Summaries: {summaries}\n\nQuestion: {question}"
                            ),
                        }
                    ],
                }
            ]

            research_done = False
            counter = 0
            f.write(f"Question: {question}\n")

            while research_done == False and counter < 10:
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

            response = client.responses.create(
                model="gpt-5-nano",
                input=input_list,
                reasoning={"effort": "low"},
            )
            output.append(response.output_text)
            f.write(f"Final response: {response.output_text}\n\n\n")

    return output


def oneshot_openai_call() -> list[str]:
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


print(oneshot_openai_call())
# print(agent_openai_call())
