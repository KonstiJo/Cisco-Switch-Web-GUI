import sqlite3
from datetime import datetime, timezone

DB_PATH = "switch_log.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS action_log (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            switch_ip TEXT NOT NULL,
            target    TEXT NOT NULL,
            action    TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_action(switch_ip: str, target: str, action: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO action_log (timestamp, switch_ip, target, action) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), switch_ip, target, action),
    )
    conn.commit()
    conn.close()


def get_logs(limit: int = 100) -> list:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT timestamp, switch_ip, target, action FROM action_log ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "switch_ip": r[1], "target": r[2], "action": r[3]}
        for r in rows
    ]
