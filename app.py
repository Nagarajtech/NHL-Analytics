import streamlit as st
from streamlit_option_menu import option_menu

import home,standings_info,teams_info,game_results,player_search,dashboard,sql_query

st.set_page_config(
    page_title="NHL Explorer",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.markdown("## 🏒 NHL Explorer")
    st.caption("Teams · Standings · Rosters · Players")
    selected = option_menu(
        menu_title=None,
        options=["Home", "Team Info", "Standings","Game Results","Players","Dashboard","SQL Queries"],
        icons=["house-door", "list-ol", "shield-shaded", "search"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"font-size": "16px"},
            "nav-link": {"font-size": "15px", "text-align": "left", "margin": "2px"},
            "nav-link-selected": {"background-color": "#0b5ed7"},
        },
    )
    st.divider()

PAGES = {
    "Home": home.render,
    "Team Info": teams_info.render,
    "Standings": standings_info.render,
    "Game Results": game_results.render,
    "Players":player_search.render,
    "Dashboard":dashboard.render,
    "SQL Queries":sql_query.render,
}

PAGES[selected]()
