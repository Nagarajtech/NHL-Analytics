import sqlite3
import config 
DB_PATH = config.PROJECT_ROOT / "data" / "nhl.db"

TEAMS_SCHEMA = """
CREATE TABLE IF NOT EXISTS teams (
    id            INTEGER PRIMARY KEY,   -- NHL team id
    franchise_id  INTEGER,
    full_name     TEXT NOT NULL,
    league_id     INTEGER,
    raw_tricode   TEXT,
    tri_code      TEXT,
    updated_at    TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def get_connection() -> sqlite3.Connection:
    """Open (and create if needed) the SQLite database file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def create_teams_table(conn: sqlite3.Connection) -> None:
    conn.execute(TEAMS_SCHEMA)
    conn.commit() 

 
 

 