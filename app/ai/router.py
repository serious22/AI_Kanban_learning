"""Code decides the column, never the model. Topics 1, 5, 16, 17."""
from app.models import Card, Outcome


def route_card(card: Card, result: dict | None) -> Outcome:
    """Topic 1: no result -> human_qa · open_questions -> human_qa ·
    needs_external_action -> human_qa · else completed.
    Topic 17: final branch only auto-completes if metrics.can_auto_complete(card.task_type).
    Topic 16: post handoff.build_handoff(...) as a comment whenever routing to human_qa.
    """
    raise NotImplementedError("Topic 1: route_card")
