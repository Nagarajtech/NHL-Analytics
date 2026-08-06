import json
import sqlite3 
import db
import config


DB_FILE = db.DB_PATH
TABLE_NAME = "game_stats"
JSON_FILE = config.JSON_DATA_PATH / "game_stats.json"

GAMES_STATS_SCHEMA = """
CREATE TABLE IF NOT EXISTS game_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    shots_on_goal INTEGER DEFAULT 0,
    penalty_min INTEGER DEFAULT 0,
    toi TEXT,    -- Time on Ice (e.g., "18:45")
    plus_minus INTEGER DEFAULT 0,

    UNIQUE (game_id),

    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id) 
);
"""



def create_table(conn: sqlite3.Connection) -> None:
    conn.execute(GAMES_STATS_SCHEMA)
    conn.commit()


def get_team_map(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT team_id, team_abbrev FROM teams")

    return {abbr: team_id for team_id, abbr in cursor.fetchall()}


def get_game_ids(conn: sqlite3.Connection):
    cur = conn.execute("SELECT game_id FROM games  ORDER BY game_id")
    return [row[0] for row in cur.fetchall()]


def fetch_games_stats(game_id: str, stats: any) -> dict:
    game_stats = [stat for stat in stats if stat["game_id"] == game_id]
    return game_stats


def extract_rows(payload: dict):
    rows = []
    for stat in payload:
        rows.append(
            (
                # stat["stat_id"],
                stat["game_id"],
                stat["player_id"],
                stat["team_id"],
                stat.get("goals", 0),
                stat.get("assists", 0),
                stat.get("points", 0),
                stat.get("shots_on_goal", 0),
                stat.get("penalty_min", 0),
                stat.get("toi"),
                stat.get("plus_minus", 0),
            )
        )
    return rows


def insert_game_stats_table(rows: list, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO game_stats (
            game_id,
            player_id,
            team_id,
            goals,
            assists,
            points,
            shots_on_goal,
            penalty_min,
            toi,
            plus_minus
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(game_id) DO UPDATE SET
            team_id = excluded.team_id,
            player_id = excluded.player_id,
            goals = excluded.goals,
            assists = excluded.assists,
            points = excluded.points,
            shots_on_goal = excluded.shots_on_goal,
            penalty_min = excluded.penalty_min,
            toi = excluded.toi,
            plus_minus = excluded.plus_minus;
        """,
    rows,
    )

    conn.commit()


def main():
    conn = db.create_connection(DB_FILE)
    create_table(conn)
    #game_list = get_game_ids(conn)
    # Load JSON
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
        #for game_id in game_list:
        # payload = fetch_games_stats(stats)
        # print(payload) 
        rows = extract_rows(stats)
        if rows:
            print(f"Games found") 
        try:
            insert_game_stats_table(rows, conn)
        except sqlite3.IntegrityError as exc:
            print("error")
    conn.close()


if __name__ == "__main__":
    main()
