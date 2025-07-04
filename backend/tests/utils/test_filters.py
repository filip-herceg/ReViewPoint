import pytest
from datetime import datetime, UTC

from src.utils.filters import filter_fields, process_user_filters
from src.utils.datetime import parse_flexible_datetime
from tests.test_templates import UtilityUnitTestTemplate


class TestFilters(UtilityUnitTestTemplate):
    """Test utility functions in src.utils.filters module."""

    def test_filter_fields_empty_fields_list(self):
        """Test filter_fields with empty fields list returns original object."""
        obj = {"id": 1, "email": "test@example.com", "name": "John", "age": 30}
        result = filter_fields(obj, [])
        self.assert_equal(result, obj)

    def test_filter_fields_none_fields_list(self):
        """Test filter_fields with None fields list returns original object."""
        obj = {"id": 1, "email": "test@example.com", "name": "John", "age": 30}
        result = filter_fields(obj, None)
        self.assert_equal(result, obj)

    def test_filter_fields_with_specific_fields(self):
        """Test filter_fields with specific fields includes requested fields plus required ones."""
        obj = {"id": 1, "email": "test@example.com", "name": "John", "age": 30, "role": "admin"}
        fields = ["name", "age"]
        result = filter_fields(obj, fields)
        
        # Should include id, email (required) + name, age (requested)
        expected = {"id": 1, "email": "test@example.com", "name": "John", "age": 30}
        self.assert_equal(result, expected)

    def test_filter_fields_with_required_fields_included(self):
        """Test filter_fields when required fields are already in the requested fields."""
        obj = {"id": 1, "email": "test@example.com", "name": "John", "age": 30}
        fields = ["id", "email", "name"]
        result = filter_fields(obj, fields)
        
        expected = {"id": 1, "email": "test@example.com", "name": "John"}
        self.assert_equal(result, expected)

    def test_filter_fields_with_nonexistent_fields(self):
        """Test filter_fields with fields that don't exist in the object."""
        obj = {"id": 1, "email": "test@example.com", "name": "John"}
        fields = ["nonexistent_field", "another_missing_field"]
        result = filter_fields(obj, fields)
        
        # Should only include the required fields that exist
        expected = {"id": 1, "email": "test@example.com"}
        self.assert_equal(result, expected)

    def test_filter_fields_missing_required_fields(self):
        """Test filter_fields when object is missing required fields."""
        obj = {"name": "John", "age": 30}  # Missing id and email
        fields = ["name"]
        result = filter_fields(obj, fields)
        
        # Should only include fields that exist
        expected = {"name": "John"}
        self.assert_equal(result, expected)

    def test_filter_fields_empty_object(self):
        """Test filter_fields with empty object."""
        obj = {}
        fields = ["name", "email"]
        result = filter_fields(obj, fields)
        
        expected = {}
        self.assert_equal(result, expected)

    def test_filter_fields_duplicate_fields(self):
        """Test filter_fields with duplicate fields in the list."""
        obj = {"id": 1, "email": "test@example.com", "name": "John", "age": 30}
        fields = ["name", "name", "age", "id"]  # Duplicates
        result = filter_fields(obj, fields)
        
        expected = {"id": 1, "email": "test@example.com", "name": "John", "age": 30}
        self.assert_equal(result, expected)

    def test_process_user_filters_ascending_sort(self):
        """Test process_user_filters with ascending sort (no prefix)."""
        sort_jsonapi = "created_at"
        created_after = "2023-01-01T00:00:00Z"
        created_before = "2023-12-31T23:59:59Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "created_at")
        self.assert_equal(order, "asc")
        self.assert_is_instance(created_after_dt, datetime)
        self.assert_is_instance(created_before_dt, datetime)
        self.assert_equal(created_after_dt.year, 2023)
        self.assert_equal(created_before_dt.year, 2023)

    def test_process_user_filters_descending_sort(self):
        """Test process_user_filters with descending sort (- prefix)."""
        sort_jsonapi = "-created_at"
        created_after = "2023-01-01T00:00:00Z"
        created_before = "2023-12-31T23:59:59Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "created_at")
        self.assert_equal(order, "desc")
        self.assert_is_instance(created_after_dt, datetime)
        self.assert_is_instance(created_before_dt, datetime)

    def test_process_user_filters_different_datetime_formats(self):
        """Test process_user_filters with different datetime formats."""
        sort_jsonapi = "name"
        created_after = "2023-01-01"  # Date only
        created_before = "2023-12-31T23:59:59+00:00"  # With timezone
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "name")
        self.assert_equal(order, "asc")
        self.assert_is_instance(created_after_dt, datetime)
        self.assert_is_instance(created_before_dt, datetime)

    def test_process_user_filters_invalid_created_after(self):
        """Test process_user_filters with invalid created_after datetime."""
        sort_jsonapi = "created_at"
        created_after = "invalid-date"
        created_before = "2023-12-31T23:59:59Z"
        
        with pytest.raises(ValueError) as exc_info:
            process_user_filters(
                sort_jsonapi, created_after, created_before, parse_flexible_datetime
            )
        
        self.assert_in("Invalid created_after", str(exc_info.value))

    def test_process_user_filters_invalid_created_before(self):
        """Test process_user_filters with invalid created_before datetime."""
        sort_jsonapi = "created_at"
        created_after = "2023-01-01T00:00:00Z"
        created_before = "not-a-date"
        
        with pytest.raises(ValueError) as exc_info:
            process_user_filters(
                sort_jsonapi, created_after, created_before, parse_flexible_datetime
            )
        
        self.assert_in("Invalid created_before", str(exc_info.value))

    def test_process_user_filters_empty_string_datetimes(self):
        """Test process_user_filters with empty string datetimes."""
        sort_jsonapi = "email"
        created_after = ""
        created_before = ""
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "email")
        self.assert_equal(order, "asc")
        self.assert_is_none(created_after_dt)
        self.assert_is_none(created_before_dt)

    def test_process_user_filters_complex_sort_field(self):
        """Test process_user_filters with complex sort field names."""
        sort_jsonapi = "-user.profile.last_login"
        created_after = "2023-01-01T00:00:00Z"
        created_before = "2023-12-31T23:59:59Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "user.profile.last_login")
        self.assert_equal(order, "desc")

    def test_process_user_filters_sort_field_starting_with_dash_but_valid_field(self):
        """Test process_user_filters with sort field that naturally starts with dash."""
        # Edge case: what if a field name actually starts with a dash?
        sort_jsonapi = "--special-field"  # Double dash
        created_after = "2023-01-01T00:00:00Z"
        created_before = "2023-12-31T23:59:59Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "-special-field")
        self.assert_equal(order, "desc")

    def test_process_user_filters_microseconds_datetime(self):
        """Test process_user_filters with datetime including microseconds."""
        sort_jsonapi = "created_at"
        created_after = "2023-01-01T00:00:00.123456Z"
        created_before = "2023-12-31T23:59:59.999999Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "created_at")
        self.assert_equal(order, "asc")
        self.assert_equal(created_after_dt.microsecond, 123456)
        self.assert_equal(created_before_dt.microsecond, 999999)

    def test_filter_fields_preserves_all_values_types(self):
        """Test filter_fields preserves different value types correctly."""
        obj = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "active": True,
            "score": 95.5,
            "tags": ["admin", "user"],
            "metadata": {"role": "admin", "level": 5},
            "null_field": None
        }
        fields = ["name", "active", "score", "tags", "metadata", "null_field"]
        result = filter_fields(obj, fields)
        
        expected = {
            "id": 1,
            "email": "test@example.com",
            "name": "John",
            "active": True,
            "score": 95.5,
            "tags": ["admin", "user"],
            "metadata": {"role": "admin", "level": 5},
            "null_field": None
        }
        self.assert_equal(result, expected)

    def test_process_user_filters_whitespace_handling(self):
        """Test process_user_filters handles whitespace in sort field correctly."""
        sort_jsonapi = " -created_at "  # With leading/trailing spaces
        created_after = "2023-01-01T00:00:00Z"
        created_before = "2023-12-31T23:59:59Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        # The function doesn't trim whitespace, so the leading space prevents 
        # recognition of the dash as descending indicator
        self.assert_equal(sort, " -created_at ")  # Whole string is preserved
        self.assert_equal(order, "asc")  # Defaults to ascending

    def test_filter_fields_with_only_required_fields_requested(self):
        """Test filter_fields when only required fields are requested."""
        obj = {"id": 1, "email": "test@example.com", "name": "John", "age": 30}
        fields = ["id", "email"]
        result = filter_fields(obj, fields)
        
        expected = {"id": 1, "email": "test@example.com"}
        self.assert_equal(result, expected)

    def test_filter_fields_empty_list_behavior(self):
        """Test filter_fields behavior with empty list."""
        obj = {"id": 1, "email": "test@example.com", "name": "John"}
        
        # Empty list should return original object
        result_empty = filter_fields(obj, [])
        self.assert_equal(result_empty, obj)
        
        # Verify it returns the same object reference
        assert result_empty is obj

    def test_process_user_filters_only_dash_sort_field(self):
        """Test process_user_filters with sort field that is just a dash."""
        sort_jsonapi = "-"
        created_after = "2023-01-01T00:00:00Z"
        created_before = "2023-12-31T23:59:59Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        self.assert_equal(sort, "")  # Empty string after removing dash
        self.assert_equal(order, "desc")

    def test_process_user_filters_multiple_dashes(self):
        """Test process_user_filters with multiple leading dashes."""
        sort_jsonapi = "---created_at"
        created_after = "2023-01-01T00:00:00Z"
        created_before = "2023-12-31T23:59:59Z"
        
        sort, order, created_after_dt, created_before_dt = process_user_filters(
            sort_jsonapi, created_after, created_before, parse_flexible_datetime
        )
        
        # Only the first dash is removed
        self.assert_equal(sort, "--created_at")
        self.assert_equal(order, "desc")

    def test_filter_fields_with_integer_and_string_keys_mixed(self):
        """Test filter_fields handles mixed key types gracefully."""
        # Edge case: what if the object has non-string keys?
        obj = {"id": 1, "email": "test@example.com", 123: "numeric_key", "name": "John"}
        fields = ["name", 123]  # Mix of string and non-string in fields
        
        # The function should include the numeric key if it's requested
        result = filter_fields(obj, fields)
        expected = {"id": 1, "email": "test@example.com", 123: "numeric_key", "name": "John"}
        self.assert_equal(result, expected)
