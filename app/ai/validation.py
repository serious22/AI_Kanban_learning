"""Semantic validation for finish_task: Topic 13."""
from app.models import Card


def validate_finish(card: Card, result: dict) -> list[str]:
    """Topic 13. Return a list of SPECIFIC error strings (empty = valid):
    empty deliverable, over the word limit, sources required but none cited, ...
    The caller retries with these errors appended (max 2), then flags via open_questions."""
    raise NotImplementedError("Topic 13: validate_finish")
