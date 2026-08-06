import json
import sqlite3 
import db
import utils
import config

DB_FILE = db.DB_PATH
TABLE_NAME = "goalie_season_stats"
JSON_FILE = config.JSON_DATA_PATH / "goalie_season_stats.json"

SKATER_SEASON_SCHEMA = """

CREATE TABLE IF NOT EXISTS goalie_season_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    season TEXT NOT NULL,
    team_id INTEGER NOT NULL,
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ot_losses INTEGER DEFAULT 0,
    save_pct REAL DEFAULT 0.0,
    goals_against_avg REAL DEFAULT 0.0,
    shutouts INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,

    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);
"""

def create_table(conn: sqlite3.Connection) -> None:
    conn.execute(SKATER_SEASON_SCHEMA)
    conn.commit()


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


def insert_into_goalie_table(conn: sqlite3.Connection, rows:list) -> None:
    print(rows)
    cursor = conn.cursor()
    # cursor.execute("DELETE FROM skater_season_stats WHERE player_id = ?", (player_id,))

    cursor.executemany(
        """
        INSERT INTO goalie_season_stats (
            player_id, season, team_id, games_played, wins, losses, ot_losses, save_pct, goals_against_avg, shutouts, saves
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
        """,
    rows,
    )
    conn.commit()


def main():
    conn = db.create_connection(DB_FILE)
    create_table(conn) 
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
        rows = extract_rows(stats) 
        try:
            insert_into_goalie_table(conn, rows)
        except sqlite3.IntegrityError as exc:
            print("error" ,{exc})
    conn.close()


if __name__ == "__main__":
    main()
