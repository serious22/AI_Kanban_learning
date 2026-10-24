"""Daily intake: fills the Items column every morning.

Part 1 (implemented, no AI): recurring cards from recurring.json.
Part 2 (AI, yours): turns free-form notes in inbox/notes.txt into cards via
`app.ai.intake.extract_cards_from_notes` (study guide Topic 13). Skipped
automatically until you implement it.
"""
from __future__ import annotations
import json, logging, os, threading, time
from datetime import date, datetime
from pathlib import Path
from . import store

log = logging.getLogger("scheduler")
ROOT = Path(__file__).resolve().parent.parent
RECURRING = ROOT / "recurring.json"
INBOX = ROOT / "inbox" / "notes.txt"
DAILY_HOUR = int(os.environ.get("DAILY_INTAKE_HOUR", "7"))       # local time
_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def add_recurring(today: date) -> list[int]:
    if not RECURRING.exists():
        return []
    created = []
    for item in json.loads(RECURRING.read_text()):
        days = item.get("days", _DAYS)
        if _DAYS[today.weekday()] not in days:
            continue
        if store.card_exists(item["title"], since_days=1):
            continue
        c = store.create_card(item["title"], item.get("description", ""),
                              task_type=item.get("task_type"), labels=item.get("labels"), source="daily")
        created.append(c.id)
    return created


def add_from_notes() -> dict:
    """AI part (Topic 13). Reads inbox/notes.txt, creates cards, archives the file."""
    if not INBOX.exists() or not INBOX.read_text().strip():
        return {"status": "no notes"}
    from .ai.intake import extract_cards_from_notes
    try:
        cards = extract_cards_from_notes(INBOX.read_text())
    except NotImplementedError as e:
        return {"status": "skipped", "reason": str(e)}
    made = []
    for c in cards:
        if store.card_exists(c["title"], since_days=7):
            continue
        made.append(store.create_card(c["title"], c.get("description", ""),
                                      task_type=c.get("task_type"), source="notes").id)
    archive = INBOX.parent / "processed" / f"notes-{datetime.now():%Y%m%d-%H%M}.txt"
    archive.parent.mkdir(exist_ok=True)
    INBOX.rename(archive)
    INBOX.write_text("")
    return {"status": "ok", "created": made}


def run_daily_intake() -> dict:
    today = date.today()
    result = {"recurring": add_recurring(today), "notes": add_from_notes()}
    store.set_meta("last_intake", today.isoformat())
    log.info("daily intake: %s", result)
    return result


def _loop() -> None:
    while True:
        try:
            now = datetime.now()
            if now.hour >= DAILY_HOUR and store.get_meta("last_intake") != date.today().isoformat():
                run_daily_intake()
        except Exception:
            log.exception("daily intake failed")
        time.sleep(60)


def start() -> None:
    threading.Thread(target=_loop, daemon=True, name="daily-intake").start()
