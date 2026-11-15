"""What every stack answers, so the stacks differ only by the layers that serve it."""

from __future__ import annotations

import random
import sqlite3
import threading
from pathlib import Path

from pydantic import BaseModel

HERE = Path(__file__).parent
TEXT = b"Hello, World!"
PAYLOAD = {"message": "Hello, World!"}
DB_PATH = HERE / "bench.sqlite3"
ROWS = 10_000
_local = threading.local()


class Item(BaseModel):
    """The body of the validation scenario."""

    name: str
    price: float
    tags: list[str] = []


def create_db() -> None:
    """Write the table the query scenario reads, once per run."""
    with sqlite3.connect(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS world (id INTEGER PRIMARY KEY, n INTEGER)")
        db.execute("DELETE FROM world")
        db.executemany("INSERT INTO world VALUES (?, ?)", ((i, i * 7) for i in range(1, ROWS + 1)))


def query_row() -> dict[str, int]:
    """One row by a random id, on a connection kept per thread."""
    db = getattr(_local, "db", None)
    if db is None:
        db = _local.db = sqlite3.connect(DB_PATH, check_same_thread=False)
    row_id = random.randint(1, ROWS)
    n = db.execute("SELECT n FROM world WHERE id = ?", (row_id,)).fetchone()[0]
    return {"id": row_id, "n": n}
