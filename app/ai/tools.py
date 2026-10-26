"""Tool schemas + execution: Topics 1, 5, 6."""
from app import store
from app.models import Card

# ── Topic 1: starter tools ────────────────────────────────────────────────
ADD_COMMENT: dict = {
    "name" : ""
    "description":""
    "input_schema":{"type": "object",
                   "properties": {"text": {"type": "string"}}, "required": ["text"]}
}      # name, description, input_schema {text}
FINISH_TASK: dict = {
    "name": "finish_task",
    "description": "Call exactly once when you've done all you can. Report facts, not confidence.",
    "type": "object",
    "properties": {
      "deliverable":    {"type": "string"},
      "steps_done":     {"type": "array", "items": {"type": "string"}},
      "open_questions": {"type": "array", "items": {"type": "string"},
                         "description": "Anything unresolved or assumed. Empty if none."},
      "needs_external_action": {"type": "boolean",
                         "description": "True if a human must send, pay, publish or approve"}
    },
    "required": ["deliverable", "steps_done", "open_questions", "needs_external_action"]

}      # deliverable, steps_done[], open_questions[], needs_external_action (NO confidence field)

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
    def make_tool_handler(card, state):
    def handle_tools(blocks):                                   # ②
        results = []
        for b in blocks:
            try:
                if b.name == "add_comment":
                    store.add_comment(card.id, "AI", b.input["text"])
                    out = "Comment posted."
                elif b.name == "finish_task":
                    state["result"] = b.input                   # ③
                    out = "Result recorded. You can stop now."
                else:
                    raise ValueError(f"Unknown tool: {b.name}")
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
            except Exception as e:                              # ④
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": f"Error: {e}", "is_error": True})
        return results
    return handle_tools


def make_basic_handler():
    """Topic 2. A card-less handler for subagents (search_web / read_url only)."""
    raise NotImplementedError("Topic 2: make_basic_handler")
