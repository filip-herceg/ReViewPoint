from datetime import UTC, datetime


def parse_flexible_datetime(dt: str) -> datetime | None:
    """
    Parse an ISO format datetime with flexible input formats.
    Assumes UTC if no timezone specified.
    """
    if not dt:
        return None

    try:
        # Accept both 'Z', '+00:00', and ' 00:00' (space before offset)
        dt = dt.replace("Z", "+00:00")
        if " " in dt and (dt.endswith(" 00:00") or dt.endswith(" 00:00:00")):
            dt = dt.replace(" ", "+", 1)
        parsed = datetime.fromisoformat(dt)
        if parsed.tzinfo is None:
            # Assume UTC if naive
            parsed = parsed.replace(tzinfo=UTC)
        else:
            parsed = parsed.astimezone(UTC)
        return parsed
    except Exception as e:
        raise ValueError(f"Invalid datetime format: {dt}") from e
