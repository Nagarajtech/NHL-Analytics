def format_season(season_id) -> str:
    """Convert 20252026 -> '2025-2026'. Falls back to str(season_id) if unexpected format."""
    s = str(season_id)
    if len(s) == 8:
        return f"{s[:4]}-{s[4:]}"
    return s