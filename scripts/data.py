from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_GAMES_DIR = BASE_DIR / "data" / "games"
OUTPUT_FILE = BASE_DIR / "data" / "combined_news.txt"

def get_news() -> None:
    with OUTPUT_FILE.open("w", encoding="utf-8") as out:
        for file_path in sorted(DATA_GAMES_DIR.iterdir()):
            if file_path.is_file():
                with file_path.open("r", encoding="utf-8") as f:
                    line = f.readline()
                    out.write(line)
                    out.write("\nFILE_PATH: " + str(file_path) + "\n")
get_news()