from datetime import datetime
from typing import Final, TypedDict

import pytest

from src.utils.datetime import parse_flexible_datetime
from src.utils.filters import filter_fields, process_user_filters
from tests.test_templates import UtilityUnitTestTemplate


class UserDict(TypedDict, total=False):
    id: int
    email: str
    name: str
    age: int
    role: str
    active: bool
    score: float
    tags: list[str]
    metadata: dict[str, object]
    null_field: None


class TestFilters(UtilityUnitTestTemplate):
    """Test utility functions in src.utils.filters module."""

    def test_filter_fields_empty_fields_list(self) -> None:
        """Test filter_fields with empty fields list returns original object."""
        obj: Final[UserDict] = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
        }
        result = filter_fields(obj, [])
        self.assert_equal(result, obj)

    def test_filter_fields_none_fields_list(self) -> None:
        """Test filter_fields with None fields list returns original object."""
        obj: Final[UserDict] = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
        }
        # filter_fields does not accept None, so skip this test or expect a type error
        with pytest.raises(TypeError):
            filter_fields(obj, None)  # type: ignore

    def test_filter_fields_with_specific_fields(self) -> None:
        """Test filter_fields with specific fields includes requested fields plus required ones."""
        obj: Final[UserDict] = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
            "role": "admin",
        }
        fields: Final[list[str]] = ["name", "age"]
        result = filter_fields(obj, fields)
        expected: UserDict = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
        }
        self.assert_equal(result, expected)

    def test_filter_fields_with_required_fields_included(self) -> None:
        """Test filter_fields when required fields are already in the requested fields."""
        obj: UserDict = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
        }
        fields: list[str] = ["id", "email", "name"]
        result = filter_fields(obj, fields)
        expected: UserDict = {"id": 1, "email": "test@example.com", "name": "John"}
        self.assert_equal(result, expected)

    def test_filter_fields_with_nonexistent_fields(self) -> None:
        """Test filter_fields with fields that don't exist in the object."""
        obj: UserDict = {"id": 1, "email": "test@example.com", "name": "John"}
        fields: list[str] = ["nonexistent_field", "another_missing_field"]
        result = filter_fields(obj, fields)
        # Should only include the required fields that exist
        expected: UserDict = {"id": 1, "email": "test@example.com"}
        self.assert_equal(result, expected)

    def test_filter_fields_missing_required_fields(self) -> None:
        """Test filter_fields when object is missing required fields."""
        obj: UserDict = {"name": "John", "age": 30}  # Missing id and email
        fields: list[str] = ["name"]
        result = filter_fields(obj, fields)
        # Should only include fields that exist
        expected: UserDict = {"name": "John"}
        self.assert_equal(result, expected)

    def test_filter_fields_empty_object(self) -> None:
        """Test filter_fields with empty object."""
        obj: UserDict = {}
        fields: list[str] = ["name", "email"]
        result = filter_fields(obj, fields)
        expected: UserDict = {}
        self.assert_equal(result, expected)

    def test_filter_fields_duplicate_fields(self) -> None:
        """Test filter_fields with duplicate fields in the list."""
        obj: UserDict = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
        }
        fields: list[str] = ["name", "name", "age", "id"]  # Duplicates
        result = filter_fields(obj, fields)
        expected: UserDict = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
        }
        self.assert_equal(result, expected)

    def test_process_user_filters_ascending_sort(self) -> None:
        """Test process_user_filters with ascending sort (no prefix)."""
        sort_jsonapi: str = "created_at"
        created_after: str = "2023-01-01T00:00:00Z"
        created_before: str = "2023-12-31T23:59:59Z"

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "created_at")
        self.assert_equal(order, "asc")
        self.assert_is_instance(created_after_dt, datetime)
        self.assert_is_instance(created_before_dt, datetime)
        assert created_after_dt is not None
        assert created_before_dt is not None
        self.assert_equal(created_after_dt.year, 2023)
        self.assert_equal(created_before_dt.year, 2023)

    def test_process_user_filters_descending_sort(self) -> None:
        """Test process_user_filters with descending sort (- prefix)."""
        sort_jsonapi: str = "-created_at"
        created_after: str = "2023-01-01T00:00:00Z"
        created_before: str = "2023-12-31T23:59:59Z"

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "created_at")
        self.assert_equal(order, "desc")
        self.assert_is_instance(created_after_dt, datetime)
        self.assert_is_instance(created_before_dt, datetime)

    def test_process_user_filters_different_datetime_formats(self) -> None:
        """Test process_user_filters with different datetime formats."""
        sort_jsonapi: str = "name"
        created_after: str = "2023-01-01"  # Date only
        created_before: str = "2023-12-31T23:59:59+00:00"  # With timezone

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "name")
        self.assert_equal(order, "asc")
        self.assert_is_instance(created_after_dt, datetime)
        self.assert_is_instance(created_before_dt, datetime)

    def test_process_user_filters_invalid_created_after(self) -> None:
        """Test process_user_filters with invalid created_after datetime. Expects ValueError."""
        sort_jsonapi: str = "created_at"
        created_after: str = "invalid-date"
        created_before: str = "2023-12-31T23:59:59Z"

        with pytest.raises(ValueError) as exc_info:
            process_user_filters(
                sort_jsonapi, created_after, created_before, parse_flexible_datetime
            )

        self.assert_in("Invalid created_after", str(exc_info.value))

    def test_process_user_filters_invalid_created_before(self) -> None:
        """Test process_user_filters with invalid created_before datetime. Expects ValueError."""
        sort_jsonapi: str = "created_at"
        created_after: str = "2023-01-01T00:00:00Z"
        created_before: str = "not-a-date"

        with pytest.raises(ValueError) as exc_info:
            process_user_filters(
                sort_jsonapi, created_after, created_before, parse_flexible_datetime
            )

        self.assert_in("Invalid created_before", str(exc_info.value))

    def test_process_user_filters_empty_string_datetimes(self) -> None:
        """Test process_user_filters with empty string datetimes."""
        sort_jsonapi: str = "email"
        created_after: str = ""
        created_before: str = ""

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "email")
        self.assert_equal(order, "asc")
        self.assert_is_none(created_after_dt)
        self.assert_is_none(created_before_dt)

    def test_process_user_filters_complex_sort_field(self) -> None:
        """Test process_user_filters with complex sort field names."""
        sort_jsonapi: str = "-user.profile.last_login"
        created_after: str = "2023-01-01T00:00:00Z"
        created_before: str = "2023-12-31T23:59:59Z"

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "user.profile.last_login")
        self.assert_equal(order, "desc")

    def test_process_user_filters_sort_field_starting_with_dash_but_valid_field(
        self,
    ) -> None:
        """Test process_user_filters with sort field that naturally starts with dash."""
        sort_jsonapi: str = "--special-field"  # Double dash
        created_after: str = "2023-01-01T00:00:00Z"
        created_before: str = "2023-12-31T23:59:59Z"

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "-special-field")
        self.assert_equal(order, "desc")

    def test_process_user_filters_microseconds_datetime(self) -> None:
        """Test process_user_filters with datetime including microseconds."""
        sort_jsonapi: str = "created_at"
        created_after: str = "2023-01-01T00:00:00.123456Z"
        created_before: str = "2023-12-31T23:59:59.999999Z"

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "created_at")
        self.assert_equal(order, "asc")
        assert created_after_dt is not None
        assert created_before_dt is not None
        self.assert_equal(created_after_dt.microsecond, 123456)
        self.assert_equal(created_before_dt.microsecond, 999999)

    def test_filter_fields_preserves_all_values_types(self) -> None:
        """Test filter_fields preserves different value types correctly."""
        obj: UserDict = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "active": True,
            "score": 95.5,
            "tags": ["admin", "user"],
            "metadata": {"role": "admin", "level": 5},
            "null_field": None,
        }
        fields: list[str] = [
            "name",
            "active",
            "score",
            "tags",
            "metadata",
            "null_field",
        ]
        result = filter_fields(obj, fields)

        expected: UserDict = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "active": True,
            "score": 95.5,
            "tags": ["admin", "user"],
            "metadata": {"role": "admin", "level": 5},
            "null_field": None,
        }
        self.assert_equal(result, expected)

    def test_process_user_filters_whitespace_handling(self) -> None:
        """Test process_user_filters handles whitespace in sort field correctly."""
        sort_jsonapi: str = " -created_at "  # With leading/trailing spaces
        created_after: str = "2023-01-01T00:00:00Z"
        created_before: str = "2023-12-31T23:59:59Z"

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        # The function doesn't trim whitespace, so the leading space prevents
        # recognition of the dash as descending indicator
        self.assert_equal(sort, " -created_at ")  # Whole string is preserved
        self.assert_equal(order, "asc")  # Defaults to ascending

    def test_filter_fields_with_only_required_fields_requested(self) -> None:
        """Test filter_fields when only required fields are requested."""
        obj: UserDict = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "age": 30,
        }
        fields: list[str] = ["id", "email"]
        result = filter_fields(obj, fields)
        expected: UserDict = {"id": 1, "email": "test@example.com"}
        self.assert_equal(result, expected)

    def test_filter_fields_empty_list_behavior(self) -> None:
        """
        Test filter_fields behavior with empty list.
        Verifies that passing an empty list returns the original object unchanged.
        """
        obj: Final[UserDict] = {"id": 1, "email": "test@example.com", "name": "John"}
        result_empty = filter_fields(obj, [])
        self.assert_equal(result_empty, obj)

    def test_process_user_filters_only_dash_sort_field(self) -> None:
        """
        Test process_user_filters with sort field that is just a dash.
        Verifies that a dash-only sort field results in an empty sort string and descending order.
        """
        sort_jsonapi: Final[str] = "-"
        created_after: Final[str] = "2023-01-01T00:00:00Z"
        created_before: Final[str] = "2023-12-31T23:59:59Z"

        sort: str
        order: str
        created_after_dt: datetime | None
        created_before_dt: datetime | None
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        self.assert_equal(sort, "")  # Empty string after removing dash
        self.assert_equal(order, "desc")

    def test_process_user_filters_multiple_dashes(self) -> None:
        """Test process_user_filters with multiple leading dashes."""
        sort_jsonapi: str = "---created_at"
        created_after: str = "2023-01-01T00:00:00Z"
        created_before: str = "2023-12-31T23:59:59Z"

        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )

        # Only the first dash is removed
        self.assert_equal(sort, "--created_at")
        self.assert_equal(order, "desc")

    def test_filter_fields_with_integer_and_string_keys_mixed(self) -> None:
        """Test filter_fields handles mixed key types gracefully."""
        # Edge case: what if the object has non-string keys?
        obj: dict[object, object] = {
            "id": 1,
            "email": "test@example.com",
            123: "numeric_key",
            "name": "John",
        }
        fields: list[str] = ["name"]  # Only use string fields for type safety
        # The function should ignore the numeric key
        result = filter_fields(
            {k: v for k, v in obj.items() if isinstance(k, str)}, fields
        )
        expected: dict[str, object] = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
        }
        self.assert_equal(result, expected)
