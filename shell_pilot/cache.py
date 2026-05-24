import sqlite3
import hashlib
import time
from pathlib import Path
from shell_pilot.config import CONFIG_DIR

DB_PATH = CONFIG_DIR / "cache.db"
TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

def _conn() -> sqlite3.Connection:
    CONFIG_DIR.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key       TEXT PRIMARY KEY,
            value     TEXT NOT NULL,
            created   INTEGER NOT NULL
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS failures (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            command   TEXT NOT NULL,
            exit_code TEXT NOT NULL,
            created   INTEGER NOT NULL
        )
    """)
    con.commit()
    return con

def _key(command: str, exit_code: str) -> str:
    raw = f"{command.strip()}:{exit_code}"
    return hashlib.sha256(raw.encode()).hexdigest()

def get(command: str, exit_code: str) -> str | None:
    k = _key(command, exit_code)
    with _conn() as con:
        row = con.execute(
            "SELECT value, created FROM cache WHERE key = ?", (k,)
        ).fetchone()
    if row is None:
        return None
    value, created = row
    if time.time() - created > TTL_SECONDS:
        _delete(k)
        return None
    return value

def set(command: str, exit_code: str, explanation: str) -> None:
    k = _key(command, exit_code)
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO cache (key, value, created) VALUES (?, ?, ?)",
            (k, explanation, int(time.time()))
        )

def _delete(key: str) -> None:
    with _conn() as con:
        con.execute("DELETE FROM cache WHERE key = ?", (key,))

def log_failure(command: str, exit_code: str) -> None:
    with _conn() as con:
        con.execute(
            "INSERT INTO failures (command, exit_code, created) VALUES (?, ?, ?)",
            (command.strip(), str(exit_code), int(time.time()))
        )

def top_failures(n: int = 10) -> list[tuple[str, int]]:
    with _conn() as con:
        rows = con.execute(
            "SELECT command, COUNT(*) as cnt FROM failures "
            "GROUP BY command ORDER BY cnt DESC LIMIT ?", (n,)
        ).fetchall()
    return [(cmd, cnt) for cmd, cnt in rows]

def clear() -> int:
    with _conn() as con:
        count = con.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
        con.execute("DELETE FROM cache")
        con.execute("DELETE FROM failures")
    return count
