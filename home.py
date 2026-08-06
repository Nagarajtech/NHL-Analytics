import pandas as pd
import plotly.express as px
import streamlit as st

from db import load_full_players, load_full_standings, load_teams


def render():
    st.title("NHL League Dashboard")

    teams_df = load_teams()
    standings_df = load_full_standings()
    players_df = load_full_players()

    if standings_df.empty or teams_df.empty:
        st.warning(
            "No data found yet. Run load_nhl_teams.py, load_nhl_standings.py, "
            "and load_nhl_players.py to populate the database first."
        )
        return

    latest_season = sorted(standings_df["season"].unique())[-1]
    season_df = standings_df[standings_df["season"] == latest_season]

    total_teams = teams_df["team_id"].nunique()
    total_players = players_df["player_id"].nunique() if not players_df.empty else 0
    total_games = int(season_df["games_played"].sum() // 2)
    total_goals = int(season_df["goals_for"].sum())

    st.caption(f"Season: {latest_season}")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.metric("Teams", total_teams)
    with c2:
        with st.container(border=True):
            st.metric("Players", total_players)
    with c3:
        with st.container(border=True):
            st.metric("Games Played", total_games)
    with c4:
        with st.container(border=True):
            st.metric("Goals Scored", total_goals)

    st.divider()
    st.subheader("League Highlights")

    league_leader = season_df.sort_values("points", ascending=False).iloc[0]
    best_offense = season_df.sort_values("goals_for", ascending=False).iloc[0]
    best_defense = season_df.sort_values("goals_against", ascending=True).iloc[0]

    h1, h2, h3 = st.columns(3)
    with h1:
        with st.container(border=True):
            if league_leader.get("logo_url"):
                st.image(league_leader["logo_url"], width=56)
            st.caption("League Leader (Points)")
            st.markdown(f"**{league_leader['team_name']}**")
            st.markdown(f"{int(league_leader['points'])} pts")
    with h2:
        with st.container(border=True):
            if best_offense.get("logo_url"):
                st.image(best_offense["logo_url"], width=56)
            st.caption("Best Offense")
            st.markdown(f"**{best_offense['team_name']}**")
            st.markdown(f"{int(best_offense['goals_for'])} goals for")
    with h3:
        with st.container(border=True):
            if best_defense.get("logo_url"):
                st.image(best_defense["logo_url"], width=56)
            st.caption("Best Defense")
            st.markdown(f"**{best_defense['team_name']}**")
            st.markdown(f"{int(best_defense['goals_against'])} goals against")

    if not players_df.empty:
        st.divider()
        st.subheader("Roster Fun Facts")

        pdf = players_df.copy()
        pdf["birth_date_parsed"] = pd.to_datetime(pdf["birth_date"], errors="coerce")

        p1, p2, p3 = st.columns(3)
        with p1:
            with st.container(border=True):
                tallest = pdf.sort_values("height_cm", ascending=False).iloc[0]
                st.metric(
                    "Tallest Player",
                    f"{tallest['first_name']} {tallest['last_name']}",
                    f"{tallest['height_cm']} cm · {tallest['team_abbrev']}",
                )
        with p2:
            with st.container(border=True):
                youngest = pdf.sort_values("birth_date_parsed", ascending=False).dropna(
                    subset=["birth_date_parsed"]
                ).iloc[0]
                st.metric(
                    "Youngest Player",
                    f"{youngest['first_name']} {youngest['last_name']}",
                    f"{youngest['team_abbrev']}",
                )
        with p3:
            with st.container(border=True):
                top_country = pdf["birth_country"].value_counts().idxmax()
                top_country_count = pdf["birth_country"].value_counts().max()
                st.metric("Most Common Birth Country", top_country, f"{top_country_count} players")

    st.divider()
    st.subheader("Top 10 Teams by Points")
    top10 = season_df.sort_values("points", ascending=False).head(10)
    fig = px.bar(
        top10,
        x="team_abbrev",
        y="points",
        color="conference_name",
        text="points",
        hover_data={"team_name": True, "wins": True, "losses": True, "team_abbrev": False},
        labels={"team_abbrev": "Team", "points": "Points", "conference_name": "Conference"},
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)