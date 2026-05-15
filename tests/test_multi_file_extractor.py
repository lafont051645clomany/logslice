"""Tests for multi_file_extractor module."""

import gzip
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from logslice.multi_file_extractor import extract_from_rotated, count_matching_lines


def dt(year, month, day, hour, minute, second=0):
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)


LINES_OLD = [
    "2024-01-01T08:00:00Z INFO  booting up\n",
    "2024-01-01T09:00:00Z INFO  ready\n",
    "2024-01-01T10:00:00Z WARN  high memory\n",
]

LINES_NEW = [
    "2024-01-02T06:00:00Z INFO  new day\n",
    "2024-01-02T07:00:00Z ERROR crash\n",
    "2024-01-02T08:00:00Z INFO  restarted\n",
]


@pytest.fixture()
def log_dir(tmp_path):
    base = tmp_path / "app.log"
    rotated = tmp_path / "app.log.1"
    rotated_gz = tmp_path / "app.log.2.gz"

    # Newest file
    base.write_text("".join(LINES_NEW))
    # Middle rotated file
    rotated.write_text("".join(LINES_OLD))
    # Oldest rotated gz (duplicate of OLD for simplicity)
    with gzip.open(str(rotated_gz), "wt") as f:
        f.write("".join(LINES_OLD))

    return str(base)


def test_extract_all_lines(log_dir):
    lines = list(extract_from_rotated(log_dir, dt(2024, 1, 1, 0, 0), dt(2024, 1, 2, 23, 59)))
    assert len(lines) == 9  # 3 from gz + 3 from .1 + 3 from base


def test_extract_only_new_file(log_dir):
    lines = list(extract_from_rotated(log_dir, dt(2024, 1, 2, 6, 0), dt(2024, 1, 2, 8, 0)))
    assert all("2024-01-02" in l for l in lines)
    assert len(lines) == 3


def test_extract_only_old_rotated(log_dir):
    lines = list(extract_from_rotated(log_dir, dt(2024, 1, 1, 9, 0), dt(2024, 1, 1, 10, 0)))
    # Should appear in both .1 and .2.gz (same content)
    assert len(lines) == 4  # 2 lines x2 files
    assert all("2024-01-01" in l for l in lines)


def test_extract_empty_range(log_dir):
    lines = list(extract_from_rotated(log_dir, dt(2024, 1, 3, 0, 0), dt(2024, 1, 3, 23, 59)))
    assert lines == []


def test_count_matching_lines(log_dir):
    count = count_matching_lines(log_dir, dt(2024, 1, 1, 0, 0), dt(2024, 1, 2, 23, 59))
    assert count == 9


def test_count_empty_range(log_dir):
    count = count_matching_lines(log_dir, dt(2025, 1, 1, 0, 0), dt(2025, 1, 1, 1, 0))
    assert count == 0
