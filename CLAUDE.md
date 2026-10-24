# AI Kanban: project memory for Claude Code

## What this is
A study project. FastAPI + SQLite backend (`app/`), vanilla-JS drag-and-drop board (`static/index.html`).
Run: `uvicorn app.main:app --reload` · Test: `pytest -q`

## Golden rules
- **Do NOT implement anything in `app/ai/`.** Sid is writing the AI layer himself while studying for
  the Claude Certified Architect exam. Only touch `app/ai/` if he explicitly asks you to, and then
  explain rather than just write.
- Keep the worker contract: `app.ai.process_card(card) -> Outcome(column, reason)`.
- The board must keep working when the AI raises `NotImplementedError` (card bounces back to Items).
- Never commit `.env` or `data/`.

## Layout
- `app/main.py`: REST API + serves the UI
- `app/store.py`: all persistence (SQLite); the AI layer may call any function here
- `app/worker.py`: background queue; the only caller of `app.ai.process_card`
- `app/scheduler.py`: daily intake (recurring.json + inbox/notes.txt via `app/ai/intake.py`)
- `app/ai/`: Sid's stubs, each docstring tagged "Topic N"
