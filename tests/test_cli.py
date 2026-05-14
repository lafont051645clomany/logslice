"""Tests for the logslice CLI."""

import io
from datetime import datetime, timezone
from pathlib import Path

import pytest

from logslice.cli import build_parser, main, parse_cli_datetime


def dt(year, month, day, hour=0, minute=0, second=0):
    return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)


@pytest.fixture
def log_file(tmp_path):
    content = (
        "2024-01-01T10:00:00 INFO  startup\n"
        "2024-01-01T10:05:00 DEBUG processing\n"
        "2024-01-01T10:10:00 INFO  checkpoint\n"
        "2024-01-01T10:15:00 WARN  slow query\n"
        "2024-01-01T10:20:00 ERROR failure\n"
    )
    p = tmp_path / "app.log"
    p.write_text(content)
    return p


# --- parse_cli_datetime ---

@pytest.mark.parametrize("value,expected", [
    ("2024-01-01", dt(2024, 1, 1)),
    ("2024-01-01 10:05", dt(2024, 1, 1, 10, 5)),
    ("2024-01-01T10:05:30", dt(2024, 1, 1, 10, 5, 30)),
    ("2024-01-01 10:05:30", dt(2024, 1, 1, 10, 5, 30)),
])
def test_parse_cli_datetime_valid(value, expected):
    assert parse_cli_datetime(value) == expected


def test_parse_cli_datetime_invalid():
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        parse_cli_datetime("not-a-date")


# --- main() integration ---

def test_main_missing_file(tmp_path):
    rc = main([str(tmp_path / "nonexistent.log"), "--start", "2024-01-01"])
    assert rc == 2


def test_main_no_range_args(log_file):
    rc = main([str(log_file)])
    assert rc == 2


def test_main_stdout(log_file, capsys):
    rc = main([str(log_file), "--start", "2024-01-01T10:05:00", "--end", "2024-01-01T10:10:00"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "processing" in captured.out
    assert "checkpoint" in captured.out
    assert "startup" not in captured.out
    assert "failure" not in captured.out


def test_main_output_file(log_file, tmp_path):
    out_file = tmp_path / "out.log"
    rc = main([
        str(log_file),
        "--start", "2024-01-01T10:10:00",
        "--end", "2024-01-01T10:15:00",
        "--output", str(out_file),
    ])
    assert rc == 0
    assert out_file.exists()
    text = out_file.read_text()
    assert "checkpoint" in text
    assert "slow query" in text
    assert "failure" not in text


def test_main_start_only(log_file, capsys):
    rc = main([str(log_file), "--start", "2024-01-01T10:15:00"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "slow query" in captured.out
    assert "failure" in captured.out
    assert "checkpoint" not in captured.out


def test_main_end_only(log_file, capsys):
    rc = main([str(log_file), "--end", "2024-01-01T10:05:00"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "startup" in captured.out
    assert "processing" in captured.out
    assert "checkpoint" not in captured.out
