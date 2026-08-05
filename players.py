import json
import sqlite3
import requests
import utils

URL = (
    "https://api-web.nhle.com/v1/roster/{team_abbrev}/current"  # any JSON API endpoint
)
DB_FILE = "nhl.db"
TABLE_NAME = "players"


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY,
            team_id INTEGER NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            position TEXT,
            jersey_number INTEGER,
            birth_date TEXT,
            birth_country TEXT,
            height_cm INTEGER,
            weight_kg INTEGER,
            shoots_catches TEXT,
            headshot_url TEXT,
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
        """)
    conn.commit()


def create_connection(db_name: str) -> sqlite3.Connection:
    return sqlite3.connect(db_name)


def get_team_ids(conn: sqlite3.Connection):
    cur = conn.execute("SELECT team_abbrev FROM teams  ORDER BY team_id")
    return [row[0] for row in cur.fetchall()]


def fetch_players(team_abbrev: str) -> dict:
    try:
        response = requests.get(
            f"https://api-web.nhle.com/v1/roster/{team_abbrev}/current", timeout=10
        )
        response.raise_for_status()  # raises an error if the request failed
        return response.json()
    except requests.exceptions.RequestException as ex:
        print("API Error")
        return []


def get_team_map(conn):

    cursor = conn.cursor()
    cursor.execute("SELECT team_id, team_abbrev FROM teams")

    return {abbr: team_id for team_id, abbr in cursor.fetchall()}


def extract_rows(payload: dict, team_id: int):
    rows = []
    print(payload)
    for group in ("forwards", "defensemen", "goalies"):
        for player in payload.get(group, []):
            rows.append(
                (
                    player.get("id"),
                    team_id,
                    player.get("firstName", {}).get("default"),
                    player.get("lastName", {}).get("default"),
                    player.get("positionCode"),
                    player.get("sweaterNumber"),
                    player.get("birthDate"),
                    player.get("birthCountry"),
                    player.get("heightInCentimeters"),
                    player.get("weightInKilograms"),
                    player.get("shootsCatches"),
                    player.get("headshot"),
                )
            )
    return rows


def save_to_sqlite(conn: sqlite3.Connection, rows: list) -> None:
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO players ( player_id, team_id, first_name, last_name, position, jersey_number, birth_date, birth_country,
          height_cm,weight_kg,shoots_catches,headshot_url )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(player_id) DO UPDATE SET 
            player_id = excluded.player_id,
            team_id = excluded.team_id,
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            position = excluded.position,
            jersey_number = excluded.jersey_number,
            birth_date = excluded.birth_date,
            birth_country = excluded.birth_country,
            height_cm = excluded.height_cm,
            weight_kg = excluded.weight_kg,
            shoots_catches = excluded.shoots_catches,
            headshot_url = excluded.headshot_url
        """,
        rows,
    )
    conn.commit()


def main():
    conn = create_connection(DB_FILE)
    create_table(conn)
    # team_list = get_team_ids(conn)
    team_map = get_team_map(conn)

    for team_abbrev in team_map:
        payload = fetch_players(team_abbrev)
        if payload is None:
            continue
        team_id = team_map.get(team_abbrev)
        print(team_id)
        rows = extract_rows(payload, team_id)
        if not rows:
            print("No players found for {team}")
            continue
        try:
            save_to_sqlite(conn, rows)
        except sqlite3.IntegrityError as exc:
            print("error")
    conn.close()


if __name__ == "__main__":
    main()
