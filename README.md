# NHL Project

A Python-based NHL data dashboard project.

## Overview

This repository contains scripts and data for loading, querying, and visualizing NHL stats and game results.

## Files

- `app.py` - main application entry
- `dashboard.py` - dashboard rendering
- `database.py` / `db.py` - database helpers
- `game_stats.py`, `players.py`, `standings.py`, `teams.py` - data modules
- `requirements.txt` - Python dependencies

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Notes

The repo ignores local environment files, database files, log output, and Python caches.
