import pandas as pd
import streamlit as st

from db import load_games


def render():
    st.title("NHL Game Results") 
    games_df = load_games()
    games_df["GameDate"] = pd.to_datetime(games_df["GameDate"]) 

    if games_df.empty:
        st.error("No game data found.")
        return

    team_list = sorted(list(
        set(games_df["HomeTeam"]).union(set(games_df["AwayTeam"]))
        ))
    col1, col2, col3 = st.columns(3)

    with col1:
        team = st.selectbox("Select Team", ["All"] + team_list)

    with col2:
        status = st.selectbox(
            "Game Status",
            ["All", "Final", "Upcoming"]
        )

    with col3:
        selected_date = st.date_input(
            "Select Date", value=games_df["GameDate"].min()
        )

    filtered = games_df.copy()

    if team != "All":
        filtered = filtered[
            (filtered["HomeTeam"] == team) |
            (filtered["AwayTeam"] == team)
        ]

    if status != "All":
        filtered = filtered[
            filtered["GameState"] == status
        ]

    filtered = filtered[
        filtered["GameDate"].dt.date >= selected_date
    ]
    st.dataframe(filtered,use_container_width=True)
