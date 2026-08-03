# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A minimal LangGraph + OpenAI agent starter kit, provided as both a CLI (`main.py`) and a Streamlit web UI (`app.py`). The repository name says "claude" but the current implementation defaults to the **OpenAI** provider — see the "나중에 Claude로 전환하는 법" section in README.md for the swap-back steps (replace `ChatOpenAI` with `ChatAnthropic` in `src/graph.py`).

## Setup and running

```bash
python3 -m venv .venv && source .venv/bin/activate   # some environments (e.g. Homebrew Python) block global pip installs
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY (TAVILY_API_KEY is optional)
```

```bash
python main.py           # CLI
streamlit run app.py     # web UI
```

There is no test suite, linter, or build step configured in this repository.

## Architecture

The agent is a LangGraph `StateGraph` that alternates between calling the model and executing tools:

```
call_model → (has tool_calls?) → tools → call_model → ... → END
```

- `src/graph.py` — `build_graph()` is the single source of truth for the agent graph. Both `main.py` (CLI) and `app.py` (Streamlit) call this same function so agent logic is never duplicated between entry points. The graph must be built once and reused (not rebuilt per request) because the `InMemorySaver` checkpointer is bound to the graph instance — rebuilding it loses conversation history.
- `src/config.py` — loads `.env` and exposes shared constants (`OPENAI_MODEL`, `MAX_TOKENS`, `WORKSPACE_DIR`, etc.). Both entry points import from here instead of reading env vars directly.
- Routing between `call_model` and `tools` uses LangGraph's prebuilt `tools_condition` helper rather than a custom conditional function.
- Conversation state is kept by `InMemorySaver`, keyed by `thread_id` — the CLI uses a fixed `"cli-session"` id, Streamlit generates a new UUID per browser session. This is in-memory only (lost on process restart); swap in `PostgresSaver` for persistence.

## Tools (`src/tools/`)

Three example tools are registered in `src/tools/__init__.py`'s `ALL_TOOLS` list, which `graph.py` binds to the model as-is:

- `calculator` — arithmetic only, no external dependencies. Deliberately avoids `eval()`; parses expressions via `ast` and walks the tree against an operator whitelist.
- `web_search` — calls the Tavily API. If `TAVILY_API_KEY` is unset, it returns a guidance string instead of raising, so the rest of the app keeps working without that key. The `tavily` import is deferred inside the function for the same reason.
- `read_local_file` — reads files sandboxed to `WORKSPACE_DIR` (the `workspace/` directory). Validates paths by resolving them and checking `is_relative_to()`, not by string-prefix comparison, to block `../` traversal and symlink escapes.

**To add a new tool:** define a function with `@tool` in a new file under `src/tools/`, then import it and append it to `ALL_TOOLS` in `src/tools/__init__.py`. Nothing else needs to change — `graph.py` binds whatever is in `ALL_TOOLS`.

## Known constraints

- `InMemorySaver` is a demo/dev-only checkpointer; conversation history does not survive a process restart.
- No auth, database, or deployment configuration is in scope for this starter kit.
- Claude Opus 5, if swapped in per the README, rejects `temperature`/`top_p`/`top_k` params (400 error) — the codebase already avoids setting these for either provider.
