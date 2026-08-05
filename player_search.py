import pandas as pd
import streamlit as st
import plotly.express as px

from db import load_players

def render():
    st.title("NHL Game Results") 
    df = load_players() 

    if df.empty:
        st.error("No Player data found.")
        return
    search = st.text_input("Search Player")

    if search:
        df = df[df["player_name"].str.contains(search, case=False)]

    player = st.selectbox(
        "Select Player",
        df["player_name"].unique()
    )

    player_df = df[df["player_name"] == player].iloc[0]

    left, right = st.columns([1,3])

    with left:

        if pd.notna(player_df["headshot_url"]):
            st.image(player_df["headshot_url"], width=180)
        else:
            st.image(
                "https://via.placeholder.com/180x220.png?text=No+Image",
                width=180
            )

    with right:

        st.subheader(player)

        st.write(f"**Team:** {player_df['team_name']}")
        st.write(f"**Position:** {player_df['position']}")
        st.write(f"**Jersey:** #{player_df['jersey_number']}")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Games", player_df["games_played"])
    c2.metric("Goals", player_df["goals"])
    c3.metric("Assists", player_df["assists"])
    c4.metric("Points", player_df["points"])

    c5, c6 = st.columns(2)

    c5.metric("Plus / Minus", player_df["plus_minus"])
    c6.metric("Penalty Minutes", player_df["penalty_min"])

    st.divider()

    chart_df = pd.DataFrame({
        "Statistic": [
            "Goals",
            "Assists",
            "Points",
            "Penalty Minutes"
        ],
        "Value": [
            player_df["goals"],
            player_df["assists"],
            player_df["points"],
            player_df["penalty_min"]
        ]
    })

    fig = px.bar(
        chart_df,
        x="Statistic",
        y="Value",
        color="Statistic",
        text="Value",
        title="Player Statistics"
    )

    st.plotly_chart(fig, use_container_width=True)