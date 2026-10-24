"""Escalation + structured handoff: Topic 16."""
from app.models import Card

ASK_FIRST = ("check with me", "ask me first", "don't start until", "wait for me")


def needs_escalation_before_work(card: Card) -> str | None:
    """Topic 16. If Sid asked to be consulted first, return the reason (escalate BEFORE work)."""
    raise NotImplementedError("Topic 16: needs_escalation_before_work")


def no_progress(messages: list) -> bool:
    """Topic 16. True if the same tool error repeated 3 times in a row."""
    raise NotImplementedError("Topic 16: no_progress")


def build_handoff(card: Card, result: dict | None, reason: str) -> str:
    """Topic 16. Structured comment: reason, deliverable?, steps done, open questions,
    recommended next action."""
    raise NotImplementedError("Topic 16: build_handoff")
