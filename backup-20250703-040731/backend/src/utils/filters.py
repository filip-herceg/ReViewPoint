def filter_fields(obj: dict, fields: list[str]) -> dict:
    if not fields:
        return obj
    required_fields = ["id", "email"]
    fields_to_include = list(set(fields + required_fields))
    return {k: v for k, v in obj.items() if k in fields_to_include}


def process_user_filters(
    sort_jsonapi: str, created_after: str, created_before: str, parse_flexible_datetime
) -> tuple[str, str, object, object]:
    if sort_jsonapi.startswith("-"):
        sort = sort_jsonapi[1:]
        order = "desc"
    else:
        sort = sort_jsonapi
        order = "asc"
    try:
        created_after_dt = parse_flexible_datetime(created_after)
    except ValueError as e:
        raise ValueError(f"Invalid created_after: {e}")
    try:
        created_before_dt = parse_flexible_datetime(created_before)
    except ValueError as e:
        raise ValueError(f"Invalid created_before: {e}")
    return sort, order, created_after_dt, created_before_dt
