from collections.abc import Callable, Mapping, Sequence
from typing import Final, Literal, TypeVar

from typing_extensions import TypedDict


class UserDict(TypedDict, total=False):
    id: str
    email: str
    # Add other possible user fields here as needed
    # For strict typing, you should enumerate all expected fields
    # If unknown, you may use: ...


RequiredField = Literal["id", "email"]


def filter_fields(
    obj: Mapping[str, object], fields: Sequence[str]
) -> dict[str, object]:
    """
    Filter a mapping to only include specified fields and required fields.
    Args:
        obj: The mapping to filter.
        fields: The fields to include.
    Returns:
        A new dict with only the specified and required fields.
    """
    if fields is None:
        raise TypeError("fields parameter cannot be None")
    if not fields:
        return dict(obj)
    required_fields: Final[list[RequiredField]] = ["id", "email"]
    fields_to_include: list[str] = list(set(fields) | set(required_fields))
    return {k: v for k, v in obj.items() if k in fields_to_include}


TDate = TypeVar("TDate")


def process_user_filters(
    sort_jsonapi: str,
    created_after: str,
    created_before: str,
    parse_flexible_datetime: Callable[[str], TDate],
) -> tuple[str, Literal["asc", "desc"], TDate, TDate]:
    """
    Process user filter parameters for sorting and date filtering.
    Args:
        sort_jsonapi: The sort field, possibly prefixed with '-'.
        created_after: The lower bound for creation date (string).
        created_before: The upper bound for creation date (string).
        parse_flexible_datetime: Callable to parse date strings.
    Returns:
        sort: The field to sort by.
        order: 'asc' or 'desc'.
        created_after_dt: Parsed lower bound date.
        created_before_dt: Parsed upper bound date.
    Raises:
        ValueError: If date parsing fails.
    """
    sort: str
    order: Literal["asc", "desc"]
    if sort_jsonapi.startswith("-"):
        sort = sort_jsonapi[1:]
        order = "desc"
    else:
        sort = sort_jsonapi
        order = "asc"
    try:
        created_after_dt: TDate = parse_flexible_datetime(created_after)
    except ValueError as e:
        raise ValueError(f"Invalid created_after: {e}") from e
    try:
        created_before_dt: TDate = parse_flexible_datetime(created_before)
    except ValueError as e:
        raise ValueError(f"Invalid created_before: {e}") from e
    return sort, order, created_after_dt, created_before_dt
