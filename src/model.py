from dotenv import load_dotenv
from data_loader import get_questions, get_news, get_summaries, get_answers
from tools import grep_file, tool_description, research_complete, cat_file
from openai_client import get_openai_client, get_async_openai_client
import json
import time
import asyncio
from pathlib import Path
from openai import AsyncOpenAI

current_time = time.ctime()
load_dotenv()


def agent_openai_call() -> str:
    """Execute the multi-tool research workflow for each question.

    Returns:
        str: Filesystem path to the log containing the agent responses and
            references to the correct answers.
    """

    tools = tool_description()
    questions = get_questions()
    summaries = get_summaries()
    answers = get_answers()
    buffer = []
    client = get_openai_client()
    log_path = f"logs/agent/logs_agent_{current_time}.json"

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
                model="gpt-4.1-nano-2025-04-14",
                tools=tools,
                tool_choice="required",
                input=input_list,
                # reasoning={"effort": "minimal"},
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
            model="gpt-4.1-nano-2025-04-14",
            input=input_list,
            # reasoning={"effort": "minimal"},
        )
        record = {
            "question": f"{question}",
            "ai_response": f"{response.output_text}",
            "correct_answer": f"{answers[i]}",
        }
        buffer.append(json.dumps(record, ensure_ascii=False))
    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n".join(buffer) + "\n")

    return log_path


async def oneshot_openai_call() -> str:
    """Answer every question in a single model call using the news digest.

    Returns:
        str: Filesystem path to the log capturing each question, generated
            answer, and ground-truth response.
    """
    questions = get_questions()
    news = get_news()
    client = get_async_openai_client()
    answers = get_answers()
    buffer = []
    lock = asyncio.Lock()

    await asyncio.gather(
        *(
            individual_response(
                news, question_text, client, answers[i], buffer, lock
            )
            for i, question_text in enumerate(questions)
        )
    )
    with open(
        f"logs/oneshot/logs_oneshot_{current_time}.json", "a", encoding="utf-8"
    ) as f:
        f.write("\n".join(buffer) + "\n")

    return f"logs/oneshot/logs_oneshot_{current_time}.json"


async def individual_response(
    news: list,
    question: str,
    client: AsyncOpenAI,
    answer: str,
    buffer: list,
    lock: asyncio.Lock,
):
    response = await client.responses.create(
        model="gpt-4.1-nano-2025-04-14",
        input="Answer the question concisely in 1 sentences using the following information sources.\n"
        f"News: {news}\n\nQuestion: {question}",
        # reasoning={"effort": "minimal"},
    )

    record = {
        "question": f"{question}",
        "ai_response": f"{response.output_text}",
        "correct_answer": f"{answer}",
    }
    async with lock:
        buffer.append(json.dumps(record, ensure_ascii=False))


async def llm_as_a_judge(path: str) -> str:
    """Grade each model response stored in a log file.

    Args:
        path (str): Path to a newline-delimited JSON log produced by one of the
            run modes where every line contains the question, the model answer,
            and the correct answer.

    Returns:
        str: Echo of ``path`` so callers can chain or log the evaluated file.
    """
    client = get_async_openai_client()
    print(f"Completing scoring for: {path}")
    with open(Path(path), "r", encoding="utf-8") as f:
        await asyncio.gather(*(individual_eval(json.loads(line), client) for line in f))

    return path


async def individual_eval(record: dict, client: AsyncOpenAI) -> str:
    """
    Evaluate a single model response using an LLM-as-a-judge.

    This function sends the question, the model-generated response, and the
    corresponding ground-truth answer to a grading model, which returns a
    binary judgment indicating whether the response should be considered
    correct.

    The evaluation is performed asynchronously and is intended to be used
    as part of a larger concurrent evaluation pipeline (e.g., via
    ``asyncio.gather``).

    Args:
        record (dict): A dictionary containing the evaluation data with the
            following keys:
            - ``"question"`` (str): The original question posed to the model.
            - ``"ai_response"`` (str): The model-generated answer to evaluate.
            - ``"correct_answer"`` (str): The reference answer used for grading.
        client (AsyncOpenAI): An asynchronous OpenAI client instance used to
            submit the grading request.

    Returns:
        str: A string judgment produced by the grading model, expected to be
        either ``"Correct"`` or ``"Incorrect"``.
    """
    response = await client.responses.create(
        model="gpt-4.1-nano-2025-04-14",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are an expert grader. "
                            "Only respond with either 'Correct' or 'Incorrect'. The answers do not need to have all context to be correct and the wording does not have to be identical to the correct answer."
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
                            f"<question>{record['question']}</question>\n"
                            f"<response>{record['ai_response']}</response>\n"
                            f"<correct_answer>{record['correct_answer']}</correct_answer>"
                        ),
                    }
                ],
            },
        ],
        # reasoning={"effort": "minimal"},
    )
    print(f"Question: {record['question']}")
    print(f"Guess: {record['ai_response']}")
    print(f"Answer: {record['correct_answer']}")
    print(response.output_text)
    print("--------------------")


path = asyncio.run(oneshot_openai_call())
#path = agent_openai_call()
asyncio.run(llm_as_a_judge(path))
