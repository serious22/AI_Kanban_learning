"""Non-AI tests: the board works with the AI layer still stubbed out."""
import os, tempfile
os.environ["DISABLE_SCHEDULER"] = "1"
from fastapi.testclient import TestClient
from app import store, worker
from app.models import Outcome
import app.ai as ai
from app.main import app


def _client(tmp):
    store.init_db(os.path.join(tmp, "t.db"))
    return TestClient(app)


def test_create_comment_move_and_stub_bounce():
    with tempfile.TemporaryDirectory() as tmp, _client(tmp) as c:
        store.init_db(os.path.join(tmp, "t.db"))
        card = c.post("/api/cards", json={"title": "Research Apollo pricing"}).json()
        c.post(f"/api/cards/{card['id']}/comments", json={"text": "3 options, with sources"})
        c.post(f"/api/cards/{card['id']}/comments", json={"text": "under 200 words"})
        r = c.post(f"/api/cards/{card['id']}/move", json={"column": "in_progress"})
        assert r.status_code == 200
        worker.drain()
        got = store.get_card(card["id"])
        assert got.column == "items"                         # stub raised NotImplementedError
        assert any("not implemented" in m.text for m in got.comments)
        assert [m.author for m in got.comments][:2] == ["Sid", "Sid"]


def test_fake_ai_routes_card(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp, _client(tmp) as c:
        store.init_db(os.path.join(tmp, "t.db"))
        monkeypatch.setattr(ai, "process_card", lambda card: Outcome("human_qa", "Open questions: which case study?"))
        card = c.post("/api/cards", json={"title": "Draft email"}).json()
        c.post(f"/api/cards/{card['id']}/move", json={"column": "in_progress"})
        worker.drain()
        got = store.get_card(card["id"])
        assert got.column == "human_qa" and got.ai_status == "idle"
        # Sid accepts it -> logged as a QA decision (Topic 17 ground truth)
        c.post(f"/api/cards/{card['id']}/move", json={"column": "completed"})
        rows = store.qa_decisions()
        assert len(rows) == 1 and rows[0]["to_col"] == "completed"


def test_reorder_and_validation():
    with tempfile.TemporaryDirectory() as tmp, _client(tmp) as c:
        store.init_db(os.path.join(tmp, "t.db"))
        ids = [c.post("/api/cards", json={"title": f"c{i}"}).json()["id"] for i in range(3)]
        c.post(f"/api/cards/{ids[2]}/move", json={"column": "items", "index": 0})
        order = [x["id"] for x in c.get("/api/cards").json() if x["column"] == "items"]
        assert order == [ids[2], ids[0], ids[1]]
        assert c.post(f"/api/cards/{ids[0]}/move", json={"column": "nope"}).status_code == 422
        assert c.post("/api/cards", json={"title": "  "}).status_code == 422


def test_daily_intake_recurring_without_ai():
    from app import scheduler
    from datetime import date
    with tempfile.TemporaryDirectory() as tmp:
        store.init_db(os.path.join(tmp, "t.db"))
        monday = date(2026, 10, 26)
        made = scheduler.add_recurring(monday)
        assert len(made) == 2                                 # mon-fri item + monday item
        assert scheduler.add_recurring(monday) == []          # no duplicates same day
