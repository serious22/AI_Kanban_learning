"""AI layer: YOU build this while studying CCAR-F_Study_Guide_Kanban.html.

Contract with the rest of the app (don't change it):
    the worker calls  process_card(card)  and expects an  Outcome(column, reason).
Everything outside app/ai/ already works.
"""
from app.models import Card, Outcome


def process_card(card: Card) -> Outcome:
    """Topic 1 (later Topic 4 + Topic 16).

    v1 (Topic 1):
        from .agent_loop import run_task
        return run_task(card)

    v2 (Topic 4): build messages with sessions.build_messages_for_run(card)
                  and pass them into run_task(card, messages=...).
    v3 (Topic 16): if handoff.needs_escalation_before_work(card) returns a reason,
                   return Outcome("human_qa", reason) BEFORE running anything.
    """
    raise NotImplementedError("Topic 1: implement process_card in app/ai/__init__.py")
