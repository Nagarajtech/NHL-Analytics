
import sqlite3
import requests
import utils
import db

URL = "https://api-web.nhle.com/v1/club-schedule-season/{team_abbrev}/now"
DB_FILE = db.DB_PATH
TABLE_NAME = "games"


GAMES_SCHEMA = """

CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY,
    season TEXT NOT NULL,
    game_type INTEGER NOT NULL,
    game_date DATE NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    game_state TEXT NOT NULL,
    venue_name TEXT,

    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);
"""


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute(GAMES_SCHEMA)
    conn.commit() 


def get_team_ids(conn: sqlite3.Connection):
    cur = conn.execute("SELECT team_abbrev FROM teams  ORDER BY team_id")
    return [row[0] for row in cur.fetchall()]


def fetch_games(team_abbrev: str) -> dict:
    try:
        response = requests.get(
            f"https://api-web.nhle.com/v1/club-schedule-season/{team_abbrev}/now",
            timeout=10,
        )
        response.raise_for_status()  # raises an error if the request failed
        return response.json()
    except requests.exceptions.RequestException as ex:
        print("API Error")
        return []


def extract_rows(payload: dict, team_map):
    rows = []
    for game in payload.get("games", []):
        home = game.get("homeTeam", {})
        away = game.get("awayTeam", {})

        home_team_abbrev = home.get("abbrev")
        away_team_abbrev = away.get("abbrev")
        print(f"Home Team - {game}")

        home_team_id = team_map.get(home_team_abbrev)
        away_team_id = team_map.get(away_team_abbrev)

        print(f"Home Team - {home_team_id}")

        rows.append(
            (
                game.get("id"),
                utils.format_season(game.get("season")),
                game.get("gameType"),
                game.get("gameDate"),
                home_team_id,
                away_team_id,
                home.get("score"),
                away.get("score"),
                game.get("gameState"),
                (game.get("venue") or {}).get("default"),
            )
        )
    return rows


def get_team_map(conn):

    cursor = conn.cursor()
    cursor.execute("SELECT team_id, team_abbrev FROM teams")

    return {abbr: team_id for team_id, abbr in cursor.fetchall()}


def save_to_sqlite(rows: list, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO games (game_id, season, game_type, game_date, home_team_id, away_team_id, home_score, away_score, game_state, venue_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(game_id) DO UPDATE SET
            season = excluded.season,
            game_type = excluded.game_type,
            game_date = excluded.game_date,
            home_team_id = excluded.home_team_id,
            away_team_id = excluded.away_team_id,
            home_score = excluded.home_score,
            away_score = excluded.away_score,
            game_state = excluded.game_state,
            venue_name = excluded.venue_name
        """,
        rows,
    )
    conn.commit()


    


def main():
    conn = db.create_connection(DB_FILE)
    create_table(conn)
    team_map = get_team_map(conn)
    for team_abbrev in sorted(team_map.keys()):
        payload = fetch_games(team_abbrev)
        if payload is None:
            continue
        rows = extract_rows(payload, team_map)
        if not rows:
            print(f"No games found for {team_abbrev}")
            continue
        try:
            save_to_sqlite(rows, conn)
        except sqlite3.IntegrityError as exc:
            print("error")
    conn.close()


if __name__ == "__main__":
    main()
