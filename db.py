
import os
import sqlite3

import pandas as pd
import streamlit as st

DB_PATH = os.environ.get("NHL_DB_PATH", "nhl.db")


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)



def load_teams() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM teams", conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


def load_standings() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM standings", conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


def load_players() -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM players", conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()



def load_full_standings() -> pd.DataFrame:
    conn = get_connection()
    try:
        query = """
            SELECT s.*, t.team_name, t.team_abbrev, t.conference_name,
                   t.division_name, t.logo_url
            FROM standings s
            JOIN teams t ON s.team_id = t.team_id
        """
        return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


def load_full_players() -> pd.DataFrame:
    conn = get_connection()
    try:
        query = """
            SELECT p.*, t.team_name, t.team_abbrev, t.logo_url,
                   t.conference_name, t.division_name
            FROM players p
            JOIN teams t ON p.team_id = t.team_id
        """
        return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def load_games() -> pd.DataFrame:
    conn = get_connection()
    try:
        query = """
            SELECT g.season as Season,g.game_date as GameDate,g.game_state as GameState,
            ht.team_name AS HomeTeam, 
            at.team_name AS AwayTeam
            FROM games g
            JOIN teams ht ON g.home_team_id = ht.team_id
            JOIN teams at ON g.away_team_id = at.team_id;
            """
        return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()


def load_players():
    conn = get_connection()

    query = """
    SELECT
    p.player_id,
    p.first_name,
    p.last_name,
    p.position,
    p.jersey_number,
    p.headshot_url,
    t.team_name,
    SUM(gs.goals) AS goals,
    SUM(gs.assists) AS assists,
    SUM(gs.points) AS points,
    SUM(gs.plus_minus) AS plus_minus,
    SUM(gs.penalty_min) AS penalty_min,
    SUM(gs.toi) AS total_toi,
    COUNT(gs.game_id) AS games_played
FROM players p
JOIN teams t
    ON p.team_id = t.team_id
JOIN game_stats gs
    ON p.player_id = gs.player_id
GROUP BY
    p.player_id,
    p.first_name,
    p.last_name,
    p.position,
    p.jersey_number,
    p.headshot_url,
    t.team_name
ORDER BY p.last_name;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df["player_name"] = df["first_name"] + " " + df["last_name"]

    return df

def load_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

