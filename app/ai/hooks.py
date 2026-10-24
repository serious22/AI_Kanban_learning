"""Rules in code: Topic 5 (PreToolUse / PostToolUse equivalents)."""
from dataclasses import dataclass
from app.models import Card


@dataclass
class HookDecision:
    allow: bool
    reason: str = ""


def card_word_limit(card: Card) -> int | None:
    """Topic 5. Parse a limit like 'under 200 words' from Sid's comments/description."""
    raise NotImplementedError("Topic 5: card_word_limit")


def card_requires_sources(card: Card) -> bool:
    """Topic 13 helper. True if the card/comments ask for sources/citations."""
    raise NotImplementedError("Topic 13: card_requires_sources")


def pre_tool_use(card: Card, name: str, tool_input: dict, state: dict) -> HookDecision:
    """Topic 5. BEFORE a tool runs: block send_email unless 'auto-send-ok' in card.labels;
    block finish_task over the word limit; prerequisite gates. Deny with an actionable reason."""
    raise NotImplementedError("Topic 5: pre_tool_use")


def post_tool_use(card: Card, name: str, output: str) -> str:
    """Topic 5. AFTER a tool runs: normalise/trim output (context.trim_tool_output for read_url)."""
    raise NotImplementedError("Topic 5: post_tool_use")
