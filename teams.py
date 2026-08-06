import sqlite3
import requests
import db

URL = "https://api-web.nhle.com/v1/standings/now"  # any JSON API endpoint
DB_FILE = "nhl.db"
TABLE_NAME = "teams"

TEAMS_SCHEMA = """
CREATE TABLE IF NOT EXISTS teams (
    team_id  INTEGER PRIMARY KEY AUTOINCREMENT,   -- NHL team id
    team_name  TEXT,
    team_abbrev     TEXT NOT NULL,
    conference_name     TEXT,
    division_name   TEXT,
    logo_url      TEXT
);
"""


def create_teams_table(conn: sqlite3.Connection) -> None:
    conn.execute(TEAMS_SCHEMA)
    conn.commit()


def fetch_teams(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises an error if the request failed
        return response.json()
    except requests.exceptions.RequestException as ex:
        print("API Error")
        return []


def extract_rows(payload: dict):
    rows = []
    print(payload)
    for team in payload.get("standings", []):
        team_abbrev = team.get("teamAbbrev", {}).get("default")
        team_name = team.get("teamName", {}).get("default")
        conference_name = team.get("conferenceName")
        division_name = team.get("divisionName")
        logo_url = team.get("teamLogo")

        rows.append(
            (
                team_abbrev,  # team_abbrev
                team_name,  # team_name
                conference_name,  # conference_name
                division_name,  # division_name
                logo_url,  # logo_url
            )
        )
    return rows


def save_to_sqlite(rows: list, conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    # for team in rows:
    cursor.executemany(
        """
        INSERT INTO teams ( 
            team_abbrev,
            team_name,
            conference_name,
            division_name,
            logo_url
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(team_id) DO UPDATE SET
            team_abbrev = excluded.team_abbrev,
            team_name = excluded.team_name,
            conference_name = excluded.conference_name,
            division_name = excluded.division_name,
            logo_url = excluded.logo_url
        """,
        rows,
    )

    conn.commit()


def main():
    print(f"Fetching {URL} ...")
    payload = fetch_teams(URL)
    teamData = extract_rows(payload)
    conn = db.create_connection(DB_FILE)
    print(len(teamData))
    create_teams_table(conn)

    save_to_sqlite(teamData, conn) 
if __name__ == "__main__":
    main()
