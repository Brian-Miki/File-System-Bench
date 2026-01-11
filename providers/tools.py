import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_GAMES_DIR = BASE_DIR / "data" / "games"


def grep_file(pattern: str, context_lines: int = 3):
    cmd = [
        "rg",
        pattern,
        str(DATA_GAMES_DIR),
        "--context",
        str(context_lines),
        "--no-heading",
        "--line-number",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    return {
        "stdout": result.stdout[:8000],
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }


print(grep_file(pattern="Tiger", context_lines=2))


def tool_description() -> list[dict]:
    tools = [
        {
            "type": "function",
            "name": "grep_file",
            "description": "Look for pattern in file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "A string pattern you are looking for",
                    },
                },
                "required": ["pattern"],
            },
        },
    ]
    return tools
