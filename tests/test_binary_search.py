"""Tests for binary_search module."""

import io
import pytest
from datetime import datetime, timezone

from logslice.binary_search import find_start_offset, find_end_offset


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, 0, tzinfo=timezone.utc)


LOG_LINES = [
    b"2024-01-15T10:00:00Z INFO  startup complete\n",
    b"2024-01-15T10:05:00Z DEBUG request received\n",
    b"2024-01-15T10:10:00Z INFO  processing\n",
    b"2024-01-15T10:15:00Z WARN  slow query detected\n",
    b"2024-01-15T10:20:00Z ERROR connection failed\n",
    b"2024-01-15T10:25:00Z INFO  retrying\n",
    b"2024-01-15T10:30:00Z INFO  shutdown\n",
]


@pytest.fixture
def log_file():
    content = b"".join(LOG_LINES)
    return io.BytesIO(content)


def test_find_start_offset_before_all(log_file):
    offset = find_start_offset(log_file, dt(9, 0))
    assert offset == 0


def test_find_start_offset_after_all(log_file):
    content = b"".join(LOG_LINES)
    offset = find_start_offset(log_file, dt(11, 0))
    assert offset == len(content)


def test_find_start_offset_exact_match(log_file):
    offset = find_start_offset(log_file, dt(10, 10))
    log_file.seek(offset)
    line = log_file.readline().decode()
    assert "10:10:00" in line


def test_find_start_offset_between_entries(log_file):
    # 10:07 is between 10:05 and 10:10, should land on 10:10
    offset = find_start_offset(log_file, dt(10, 7))
    log_file.seek(offset)
    line = log_file.readline().decode()
    assert "10:10:00" in line


def test_find_end_offset_after_all(log_file):
    content = b"".join(LOG_LINES)
    offset = find_end_offset(log_file, dt(11, 0))
    assert offset == len(content)


def test_find_end_offset_before_all(log_file):
    offset = find_end_offset(log_file, dt(9, 0))
    assert offset == 0


def test_find_end_offset_exact_match(log_file):
    offset = find_end_offset(log_file, dt(10, 20))
    log_file.seek(0)
    content_up_to = log_file.read(offset)
    lines = content_up_to.decode().splitlines()
    assert any("10:20:00" in l for l in lines)
    assert not any("10:25:00" in l for l in lines)


def test_find_end_offset_between_entries(log_file):
    # 10:22 is between 10:20 and 10:25, last match should be 10:20
    offset = find_end_offset(log_file, dt(10, 22))
    log_file.seek(0)
    content_up_to = log_file.read(offset).decode()
    assert "10:20:00" in content_up_to
    assert "10:25:00" not in content_up_to


def test_empty_file():
    f = io.BytesIO(b"")
    assert find_start_offset(f, dt(10)) == 0
    assert find_end_offset(f, dt(10)) == 0


def test_range_extraction(log_file):
    start = find_start_offset(log_file, dt(10, 10))
    end = find_end_offset(log_file, dt(10, 20))
    log_file.seek(start)
    segment = log_file.read(end - start).decode()
    lines = segment.strip().splitlines()
    assert len(lines) == 3
    assert "10:10:00" in lines[0]
    assert "10:20:00" in lines[-1]
