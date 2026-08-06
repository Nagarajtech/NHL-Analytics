# NHL Analytics Dashboard

A Streamlit-based NHL analytics dashboard for exploring teams, standings, player stats, game results, and SQL queries.

## Overview

This repository provides a Streamlit app that reads NHL data from a local SQLite database and displays interactive pages for:

- League dashboard and team highlights
- Team information and rosters
- Standings by season, conference, and division
- Player search and stat summaries
- SQL query explorer with downloadable results

## Requirements

- Python 3.9+
- `streamlit`
- `streamlit-option-menu`
- `pandas`
- `plotly`
- `requests`
- `python-dotenv`

Install dependencies with:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the app

Start the Streamlit application from the repository root:

```bash
streamlit run app.py
```

Then open the URL shown in the terminal to access the NHL Explorer.

## Database

The app loads data from a local SQLite database using `db.py`.
By default it uses `nhl.db` in the project root.

To override the database path, set:

```bash
export NHL_DB_PATH=/path/to/your/nhl.db
```

## Project structure

- `app.py` - Streamlit application entry point and sidebar navigation
- `home.py` - main dashboard page with league metrics and charts
- `teams_info.py` - team overview and roster browser
- `standings_info.py` - standings explorer by season, conference, and division
- `game_results.py` - player statistics and game-summary page
- `player_search.py` - player search and profile stats
- `dashboard.py` - leaderboard views for goals, assists, points, and penalties
- `sql_query.py` - predefined SQL queries and CSV export
- `db.py` - SQLite connection and data loading helpers
- `data/` - raw and processed data folders
- `requirements.txt` - required Python packages

## Notes

The app depends on a populated SQLite database. If the dashboard shows no data, ensure the NHL database contains the required tables and data.
