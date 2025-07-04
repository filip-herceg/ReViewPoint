from datetime import UTC, datetime


def parse_flexible_datetime(dt: str) -> datetime | None:
    """
    Parse an ISO format datetime with flexible input formats.
    Assumes UTC if no timezone specified.

    Args:
        dt (str): The datetime string to parse.

    Returns:
        Optional[datetime]: The parsed datetime object in UTC, or None if input is empty.

    Raises:
        ValueError: If the input string is not a valid datetime format.
    """
    if not dt:
        return None

    # Local variables with explicit types
    dt_str: str = dt
    parsed: datetime

    try:
        # Accept both 'Z', '+00:00', and ' 00:00' (space before offset)
        dt_str = dt_str.replace("Z", "+00:00")
        if " " in dt_str and (
            dt_str.endswith(" 00:00") or dt_str.endswith(" 00:00:00")
        ):
            dt_str = dt_str.replace(" ", "+", 1)
        parsed = datetime.fromisoformat(dt_str)
        if parsed.tzinfo is None:
            # Assume UTC if naive
            parsed = parsed.replace(tzinfo=UTC)
        else:
            parsed = parsed.astimezone(UTC)
        return parsed
    except ValueError as e:
        raise ValueError(f"Invalid datetime format: {dt_str}") from e
