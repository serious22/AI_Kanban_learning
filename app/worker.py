"""Background worker: runs the AI layer when a card enters In-Progress.

Fully implemented. It calls `app.ai.process_card(card)` and moves the card to
whatever `Outcome.column` comes back. Until you implement the AI layer, cards
bounce back to Items with a "not implemented yet" comment.
"""
from __future__ import annotations
import logging, queue, threading
from . import store
from .models import COLUMNS, COLUMN_LABELS, Outcome

log = logging.getLogger("worker")
_q: "queue.Queue[int]" = queue.Queue()
_started = False


def enqueue(card_id: int) -> None:
    store.set_ai_status(card_id, "queued")
    _q.put(card_id)


def process(card_id: int) -> None:
    from . import ai                          # imported late so edits reload cleanly
    card = store.get_card(card_id)
    if card is None or card.column != "in_progress":
        return                                # moved away while queued
    store.set_ai_status(card_id, "running")
    try:
        outcome = ai.process_card(card)
    except NotImplementedError as e:
        store.add_comment(card_id, "system",
                          f"⚙️ AI layer not implemented yet ({e}). Card returned to Items.")
        store.move_card(card_id, "items", by="system")
        store.set_ai_status(card_id, "idle", str(e))
        return
    except Exception as e:                    # agent crashed → a human looks at it
        log.exception("agent crashed on card %s", card_id)
        store.add_comment(card_id, "system", f"❌ Agent crashed: {e!r}")
        store.move_card(card_id, "human_qa", by="system")
        store.set_ai_status(card_id, "error", repr(e))
        return

    if not isinstance(outcome, Outcome) or outcome.column not in COLUMNS or outcome.column == "in_progress":
        outcome = Outcome("human_qa", f"Invalid outcome from AI layer: {outcome!r}")
    store.move_card(card_id, outcome.column, by="AI")
    store.add_comment(card_id, "system", f"→ {COLUMN_LABELS[outcome.column]}: {outcome.reason}")
    store.set_ai_status(card_id, "idle", outcome.reason)


def _loop() -> None:
    while True:
        card_id = _q.get()
        try:
            process(card_id)
        except Exception:
            log.exception("worker loop error on card %s", card_id)
        finally:
            _q.task_done()


def start() -> None:
    """Start the worker thread and re-queue cards stranded in In-Progress (crash recovery)."""
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_loop, daemon=True, name="ai-worker").start()
    for c in store.list_cards():
        if c.column == "in_progress":
            enqueue(c.id)


def drain(timeout: float = 10.0) -> None:
    """Tests: wait until the queue is empty."""
    import time
    end = time.time() + timeout
    while _q.unfinished_tasks and time.time() < end:
        time.sleep(0.05)
