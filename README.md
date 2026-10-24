# AI Kanban (CCAR-F study project)

A 4-column board (**Items → In-Progress → Human QA → Completed**). You add cards (or they arrive automatically every morning), write prompts as comments, and drag a card to **In-Progress**. That hands it to an AI agent, which works on it and returns it to **Human QA** or **Completed**.

**Everything except the AI is built.** The AI layer (`app/ai/`) is a set of empty, documented stubs. You fill them in as you work through `CCAR-F_Study_Guide_Kanban.html` (in the Sid folder). Each stub's docstring names its topic.

## Run it

```bash
cd Projects/AI_Kanban
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # add your ANTHROPIC_API_KEY when you start Topic 1
uvicorn app.main:app --reload   # open http://localhost:8000
pytest -q                       # non-AI tests (no API key needed)
```

Before you implement anything, dragging a card to In-Progress bounces it back to Items with a "⚙️ AI layer not implemented yet" comment. That's expected.

## How the pieces fit

```
UI (static/index.html)  ──drag to In-Progress──▶  POST /api/cards/{id}/move
                                                     │
                                                     ▼
                         app/worker.py  (background thread queue)
                                                     │  calls
                                                     ▼
                         app/ai/__init__.py :: process_card(card) -> Outcome(column, reason)   ← YOU
                                                     │
                         worker moves the card + posts the reason as a comment
UI polls /api/cards every 3s and shows the result.
```

Daily intake (`app/scheduler.py`) runs once a day after `DAILY_INTAKE_HOUR` (default 7):

1. Recurring cards from `recurring.json` (no AI, works now).
2. Free-form notes in `inbox/notes.txt` → cards via `app/ai/intake.py` (Topic 13, yours).

Use the **Run daily intake** button to trigger it manually.

## The stubs you'll fill (in study-guide order)

| Topic | File | What |
|---|---|---|
| 1 | `ai/__init__.py`, `prompts.py`, `tools.py`, `agent_loop.py`, `router.py` | Loop, first message, tools, routing |
| 2–3 | `ai/subagents.py` | Parallel subagents, structured failures |
| 4 | `ai/sessions.py` | Resume vs fresh-with-summary vs fork |
| 5 | `ai/hooks.py` | Pre/post tool hooks, hard rules |
| 6 | `ai/tools.py` | Real work tools, role scoping, forced `tool_choice` |
| 7 | `ai/mcp_server.py` | The board as an MCP server |
| 12 | `ai/prompts.py` | `SYSTEM_PROMPT` with explicit criteria + examples |
| 13 | `ai/intake.py`, `ai/validation.py` | Forced-tool extraction, validation-retry |
| 14 | `ai/batch.py` | Nightly digest via the Batch API |
| 15 | `ai/context.py` | Trimming, case-facts block |
| 16 | `ai/handoff.py` | Escalation triggers, structured handoff |
| 17 | `ai/metrics.py` | Acceptance by task type → earned auto-complete |

Useful `store` functions for the AI layer: `get_card`, `add_comment`, `save_result`, `save_transcript`, `load_transcript`, `card_exists`, `create_card`, `qa_decisions`.

To list what's left, run: `grep -rn "NotImplementedError" app/ai`
