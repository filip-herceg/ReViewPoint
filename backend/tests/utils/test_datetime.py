from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final

from src.utils import datetime as dt_utils
from tests.test_templates import UtilityUnitTestTemplate


class TestParseFlexibleDatetime(UtilityUnitTestTemplate):
    def test_iso(self) -> None:
        """
        Test parsing of ISO 8601 datetime with explicit UTC offset.
        """
        dt_str: Final[str] = "2024-06-26T12:34:56+00:00"
        d: datetime | None = dt_utils.parse_flexible_datetime(dt_str)
        self.assert_is_not_none(d)
        assert d is not None
        self.assert_is_instance(d, datetime)
        self.assert_is_not_none(d.tzinfo)
        assert d.tzinfo is not None
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))
        self.assert_equal((d.year, d.month, d.day), (2024, 6, 26))
        self.assert_equal((d.hour, d.minute, d.second), (12, 34, 56))

    def test_z(self) -> None:
        """
        Test parsing of ISO 8601 datetime with 'Z' (UTC) suffix.
        """
        dt_str: Final[str] = "2024-06-26T12:34:56Z"
        d: datetime | None = dt_utils.parse_flexible_datetime(dt_str)
        self.assert_is_not_none(d)
        assert d is not None
        self.assert_is_not_none(d.tzinfo)
        assert d.tzinfo is not None
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))

    def test_space_offset(self) -> None:
        """
        Test parsing of datetime with space before offset.
        """
        dt_str: Final[str] = "2024-06-26T12:34:56 00:00"
        d: datetime | None = dt_utils.parse_flexible_datetime(dt_str)
        self.assert_is_not_none(d)
        assert d is not None
        self.assert_is_not_none(d.tzinfo)
        assert d.tzinfo is not None
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))

    def test_naive(self) -> None:
        """
        Test parsing of naive datetime (should be treated as UTC).
        """
        dt_str: Final[str] = "2024-06-26T12:34:56"
        d: datetime | None = dt_utils.parse_flexible_datetime(dt_str)
        self.assert_is_not_none(d)
        assert d is not None
        self.assert_is_not_none(d.tzinfo)
        assert d.tzinfo is not None
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))

    def test_none(self) -> None:
        """
        Test that empty string returns None.
        """
        result: datetime | None = dt_utils.parse_flexible_datetime("")
        self.assert_is_none(result)

    def test_invalid(self) -> None:
        """
        Test that invalid datetime strings raise ValueError.
        """
        parse: Callable[[str], object] = dt_utils.parse_flexible_datetime
        self.assert_raises(ValueError, parse, "not-a-date")
        self.assert_raises(ValueError, parse, "2024-13-99T99:99:99Z")
        self.assert_raises(ValueError, parse, "2024-06-26T12:34:56+99:99")

    def test_microseconds(self) -> None:
        """
        Test parsing of datetime with microseconds and UTC.
        """
        dt_str: Final[str] = "2024-06-26T12:34:56.123456Z"
        d: datetime | None = dt_utils.parse_flexible_datetime(dt_str)
        self.assert_is_not_none(d)
        assert d is not None
        self.assert_equal(d.microsecond, 123456)
        self.assert_is_not_none(d.tzinfo)
        assert d.tzinfo is not None
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))
