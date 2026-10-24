"""Context hygiene: Topic 15."""
from app.models import Card


def trim_tool_output(name: str, text: str, max_chars: int = 4000) -> str:
    """Topic 15. Keep the relevant part; mark what was cut."""
    raise NotImplementedError("Topic 15: trim_tool_output")


def case_facts_block(card: Card) -> str:
    """Topic 15. <case_facts> with the task + Sid's comments VERBATIM."""
    raise NotImplementedError("Topic 15: case_facts_block")


def with_case_facts(messages: list, card: Card) -> list:
    """Topic 15. Return a copy of messages with case facts appended to the latest user
    message (end of context = strongest attention). Don't mutate the saved transcript."""
    raise NotImplementedError("Topic 15: with_case_facts")
