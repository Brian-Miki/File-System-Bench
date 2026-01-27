# LLM Research Bench

LLM Research Bench is a small playground for comparing a one-shot question-answering prompt with an agentic workflow that can iteratively inspect baseball recap files. The repo ships with a synthetic postseason news set, a handful of evaluation questions, and the scaffolding required to drive the OpenAI Responses API with function-calling tools (ripgrep search, file cat, research-complete handshake). Use it to prototype research agents, tweak prompting strategies, or benchmark prompt tuning ideas on a fixed corpus.

## Project layout

```
.
├── data/                 # Source articles, summaries, and evaluation questions
│   ├── games/            # Game recap text files used as the primary corpus
│   ├── off-season/       # Complementary news blurbs
│   ├── combined_news.txt # Summaries built from `scripts/data.py`
│   └── tests/tests.json  # Question + answer key used for evaluation
├── logs/                 # Append-only traces from model runs
├── scripts/
│   └── data.py           # Helper to regenerate `combined_news.txt`
├── src/
│   ├── data_loader.py    # Helpers that load news, summaries, and questions
│   ├── model.py          # One-shot baseline + agentic workflow
│   ├── openai_client.py  # Thin OpenAI client wrapper (expects OPENAI_API_KEY)
│   └── tools.py          # Tool implementations exposed to the agent
├── pyproject.toml        # Project metadata + runtime dependencies
└── uv.lock               # Locked dependency versions (optional with uv)
```

## Requirements

- Python 3.11+
- An OpenAI API key with access to the `gpt-5-nano` Responses API
- `rg` (ripgrep) available on your `PATH` for the agent's `grep_file` tool
- Optional but recommended: [`uv`](https://github.com/astral-sh/uv) for fast env management

## Setup

1. **Install dependencies**

   ```bash
   # create & activate a virtual environment if desired
   python -m venv .venv && source .venv/bin/activate

   # install via pip
   pip install -e .
   # or, with uv
   uv pip install --system .
   ```

2. **Expose your API key**

   Create a `.env` file (auto-loaded by `python-dotenv`) or export the variable directly:

   ```bash
   echo "OPENAI_API_KEY=sk-your-key" > .env
   # or
   export OPENAI_API_KEY=sk-your-key
   ```

## Running experiments

`src/model.py` contains two entry points:

- `oneshot_openai_call()` — sends each evaluation question along with the entire concatenated news corpus.
- `agent_openai_call()` — lets the model reason step-by-step, calling `grep_file`, `cat_file`, and `research_complete` before finalizing an answer.

At the bottom of `src/model.py`, whichever function is `print`ed will execute when you run the module. By default the one-shot baseline is active. Toggle which experiment runs by commenting/uncommenting the final two lines.

### One-shot baseline

```bash
# ensure print(oneshot_openai_call()) is uncommented
python -m src.model
```

Each answer is printed to stdout and appended to `logs/logs_oneshot.txt` alongside the raw response payload.

### Agentic workflow

```bash
# ensure print(agent_openai_call()) is uncommented instead
python -m src.model
```

During each step, the assistant's tool calls and outputs are recorded in `logs/logs_agent.txt`. The helper tools are implemented in `src/tools.py`:

- `grep_file` wraps `rg` to pull evidence snippets (default search path: `data/games`).
- `cat_file` reads a full file when more context is needed.
- `research_complete` signals the agent to stop researching and deliver the final answer.

Both flows iterate over the entire question set returned by `get_questions()`.

## Customization tips

- **Change the corpus**: swap any files under `data/games/` or `data/off-season/`, then rerun `python scripts/data.py` so the agent has an up-to-date `combined_news.txt` summary.
- **Alter evaluation questions**: edit `data/tests/tests.json`. Keeping answers in the file enables quick human scoring.
- **Add tools**: extend `src/tools.py` and update `tool_description()` to expose new functions (e.g., vector search, structured stats lookups).
- **Tweak prompts**: adjust the instructions inside `agent_openai_call()` and `oneshot_openai_call()` to explore different behaviors (answer length, step caps, etc.).
- **Swap models**: change the `model="gpt-5-nano"` parameter when calling the Responses API as long as the replacement supports function calling.

## Development & linting

- Run `ruff check .` before committing changes (dependency already listed in `pyproject.toml`).
- There are no automated tests yet; when modifying the agent logic, validate by running both flows and inspecting the logs for unexpected tool-call loops or empty outputs.

Happy benchmarking!
