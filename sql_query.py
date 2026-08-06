import streamlit as st
import pandas as pd
from db import create_connection, DB_PATH

QUERIES = {

    "All Players": """
        SELECT
            p.player_id,
            p.first_name,
            p.last_name,
            p.position,
            t.team_name
        FROM players p
        JOIN teams t
            ON p.team_id = t.team_id
        ORDER BY p.last_name;
    """,

    "Player Scoring Leaders": """
        SELECT
            CONCAT(p.first_name,' ',p.last_name) AS player_name,
            t.team_name,
            SUM(gs.goals) AS goals,
            SUM(gs.assists) AS assists,
            SUM(gs.points) AS points
        FROM players p
        JOIN game_stats gs
            ON p.player_id = gs.player_id
        JOIN teams t
            ON p.team_id = t.team_id
        GROUP BY
            player_name,
            t.team_name
        ORDER BY points DESC
        LIMIT 20;
    """,

    "Game Results": """
        SELECT
            g.game_date,
            ht.team_name AS home_team,
            at.team_name AS away_team,
            g.home_score,
            g.away_score
        FROM games g
        JOIN teams ht
            ON g.home_team_id = ht.team_id
        JOIN teams at
            ON g.away_team_id = at.team_id
        ORDER BY g.game_date DESC;
    """,

    "Top Penalty Minutes": """
        SELECT
            CONCAT(p.first_name,' ',p.last_name) AS player_name,
            SUM(gs.penalty_min) AS penalty_minutes
        FROM players p
        JOIN game_stats gs
            ON p.player_id = gs.player_id
        GROUP BY player_name
        ORDER BY penalty_minutes DESC
        LIMIT 10;
    """,

    "Team Goals": """
        SELECT
            t.team_name,
            SUM(gs.goals) AS total_goals
        FROM teams t
        JOIN players p
            ON t.team_id = p.team_id
        JOIN game_stats gs
            ON p.player_id = gs.player_id
        GROUP BY t.team_name
        ORDER BY total_goals DESC;
    """
}

def run_query(query):

    conn = create_connection(DB_PATH)

    try:
        df = pd.read_sql_query(
            query,
            conn
        )

        return df

    except Exception as e:
        st.error(f"SQL Error: {e}")
        return pd.DataFrame()

    finally:
        conn.close()


def render():

    st.title("SQL Query Explorer")

    st.write(
        "Run predefined SQL queries against the NHL database."
    )


    selected_query = st.selectbox(
        "Choose Query",
        list(QUERIES.keys())
    )


    with st.expander("View SQL"):
        st.code(
            QUERIES[selected_query],
            language="sql"
        )


    if st.button("Run Query"):

        result = run_query(
            QUERIES[selected_query]
        )


        if not result.empty:

            st.success(
                f"Returned {len(result)} rows"
            )


            st.dataframe(
                result,
                use_container_width=True
            )


            csv = result.to_csv(index=False)

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="query_result.csv",
                mime="text/csv"
            )

        else:

            st.warning(
                "No results found."
            )