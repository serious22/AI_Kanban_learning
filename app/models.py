"""Plain data types shared by the board and the AI layer."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime

COLUMNS = ["items", "in_progress", "human_qa", "completed"]
COLUMN_LABELS = {"items": "Items", "in_progress": "In-Progress",
                 "human_qa": "Human QA", "completed": "Completed"}


@dataclass
class Comment:
    id: int
    card_id: int
    author: str          # "Sid" | "AI" | "system"
    text: str
    created_at: datetime


@dataclass
class Card:
    id: int
    title: str
    description: str
    column: str
    task_type: str | None
    labels: list[str]
    ai_status: str       # "idle" | "queued" | "running" | "error"
    ai_reason: str | None
    source: str          # "manual" | "daily" | "notes" | "mcp"
    result: dict | None  # the agent's finish_task report (you save it via store.save_result)
    created_at: datetime
    updated_at: datetime
    comments: list[Comment] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("created_at", "updated_at"):
            d[k] = d[k].isoformat()
        for c in d["comments"]:
            c["created_at"] = c["created_at"].isoformat()
        return d


@dataclass
class Outcome:
    """What the AI layer returns to the worker. The worker moves the card."""
    column: str          # "human_qa" | "completed" (or "items" to give it back untouched)
    reason: str
