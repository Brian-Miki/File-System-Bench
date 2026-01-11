import subprocess


def grep_file(pattern: str, path: str, context_lines: int = 3):
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


grep_file(pattern="Tiger", path="data/games/Game-1-AL-Wildcard.txt", context_lines=2)
