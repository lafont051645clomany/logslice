"""Tests for logslice.output_formatter."""

import io
import pytest

from logslice.output_formatter import (
    OutputFormat,
    format_lines,
    format_name_from_string,
)


LINES = [
    "2024-01-01T00:00:01Z INFO  starting\n",
    "2024-01-01T00:00:02Z DEBUG loop\n",
    "2024-01-01T00:00:03Z ERROR boom\n",
]


# ---------------------------------------------------------------------------
# format_name_from_string
# ---------------------------------------------------------------------------

def test_format_name_valid_raw():
    assert format_name_from_string("raw") == OutputFormat.RAW


def test_format_name_valid_numbered():
    assert format_name_from_string("numbered") == OutputFormat.NUMBERED


def test_format_name_valid_count():
    assert format_name_from_string("count") == OutputFormat.COUNT


def test_format_name_case_insensitive():
    assert format_name_from_string("RAW") == OutputFormat.RAW
    assert format_name_from_string("Numbered") == OutputFormat.NUMBERED


def test_format_name_invalid():
    with pytest.raises(ValueError, match="Unknown output format"):
        format_name_from_string("json")


# ---------------------------------------------------------------------------
# format_lines — RAW
# ---------------------------------------------------------------------------

def test_format_raw_writes_lines():
    buf = io.StringIO()
    count = format_lines(LINES, OutputFormat.RAW, out=buf)
    assert count == 3
    assert buf.getvalue() == "".join(LINES)


def test_format_raw_adds_newline_if_missing():
    buf = io.StringIO()
    format_lines(["no newline"], OutputFormat.RAW, out=buf)
    assert buf.getvalue().endswith("\n")


def test_format_raw_empty():
    buf = io.StringIO()
    count = format_lines([], OutputFormat.RAW, out=buf)
    assert count == 0
    assert buf.getvalue() == ""


# ---------------------------------------------------------------------------
# format_lines — NUMBERED
# ---------------------------------------------------------------------------

def test_format_numbered_prefixes_line_numbers():
    buf = io.StringIO()
    count = format_lines(LINES, OutputFormat.NUMBERED, out=buf)
    assert count == 3
    output = buf.getvalue()
    assert "       1  " in output
    assert "       2  " in output
    assert "       3  " in output


def test_format_numbered_custom_start():
    buf = io.StringIO()
    format_lines(LINES[:1], OutputFormat.NUMBERED, out=buf, start_number=42)
    assert "      42  " in buf.getvalue()


# ---------------------------------------------------------------------------
# format_lines — COUNT
# ---------------------------------------------------------------------------

def test_format_count_writes_number():
    buf = io.StringIO()
    count = format_lines(LINES, OutputFormat.COUNT, out=buf)
    assert count == 3
    assert buf.getvalue().strip() == "3"


def test_format_count_empty():
    buf = io.StringIO()
    count = format_lines([], OutputFormat.COUNT, out=buf)
    assert count == 0
    assert buf.getvalue().strip() == "0"


# ---------------------------------------------------------------------------
# default out=None uses stdout (smoke test via capsys)
# ---------------------------------------------------------------------------

def test_format_raw_default_stdout(capsys):
    format_lines(["hello\n"], OutputFormat.RAW)
    captured = capsys.readouterr()
    assert "hello" in captured.out
