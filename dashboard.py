import pandas as pd
import streamlit as st
import plotly.express as px
from db import load_data


GOALS_QUERY = """
SELECT
    CONCAT(p.first_name,' ',p.last_name) AS player_name,
    t.team_name,
    SUM(gs.goals) AS goals
FROM players p
JOIN game_stats gs
    ON p.player_id = gs.player_id
JOIN teams t
    ON p.team_id = t.team_id
GROUP BY player_name, t.team_name
ORDER BY goals DESC
LIMIT 10;
"""

ASSISTS_QUERY = """
SELECT
    CONCAT(p.first_name,' ',p.last_name) AS player_name,
    t.team_name,
    SUM(gs.assists) AS assists
FROM players p
JOIN game_stats gs
    ON p.player_id = gs.player_id
JOIN teams t
    ON p.team_id = t.team_id
GROUP BY player_name, t.team_name
ORDER BY assists DESC
LIMIT 10;
"""

POINTS_QUERY = """
SELECT
    CONCAT(p.first_name,' ',p.last_name) AS player_name,
    t.team_name,
    SUM(gs.points) AS points
FROM players p
JOIN game_stats gs
    ON p.player_id = gs.player_id
JOIN teams t
    ON p.team_id = t.team_id
GROUP BY player_name, t.team_name
ORDER BY points DESC
LIMIT 10;
"""

PENALTY_QUERY = """
SELECT
    CONCAT(p.first_name,' ',p.last_name) AS player_name,
    t.team_name,
    SUM(gs.penalty_min) AS penalty_minutes
FROM players p
JOIN game_stats gs
    ON p.player_id = gs.player_id
JOIN teams t
    ON p.team_id = t.team_id
GROUP BY player_name, t.team_name
ORDER BY penalty_minutes DESC
LIMIT 10;
"""



def show_leaderboard(title, query, stat_column):

    df = load_data(query)

    st.subheader(title)

    if df.empty:
        st.warning("No data available.")
        return

    # Top Player Card
    top = df.iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric("Leader", top["player_name"])
    c2.metric("Team", top["team_name"])
    c3.metric(stat_column.replace("_", " ").title(), top[stat_column])

    st.dataframe(df, use_container_width=True)

    


def render():

    st.title("🏆 NHL Leaderboards")

    tab1, tab2 = st.tabs(
        [
            "🎯 Scoring",
            "🥊 Penalties", 
        ]
    )

    with tab1:

        show_leaderboard(
            "Top Goal Scorers",
            GOALS_QUERY,
            "goals",
        )

        st.divider()

        show_leaderboard(
            "Top Assist Leaders",
            ASSISTS_QUERY,
            "assists",
        )

        st.divider()

        show_leaderboard(
            "Top Point Leaders",
            POINTS_QUERY,
            "points",
        )

    with tab2:

        show_leaderboard(
            "Most Penalty Minutes",
            PENALTY_QUERY,
            "penalty_minutes",
        )