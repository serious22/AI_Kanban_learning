"""Daily AI intake: notes -> cards. Topic 13 (forced tool + schema), Topic 3 (fixed pipeline)."""

# Topic 13: tool whose input_schema is {"cards": [{title, description, task_type enum
# (+ "other"/"unclear"), type_detail|null, due_date|null, person|null}]}
RECORD_CARDS: dict = {}


def extract_cards_from_notes(notes: str) -> list[dict]:
    """Topic 13. ONE call with tool_choice={"type":"tool","name":"record_cards"};
    return block.input["cards"]. Called by app/scheduler.py every morning."""
    raise NotImplementedError("Topic 13: extract_cards_from_notes")
