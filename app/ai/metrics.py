"""Earned autonomy from Sid's QA decisions: Topic 17."""

MIN_SAMPLES = 20
MIN_ACCEPT_RATE = 0.90


def qa_acceptance_by_type() -> dict[str, dict]:
    """Topic 17. Use store.qa_decisions() (Sid's moves out of Human QA).
    accepted = moved to completed; sent back = miss. Return {task_type: {n, accepted, rate}}."""
    raise NotImplementedError("Topic 17: qa_acceptance_by_type")


def can_auto_complete(task_type: str | None) -> bool:
    """Topic 17. True only with >= MIN_SAMPLES decisions and rate >= MIN_ACCEPT_RATE."""
    raise NotImplementedError("Topic 17: can_auto_complete")
