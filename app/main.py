"""FastAPI app: REST API for the board + serves the UI. Fully implemented.

Run:  uvicorn app.main:app --reload     then open http://localhost:8000
"""
from __future__ import annotations
import logging, os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from . import store, worker, scheduler
from .models import COLUMNS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
STATIC = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.init_db()
    worker.start()
    if os.environ.get("DISABLE_SCHEDULER") != "1":
        scheduler.start()
    yield

app = FastAPI(title="AI Kanban", lifespan=lifespan)


class CardIn(BaseModel):
    title: str
    description: str = ""
    task_type: str | None = None
    labels: list[str] | None = None


class CardPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    task_type: str | None = None
    labels: list[str] | None = None


class CommentIn(BaseModel):
    text: str
    author: str = "Sid"


class MoveIn(BaseModel):
    column: str
    index: int | None = None        # drop position within the target column (0 = top)


def _card_or_404(card_id: int):
    c = store.get_card(card_id)
    if c is None:
        raise HTTPException(404, "card not found")
    return c


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/cards")
def list_cards():
    return [c.to_dict() for c in store.list_cards()]


@app.post("/api/cards", status_code=201)
def create_card(body: CardIn):
    if not body.title.strip():
        raise HTTPException(422, "title required")
    return store.create_card(body.title, body.description, body.task_type, body.labels).to_dict()


@app.patch("/api/cards/{card_id}")
def patch_card(card_id: int, body: CardPatch):
    _card_or_404(card_id)
    return store.update_card(card_id, title=body.title, description=body.description, task_type=body.task_type, labels=body.labels).to_dict()


@app.delete("/api/cards/{card_id}", status_code=204)
def delete_card(card_id: int):
    c = _card_or_404(card_id)
    if c.ai_status in ("queued", "running"):
        raise HTTPException(409, "AI is working on this card")
    store.delete_card(card_id)


@app.post("/api/cards/{card_id}/comments", status_code=201)
def add_comment(card_id: int, body: CommentIn):
    _card_or_404(card_id)
    if not body.text.strip():
        raise HTTPException(422, "empty comment")
    store.add_comment(card_id, body.author, body.text.strip())
    return store.get_card(card_id).to_dict()


@app.post("/api/cards/{card_id}/move")
def move_card(card_id: int, body: MoveIn):
    c = _card_or_404(card_id)
    if body.column not in COLUMNS:
        raise HTTPException(422, f"column must be one of {COLUMNS}")
    if c.ai_status in ("queued", "running") and body.column != c.column:
        raise HTTPException(409, "AI is working on this card; wait for it to finish")
    store.move_card(card_id, body.column, by="Sid", index=body.index)
    if body.column == "in_progress" and c.column != "in_progress":
        worker.enqueue(card_id)                    # ← the only place the AI gets triggered
    return store.get_card(card_id).to_dict()


@app.post("/api/intake/run")
def run_intake():
    return scheduler.run_daily_intake()
