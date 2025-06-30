from datetime import datetime, timedelta

from src.utils import datetime as dt_utils
from tests.test_templates import UtilityUnitTestTemplate


class TestParseFlexibleDatetime(UtilityUnitTestTemplate):
    def test_iso(self):
        d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56+00:00")
        self.assert_is_instance(d, datetime)
        self.assert_is_not_none(d.tzinfo)
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))
        self.assert_equal((d.year, d.month, d.day), (2024, 6, 26))
        self.assert_equal((d.hour, d.minute, d.second), (12, 34, 56))

    def test_z(self):
        d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56Z")
        self.assert_is_not_none(d.tzinfo)
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))

    def test_space_offset(self):
        d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56 00:00")
        self.assert_is_not_none(d.tzinfo)
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))

    def test_naive(self):
        d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56")
        self.assert_is_not_none(d.tzinfo)
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))

    def test_none(self):
        self.assert_is_none(dt_utils.parse_flexible_datetime(""))

    def test_invalid(self):
        self.assert_raises(ValueError, dt_utils.parse_flexible_datetime, "not-a-date")
        self.assert_raises(
            ValueError, dt_utils.parse_flexible_datetime, "2024-13-99T99:99:99Z"
        )
        self.assert_raises(
            ValueError, dt_utils.parse_flexible_datetime, "2024-06-26T12:34:56+99:99"
        )

    def test_microseconds(self):
        d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56.123456Z")
        self.assert_is_not_none(d)
        self.assert_equal(d.microsecond, 123456)
        self.assert_is_not_none(d.tzinfo)
        self.assert_equal(d.tzinfo.utcoffset(d), timedelta(0))
