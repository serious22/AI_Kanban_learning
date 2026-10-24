"""Sessions: Topic 4 (resume vs fork vs fresh start with a summary)."""
from datetime import timedelta
from app.models import Card

STALE_AFTER = timedelta(hours=24)
TIME_SENSITIVE_TYPES = {"research", "pricing", "news"}


def build_messages_for_run(card: Card) -> list:
    """Topic 4. No transcript -> fresh task prompt.
    Recent + not time-sensitive -> RESUME: old transcript + one user message with the
    comments added since store.load_transcript()'s timestamp.
    Stale -> FRESH: task prompt + summarize_transcript(old) with [re-verify] markers."""
    raise NotImplementedError("Topic 4: build_messages_for_run")


def summarize_transcript(messages: list) -> str:
    """Topic 4. Fact-preserving summary: decisions, deliverable, numbers/dates/names WITH
    sources, user constraints; mark volatile facts [re-verify]."""
    raise NotImplementedError("Topic 4: summarize_transcript")


def fork(card: Card, variants: list[str]) -> list[list]:
    """Topic 4. Copy the saved transcript once per variant + a different next message."""
    raise NotImplementedError("Topic 4: fork")
