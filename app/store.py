"""SQLite persistence. Fully implemented. The AI layer may call any function here."""
from __future__ import annotations
import json, os, sqlite3, threading
from datetime import datetime, timedelta
from pathlib import Path
from .models import Card, Comment, COLUMNS

_DB_PATH = os.environ.get("KANBAN_DB", str(Path(__file__).resolve().parent.parent / "data" / "kanban.db"))
_lock = threading.RLock()
_conn: sqlite3.Connection | None = None


def _now() -> datetime:
    return datetime.utcnow()


def _db() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        Path(_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
    return _conn


def init_db(path: str | None = None) -> None:
    """Create tables. Pass a path (tests) to use a different database file."""
    global _conn, _DB_PATH
    with _lock:
        if path:
            _DB_PATH, _conn = path, None
        _db().executescript("""
        CREATE TABLE IF NOT EXISTS cards(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, description TEXT DEFAULT '',
            col TEXT NOT NULL DEFAULT 'items', position REAL NOT NULL DEFAULT 0,
            task_type TEXT, labels TEXT DEFAULT '[]',
            ai_status TEXT DEFAULT 'idle', ai_reason TEXT,
            source TEXT DEFAULT 'manual', result TEXT,
            transcript TEXT, transcript_updated_at TEXT,
            created_at TEXT, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER,
            author TEXT, text TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER,
            from_col TEXT, to_col TEXT, by TEXT, at TEXT);
        CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
        """)
        _db().commit()


# ── reading ────────────────────────────────────────────────────────────────
def _row_to_card(r, comments) -> Card:
    return Card(
        id=r["id"], title=r["title"], description=r["description"] or "", column=r["col"],
        task_type=r["task_type"], labels=json.loads(r["labels"] or "[]"),
        ai_status=r["ai_status"], ai_reason=r["ai_reason"], source=r["source"],
        result=json.loads(r["result"]) if r["result"] else None,
        created_at=datetime.fromisoformat(r["created_at"]),
        updated_at=datetime.fromisoformat(r["updated_at"]),
        comments=comments)


def _comments_for(card_ids: list[int]) -> dict[int, list[Comment]]:
    out: dict[int, list[Comment]] = {i: [] for i in card_ids}
    if not card_ids:
        return out
    q = f"SELECT * FROM comments WHERE card_id IN ({','.join('?' * len(card_ids))}) ORDER BY id"
    for r in _db().execute(q, card_ids):
        out[r["card_id"]].append(Comment(r["id"], r["card_id"], r["author"], r["text"],
                                         datetime.fromisoformat(r["created_at"])))
    return out


def list_cards() -> list[Card]:
    with _lock:
        rows = _db().execute("SELECT * FROM cards ORDER BY col, position, id").fetchall()
        cm = _comments_for([r["id"] for r in rows])
        return [_row_to_card(r, cm[r["id"]]) for r in rows]


def get_card(card_id: int) -> Card | None:
    with _lock:
        r = _db().execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        return _row_to_card(r, _comments_for([card_id])[card_id]) if r else None


def card_exists(title: str, since_days: int | None = None) -> bool:
    """True if a card with this exact title (case-insensitive) exists (optionally recently)."""
    with _lock:
        q, args = "SELECT 1 FROM cards WHERE lower(title)=lower(?)", [title.strip()]
        if since_days is not None:
            q += " AND created_at >= ?"
            args.append((_now() - timedelta(days=since_days)).isoformat())
        return _db().execute(q, args).fetchone() is not None


# ── writing ────────────────────────────────────────────────────────────────
def create_card(title: str, description: str = "", task_type: str | None = None,
                labels: list[str] | None = None, source: str = "manual", column: str = "items") -> Card:
    assert column in COLUMNS
    with _lock:
        now = _now().isoformat()
        pos = (_db().execute("SELECT COALESCE(MAX(position),0)+1 FROM cards WHERE col=?", (column,)).fetchone()[0])
        cur = _db().execute(
            "INSERT INTO cards(title,description,col,position,task_type,labels,source,created_at,updated_at)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (title.strip(), description, column, pos, task_type, json.dumps(labels or []), source, now, now))
        _db().commit()
        return get_card(cur.lastrowid)


def update_card(card_id: int, **fields) -> Card | None:
    allowed = {"title", "description", "task_type", "labels"}
    sets, args = [], []
    for k, v in fields.items():
        if k in allowed and v is not None:
            sets.append(f"{k}=?")
            args.append(json.dumps(v) if k == "labels" else v)
    with _lock:
        if sets:
            _db().execute(f"UPDATE cards SET {', '.join(sets)}, updated_at=? WHERE id=?",
                          (*args, _now().isoformat(), card_id))
            _db().commit()
        return get_card(card_id)


def delete_card(card_id: int) -> None:
    with _lock:
        _db().execute("DELETE FROM comments WHERE card_id=?", (card_id,))
        _db().execute("DELETE FROM cards WHERE id=?", (card_id,))
        _db().commit()


def add_comment(card_id: int, author: str, text: str) -> Comment:
    with _lock:
        now = _now()
        cur = _db().execute("INSERT INTO comments(card_id,author,text,created_at) VALUES(?,?,?,?)",
                            (card_id, author, text, now.isoformat()))
        _db().execute("UPDATE cards SET updated_at=? WHERE id=?", (now.isoformat(), card_id))
        _db().commit()
        return Comment(cur.lastrowid, card_id, author, text, now)


def move_card(card_id: int, column: str, by: str = "Sid", index: int | None = None) -> Card | None:
    """Move a card (optionally to a slot in the column) and log the move in `events`.
    Topic 17 uses Sid's moves out of Human QA as ground truth."""
    assert column in COLUMNS, column
    with _lock:
        r = _db().execute("SELECT col FROM cards WHERE id=?", (card_id,)).fetchone()
        if not r:
            return None
        now = _now().isoformat()
        ids = [x["id"] for x in _db().execute(
            "SELECT id FROM cards WHERE col=? AND id!=? ORDER BY position, id", (column, card_id))]
        ids.insert(len(ids) if index is None else max(0, min(index, len(ids))), card_id)
        _db().execute("UPDATE cards SET col=?, updated_at=? WHERE id=?", (column, now, card_id))
        for pos, cid in enumerate(ids, 1):
            _db().execute("UPDATE cards SET position=? WHERE id=?", (pos, cid))
        if r["col"] != column:
            _db().execute("INSERT INTO events(card_id,from_col,to_col,by,at) VALUES(?,?,?,?,?)",
                          (card_id, r["col"], column, by, now))
        _db().commit()
        return get_card(card_id)


def set_ai_status(card_id: int, status: str, reason: str | None = None) -> None:
    with _lock:
        _db().execute("UPDATE cards SET ai_status=?, ai_reason=COALESCE(?, ai_reason) WHERE id=?",
                      (status, reason, card_id))
        _db().commit()


def save_result(card_id: int, result: dict | None) -> None:
    """Store the agent's finish_task report on the card (shown in the UI drawer)."""
    with _lock:
        _db().execute("UPDATE cards SET result=? WHERE id=?",
                      (json.dumps(result) if result is not None else None, card_id))
        _db().commit()


def save_transcript(card_id: int, messages: list) -> None:
    """Topic 4: persist the agent's messages array (must be JSON-serialisable dicts)."""
    with _lock:
        _db().execute("UPDATE cards SET transcript=?, transcript_updated_at=? WHERE id=?",
                      (json.dumps(messages), _now().isoformat(), card_id))
        _db().commit()


def load_transcript(card_id: int) -> tuple[list | None, datetime | None]:
    with _lock:
        r = _db().execute("SELECT transcript, transcript_updated_at FROM cards WHERE id=?", (card_id,)).fetchone()
        if not r or not r["transcript"]:
            return None, None
        return json.loads(r["transcript"]), datetime.fromisoformat(r["transcript_updated_at"])


def qa_decisions() -> list[sqlite3.Row]:
    """Topic 17: Sid's moves OUT of Human QA → rows with task_type, to_col, at."""
    with _lock:
        return _db().execute(
            "SELECT e.card_id, COALESCE(c.task_type,'general') AS task_type, e.to_col, e.at "
            "FROM events e JOIN cards c ON c.id=e.card_id "
            "WHERE e.from_col='human_qa' AND e.by='Sid' ORDER BY e.at").fetchall()


def get_meta(k: str) -> str | None:
    with _lock:
        r = _db().execute("SELECT v FROM meta WHERE k=?", (k,)).fetchone()
        return r["v"] if r else None


def set_meta(k: str, v: str) -> None:
    with _lock:
        _db().execute("INSERT INTO meta(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, v))
        _db().commit()
