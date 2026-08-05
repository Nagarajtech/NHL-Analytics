
ENDPOINTS = {
    # Static / reference data
    "teams": "https://api-web.nhle.com/v1/standings/now",

    # Standings
    "standings_now": "https://api-web.nhle.com/v1/standings/now",

    # Schedule (requires a date, e.g. 2026-07-27, or 'now')
    "schedule_by_date": "https://api-web.nhle.com/v1/schedule/{date}",

    # Roster (requires team abbreviation + season, e.g. TOR / 20252026)
    "team_roster": "https://api-web.nhle.com/v1/roster/{team}/{season}",

    # Player profile (requires player_id)
     "player_landing": "https://api-web.nhle.com/v1/player/{player_id}/landing",

    # Game boxscore (requires game_id)
     "game_boxscore": "https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore",

    # Game play-by-play (requires game_id)
     "game_play_by_play": "https://api-web.nhle.com/v1/gamecenter/{game_id}/play-by-play",
}
