"""Prompts: Topic 1 (task prompt) and Topic 12 (system prompt)."""
from app.models import Card

# Topic 12: role + explicit open_questions criteria + 2-4 examples + output contract.
SYSTEM_PROMPT = ""


def build_task_prompt(card: Card) -> str:
    """Topic 1. Turn the card into the agent's FIRST user message.

    Must include: title, task_type, description and EVERY comment in order
    (author + timestamp), wrapped in XML tags. Tell Claude later comments win
    on conflict and that it must finish by calling finish_task exactly once.
    """
    raise NotImplementedError("Topic 1: build_task_prompt")
