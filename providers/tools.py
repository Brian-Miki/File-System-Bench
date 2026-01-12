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


def tool_description() -> list[dict]:
    return [
        {
            "type": "function",
            "name": "grep_file",
            "description": (
                "Search the game text files for specific evidence related to the question. "
                "Use this tool to look up concrete names, events, statistics, or phrases that are "
                "likely to appear verbatim in the source text. "
                "Prefer distinctive keywords (e.g., full player names, teams, or unique events) "
                "rather than generic terms. Do not use this tool for speculation or summarization."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": (
                            "A specific keyword or short phrase to search for in the text. "
                            "This should usually be a proper noun (e.g., a player name), "
                            "a team name, or a distinctive phrase that is likely to appear exactly "
                            "in the source files."
                        ),
                    },
                },
                "required": ["pattern"],
            },
        }
    ]
