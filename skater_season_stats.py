import json
import sqlite3
import requests
import utils

DB_FILE = "nhl.db"
TABLE_NAME = "skater_season_stats"
JSON_FILE = "skater_season_stats.json"

SKATER_SEASON_SCHEMA = """

CREATE TABLE IF NOT Exists skater_season_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    season TEXT NOT NULL,
    team_id INTEGER NOT NULL,
    games_played INTEGER DEFAULT 0,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    plus_minus INTEGER DEFAULT 0,
    penalty_min INTEGER DEFAULT 0,
    shots INTEGER DEFAULT 0,
    avg_toi TEXT,

    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);
"""


def create_connection(db_name: str) -> sqlite3.Connection:
    return sqlite3.connect(db_name)


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute(SKATER_SEASON_SCHEMA)
    conn.commit()


def get_skater_player_ids(conn: sqlite3.Connection):
    cur = conn.execute(
        "SELECT player_id FROM players WHERE position != 'G' ORDER BY player_id"
    )
    return [row[0] for row in cur.fetchall()]


def build_team_name_lookup(conn: sqlite3.Connection) -> dict:
    cur = conn.execute("SELECT team_id, team_name FROM teams")
    return {name: team_id for team_id, name in cur.fetchall() if name}


def extract_rows(payload: dict):
    rows = []
    for stat in payload:
        rows.append(
            (
                stat["player_id"],
                utils.format_season(stat["season"]),
                stat["team_id"],
                stat.get("gamesPlayed", 0) or 0,
                stat.get("wins", 0) or 0,
                stat.get("losses", 0) or 0,
                stat.get("otLosses", 0) or 0,
                stat.get("savePctg", 0) or 0,
                stat.get("goalsAgainstAvg", 0) or 0,
                stat.get("shutouts", 0) or 0,
                stat.get("saves", 0) or 0,
            )
        )

    return rows


def insert_into_skater_table(conn: sqlite3.Connection, rows) -> None:
    cursor = conn.cursor()

    cursor.executemany(
        """
            INSERT INTO skater_season_stats ( player_id, season, team_id, games_played, goals, assists,
                points, plus_minus, penalty_min, shots, avg_toi
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
            """,
        rows,
    )
    conn.commit()


def main():
    conn = create_connection(DB_FILE)
    create_table(conn)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
        rows = extract_rows(stats)
        try:
            insert_into_skater_table(conn, rows)
        except sqlite3.IntegrityError as exc:
            print("error", {exc})
    conn.close()


if __name__ == "__main__":
    main()
