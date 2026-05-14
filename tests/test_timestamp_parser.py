"""Tests for logslice.timestamp_parser module."""

import pytest
from datetime import datetime

from logslice.timestamp_parser import parse_line_timestamp, parse_timestamp


class TestParseLineTimestamp:
    def test_iso8601_with_z(self):
        line = "2024-01-15T13:45:00Z INFO server started"
        result = parse_line_timestamp(line)
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_iso8601_no_tz(self):
        line = "2024-03-22T08:00:00 DEBUG connection established"
        result = parse_line_timestamp(line)
        assert result == datetime(2024, 3, 22, 8, 0, 0)

    def test_syslog_format(self):
        line = "Jan 15 13:45:00 myhost sshd[1234]: Accepted"
        result = parse_line_timestamp(line)
        assert result is not None
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 13
        assert result.minute == 45

    def test_apache_format(self):
        line = '192.168.1.1 - - [15/Jan/2024:13:45:00 +0000] "GET / HTTP/1.1" 200'
        result = parse_line_timestamp(line)
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_simple_datetime_format(self):
        line = "2024-06-01 09:30:00 ERROR disk full"
        result = parse_line_timestamp(line)
        assert result == datetime(2024, 6, 1, 9, 30, 0)

    def test_no_timestamp_returns_none(self):
        line = "this log line has no timestamp at all"
        result = parse_line_timestamp(line)
        assert result is None

    def test_empty_line_returns_none(self):
        assert parse_line_timestamp("") is None


class TestParseTimestamp:
    def test_date_only(self):
        result = parse_timestamp("2024-01-15")
        assert result == datetime(2024, 1, 15)

    def test_datetime_with_seconds(self):
        result = parse_timestamp("2024-01-15 13:45:00")
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_datetime_without_seconds(self):
        result = parse_timestamp("2024-01-15 13:45")
        assert result == datetime(2024, 1, 15, 13, 45)

    def test_iso8601(self):
        result = parse_timestamp("2024-01-15T13:45:00")
        assert result == datetime(2024, 1, 15, 13, 45, 0)

    def test_invalid_raises_value_error(self):
        with pytest.raises(ValueError, match="Unable to parse timestamp"):
            parse_timestamp("not-a-date")

    def test_invalid_format_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_timestamp("15/01/2024")
