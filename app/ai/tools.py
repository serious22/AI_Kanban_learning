"""Tool schemas + execution: Topics 1, 5, 6."""
from app import store
from app.models import Card

# ── Topic 1: starter tools ────────────────────────────────────────────────
ADD_COMMENT: dict = {}      # name, description, input_schema {text}
FINISH_TASK: dict = {}      # deliverable, steps_done[], open_questions[], needs_external_action (NO confidence field)

# ── Topic 6: work tools (sharp descriptions: what / returns / when-vs-alternative / limits)
SEARCH_WEB: dict = {}
READ_URL: dict = {}
SEARCH_PAST_CARDS: dict = {}

TOOLS: list[dict] = []      # Topic 1: [ADD_COMMENT, FINISH_TASK]; Topic 6: role-scoped lists


def execute_tool(card: Card, block, state: dict) -> str:
    """Topic 1. Run ONE tool_use block and return its output string.

    - add_comment  -> store.add_comment(card.id, "AI", text)
    - finish_task  -> validate (Topic 13), then state["result"] = block.input and
                      store.save_result(card.id, block.input)
    - unknown name -> raise ValueError
    """
    raise NotImplementedError("Topic 1: execute_tool")


def make_tool_handler(card: Card, state: dict):
    """Topic 1 (+ Topic 5 hooks). Return handle_tools(blocks) -> list[tool_result dict].

    For each block: pre_tool_use gate (Topic 5) -> execute_tool -> post_tool_use.
    Every tool_use gets exactly one tool_result with the matching tool_use_id.
    Exceptions become {"is_error": True, "content": "Error: ..."}.
    """
    raise NotImplementedError("Topic 1: make_tool_handler")


def make_basic_handler():
    """Topic 2. A card-less handler for subagents (search_web / read_url only)."""
    raise NotImplementedError("Topic 2: make_basic_handler")
