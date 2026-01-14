import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_GAMES_DIR = BASE_DIR / "data" / "games"


def grep_file(pattern: str, path: str = str(DATA_GAMES_DIR),context_lines: int = 3):
    cmd = [
        "rg",
        pattern,
        path,
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
                            "A short phrase to search for in the text. "
                            "This should usually be a proper noun (e.g., a players first name), "
                            "a team name, or a distinctive phrase that is likely to appear exactly "
                            "in the source files."
                            "Make sure to keep things fairly generic to get as much context as needed."
                        ),
                    },
                    "path": {
                        "type": "string",
                        "description": (
                            "The specific path to the file the search is required for."
                            "The path should exactly match the one shared in the summarized information information given."
                        ),
                    },
                },
                "required": ["pattern"],
            },
        }
    ]
