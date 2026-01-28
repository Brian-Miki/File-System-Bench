import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_GAMES_DIR = BASE_DIR / "data" / "games"


def grep_file(pattern: str, path: str = str(BASE_DIR), context_lines: int = 3):
    cleaned_pattern = pattern.replace("\x00", "")

    if not Path(path).exists():
        return {
            "stdout": "",
            "stderr": f"Invalid path: '{path}' does not exist.",
            "exit_code": 1,
        }

    cmd = [
        "rg",
        cleaned_pattern,
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


def cat_file(path: str):
    if not Path(path).exists():
        return {
            "stdout": "",
            "stderr": f"Invalid path: '{path}' does not exist.",
            "exit_code": 1,
        }

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "stdout": content,
        "stderr": "",
        "exit_code": 0,
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
                "Example: When asked who played in the 2024 Olympics you may search the keyword Olympics."
                "Example: If there was a certain OPS tied to a unidentified palyer you may search that specific OPS."
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
        {
            "type": "function",
            "name": "cat_file",
            "description": (
                "Read and return the full contents of a specified text file. "
                "Use this tool when complete file context is required for understanding "
                "or summarization. The file should be text-based."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "The full path to the file to read. "
                            "The path must refer to an existing text file."
                        ),
                    }
                },
                "required": ["path"],
            },
        },
    ]
