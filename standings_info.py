import streamlit as st

from db import load_full_standings


def render():
    st.title("League Standings")

    df = load_full_standings()
    if df.empty:
        st.warning("No standings data found. Run load_nhl_standings.py first.")
        return

    seasons = sorted(df["season"].unique(), reverse=True)
    season = st.selectbox("Season", seasons)
    df = df[df["season"] == season]

    f1, f2 = st.columns(2)
    with f1:
        conferences = ["All"] + sorted(df["conference_name"].dropna().unique().tolist())
        conf = st.selectbox("Conference", conferences)
    with f2:
        div_pool = df if conf == "All" else df[df["conference_name"] == conf]
        divisions = ["All"] + sorted(div_pool["division_name"].dropna().unique().tolist())
        division = st.selectbox("Division", divisions)

    filtered = df.copy()
    if conf != "All":
        filtered = filtered[filtered["conference_name"] == conf]
    if division != "All":
        filtered = filtered[filtered["division_name"] == division]

    filtered = filtered.sort_values("points", ascending=False).reset_index(drop=True)
    filtered.insert(0, "Rank", filtered.index + 1)

    display_df = filtered[
        [
            "Rank",
            "logo_url",
            "team_name",
            "conference_name",
            "division_name",
            "games_played",
            "wins",
            "losses",
            "ot_losses",
            "points",
            "goals_for",
            "goals_against",
            "streak_type",
            "streak_count",
        ]
    ].rename(
        columns={
            "logo_url": "Logo",
            "team_name": "Team",
            "conference_name": "Conference",
            "division_name": "Division",
            "games_played": "GP",
            "wins": "W",
            "losses": "L",
            "ot_losses": "OTL",
            "points": "PTS",
            "goals_for": "GF",
            "goals_against": "GA",
            "streak_type": "Streak",
            "streak_count": "Count",
        }
    )

    st.dataframe(
        display_df,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo", width="small"),
            "PTS": st.column_config.NumberColumn("PTS", format="%d"),
        },
        hide_index=True,
        use_container_width=True,
        height=min(700, 40 + 35 * len(display_df)),
    )

    st.caption(f"Showing {len(display_df)} team(s) for {season}")
