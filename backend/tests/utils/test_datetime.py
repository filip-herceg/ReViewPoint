import pytest
from datetime import datetime, timezone, timedelta
from src.utils import datetime as dt_utils

def test_parse_flexible_datetime_iso():
    d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56+00:00")
    assert isinstance(d, datetime)
    assert d.tzinfo is not None
    assert d.tzinfo.utcoffset(d) == timedelta(0)
    assert d.year == 2024 and d.month == 6 and d.day == 26
    assert d.hour == 12 and d.minute == 34 and d.second == 56

def test_parse_flexible_datetime_z():
    d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56Z")
    assert d.tzinfo is not None
    assert d.tzinfo.utcoffset(d) == timedelta(0)

def test_parse_flexible_datetime_space_offset():
    d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56 00:00")
    assert d.tzinfo is not None
    assert d.tzinfo.utcoffset(d) == timedelta(0)

def test_parse_flexible_datetime_naive():
    d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56")
    assert d.tzinfo is not None
    assert d.tzinfo.utcoffset(d) == timedelta(0)

def test_parse_flexible_datetime_none():
    assert dt_utils.parse_flexible_datetime("") is None
    assert dt_utils.parse_flexible_datetime(None) is None

def test_parse_flexible_datetime_invalid():
    with pytest.raises(ValueError):
        dt_utils.parse_flexible_datetime("not-a-date")
    with pytest.raises(ValueError):
        dt_utils.parse_flexible_datetime("2024-13-99T99:99:99Z")
    with pytest.raises(ValueError):
        dt_utils.parse_flexible_datetime("2024-06-26T12:34:56+99:99")

def test_parse_flexible_datetime_microseconds():
    d = dt_utils.parse_flexible_datetime("2024-06-26T12:34:56.123456Z")
    assert d.microsecond == 123456
    assert d.tzinfo is not None
    assert d.tzinfo.utcoffset(d) == timedelta(0)
