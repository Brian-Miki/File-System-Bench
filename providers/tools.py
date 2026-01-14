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

def research_complete() -> str:
    return f"The research is complete. Answer the question based on the research provided in 1 sentence."    


def tool_description() -> list[dict]:
    return [
        {
            "type": "function",
            "name": "grep_file",
            "description": (
                "Search the game text files for concrete evidence related to the question. "
                "Use this tool to look up names, events, statistics, or exact phrases "
                "that are likely to not appear verbatim in the source text."
                "Avoid patterns and paths already used as the contents in the files does not change."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": (
                            "A distinctive keyword or short phrase to search for "
                            "(e.g., player name, team name, or unique event)."
                        ),
                    },
                    "path": {
                        "type": "string",
                        "description": (
                            "Optional file or directory path to search. "
                            "If omitted, the default games directory is used."
                        ),
                    },
                },
                "required": ["pattern"],
            },
        },
        {
            "type": "function",
            "name": "research_complete",
            "description": (
                "Call this once sufficient evidence has been gathered and no further "
                "search is needed."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    ]
