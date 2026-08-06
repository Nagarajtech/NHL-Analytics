import pandas as pd
import streamlit as st

from db import load_full_standings, load_players, load_teams,load_full_players

POSITION_GROUPS = {
    "Forwards": ["C", "LW", "RW"],
    "Defensemen": ["D"],
    "Goalies": ["G"],
}


def render():
    st.title("🛡️ Team Info")

    teams_df = load_teams()
    if teams_df.empty:
        st.warning("No team data found. Run load_nhl_teams.py first.")
        return

    teams_sorted = teams_df.sort_values("team_name")
    selected_name = st.selectbox("Choose a team", teams_sorted["team_name"].tolist())
    team = teams_sorted[teams_sorted["team_name"] == selected_name].iloc[0]

    col1, col2 = st.columns([1, 4])
    with col1:
        if team.get("logo_url"):
            st.image(team["logo_url"], width=140)
    with col2:
        st.header(team["team_name"])
        st.write(f"**Conference:** {team['conference_name'] or '—'}")
        st.write(f"**Division:** {team['division_name'] or '—'}")

    standings_df = load_full_standings()
    team_standings = standings_df[standings_df["team_id"] == team["team_id"]]
    if not team_standings.empty:
        latest = team_standings.sort_values("season").iloc[-1]
        st.divider()
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.metric(
            "Record",
            f"{int(latest['wins'])}-{int(latest['losses'])}-{int(latest['ot_losses'])}",
        )
        s2.metric("Points", int(latest["points"]))
        s3.metric("Goals For", int(latest["goals_for"]))
        s4.metric("Goals Against", int(latest["goals_against"]))
        streak = (
            f"{latest['streak_type']}{int(latest['streak_count'])}"
            if latest["streak_type"]
            else "—"
        )
        s5.metric("Streak", streak)

    st.divider()
    st.subheader("Roster")

    players_df = load_full_players()
    print(players_df.columns)
    print(players_df.head())
    print(players_df.where(players_df["position"] == "G"))
    roster = players_df[players_df["team_id"] == team["team_id"]]

    if roster.empty:
        st.info("No roster data found for this team. Run load_players.py first.")
        return

    tabs = st.tabs(list(POSITION_GROUPS.keys()))
    for tab, (group_name, codes) in zip(tabs, POSITION_GROUPS.items()):
        with tab:
            group_df = roster[roster["position"].isin(codes)].sort_values(
                "jersey_number", na_position="last"
            )
            if group_df.empty:
                st.caption("No players in this group.")
                continue

            cols = st.columns(4)
            for i, (_, player) in enumerate(group_df.iterrows()):
                with cols[i % 4]:
                    with st.container(border=True):
                        if player.get("headshot_url"):
                            st.image(player["headshot_url"], width=100)
                        number = (
                            int(player["jersey_number"])
                            if pd.notna(player["jersey_number"])
                            else "-"
                        )
                        st.markdown(f"**#{number} {player['first_name']} {player['last_name']}**")
                        st.caption(player["position"])
