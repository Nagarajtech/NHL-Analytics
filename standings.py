import json
import sqlite3
import requests
import utils
import db

URL = "https://api-web.nhle.com/v1/standings/now"  # any JSON API endpoint
DB_FILE = db.DB_PATH

STANDINGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS standings (
    standing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    season TEXT NOT NULL,
    games_played INTEGER NOT NULL,
    wins INTEGER NOT NULL,
    losses INTEGER NOT NULL,
    ot_losses INTEGER NOT NULL,
    points INTEGER NOT NULL,
    goals_for INTEGER NOT NULL,
    goals_against INTEGER NOT NULL,
    home_wins INTEGER NOT NULL,
    away_wins INTEGER NOT NULL,
    streak_type TEXT,
    streak_count INTEGER NOT NULL,

    UNIQUE (team_id, season),

    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);
"""


def create_standings_table(conn: sqlite3.Connection) -> None:
    conn.execute(STANDINGS_SCHEMA)
    conn.commit()


def fetch_standings(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises an error if the request failed
        return response.json()
    except requests.exceptions.RequestException as ex:
        print("API Error")
        return []


def get_team_map(conn):
    cursor = conn.cursor()

    cursor.execute(""" SELECT team_abbrev, team_id FROM teams """)

    return dict(cursor.fetchall())


def extract_rows(payload: dict, team_map):
    rows = []
    for team in payload.get("standings", []):
        team_abbrev = team.get("teamAbbrev", {}).get("default")
        season = utils.format_season(team.get("seasonId"))
        team_id = team_map.get(team_abbrev)
        rows.append(
            (
                team_id,
                season,
                team.get("gamesPlayed"),
                team.get("wins"),
                team.get("losses"),
                team.get("otLosses"),
                team.get("points"),
                team.get("goalFor"),
                team.get("goalAgainst"),
                team.get("homeWins"),
                team.get("roadWins"),
                team.get("streakCode"),
                team.get("streakCount"),
            )
        )
    return rows



def save_to_sqlite(rows: list, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    print(rows)
    cursor.executemany(
        """
        INSERT INTO standings (
        team_id,
        season,
        games_played,
        wins,
        losses,
        ot_losses,
        points,
        goals_for,
        goals_against,
        home_wins,
        away_wins,
        streak_type,
        streak_count
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(team_id, season) DO UPDATE SET
        games_played = excluded.games_played,
        wins = excluded.wins,
        losses = excluded.losses,
        ot_losses = excluded.ot_losses,
        points = excluded.points,
        goals_for = excluded.goals_for,
        goals_against = excluded.goals_against,
        home_wins = excluded.home_wins,
        away_wins = excluded.away_wins,
        streak_type = excluded.streak_type,
        streak_count = excluded.streak_count;
    """,
        rows,
    )

    conn.commit()


def main():

    conn = db.create_connection(DB_FILE)
    create_standings_table(conn)

    team_map = get_team_map(conn)
    payload = fetch_standings(URL)
    standingsData = extract_rows(payload, team_map)
    print(len(standingsData))

    save_to_sqlite(standingsData, conn)
    conn.close()


if __name__ == "__main__":
    main()
