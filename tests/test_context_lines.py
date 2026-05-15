"""Tests for logslice.context_lines module."""

import io
import pytest
from logslice.context_lines import extract_with_context, attach_context_from_file


SAMPLE_LINES = [
    "line one\n",
    "line two\n",
    "line three\n",
    "line four\n",
    "line five\n",
]


def test_extract_with_context_no_context():
    result = list(extract_with_context(SAMPLE_LINES, before=0, after=0))
    assert len(result) == 5
    # All lines are core when before=0 and after=0
    assert all(is_core for _, _, is_core in result)


def test_extract_with_context_empty():
    result = list(extract_with_context([], before=2, after=2))
    assert result == []


def test_extract_with_context_line_numbers():
    result = list(extract_with_context(SAMPLE_LINES))
    line_numbers = [n for n, _, _ in result]
    assert line_numbers == [1, 2, 3, 4, 5]


def test_extract_with_context_before_marks_non_core():
    result = list(extract_with_context(SAMPLE_LINES, before=2, after=0))
    # First 2 lines are context (not core), rest are core
    is_core_flags = [is_core for _, _, is_core in result]
    assert is_core_flags == [False, False, True, True, True]


def test_extract_with_context_after_marks_non_core():
    result = list(extract_with_context(SAMPLE_LINES, before=0, after=2))
    is_core_flags = [is_core for _, _, is_core in result]
    assert is_core_flags == [True, True, True, False, False]


def test_extract_with_context_before_and_after():
    result = list(extract_with_context(SAMPLE_LINES, before=1, after=1))
    is_core_flags = [is_core for _, _, is_core in result]
    assert is_core_flags == [False, True, True, True, False]


def _make_file(*lines):
    """Create an in-memory binary file-like object from lines."""
    content = "".join(lines).encode()
    return io.BytesIO(content)


def test_attach_context_full_file_no_context():
    f = _make_file("alpha\n", "beta\n", "gamma\n")
    content = "".join(["alpha\n", "beta\n", "gamma\n"]).encode()
    result = attach_context_from_file(f, 0, len(content), before=0, after=0)
    assert result == ["alpha\n", "beta\n", "gamma\n"]


def test_attach_context_with_before():
    lines = ["pre1\n", "pre2\n", "match1\n", "match2\n"]
    encoded = ["".join(lines[:i]).encode() for i in range(len(lines) + 1)]
    pre_len = len("pre1\npre2\n")
    full = "".join(lines).encode()
    f = io.BytesIO(full)
    result = attach_context_from_file(f, pre_len, len(full), before=2, after=0)
    assert "pre1\n" in result
    assert "pre2\n" in result
    assert "match1\n" in result


def test_attach_context_with_after():
    lines = ["match1\n", "match2\n", "post1\n", "post2\n"]
    full = "".join(lines).encode()
    match_end = len("match1\nmatch2\n")
    f = io.BytesIO(full)
    result = attach_context_from_file(f, 0, match_end, before=0, after=2)
    assert "match1\n" in result
    assert "post1\n" in result
    assert "post2\n" in result


def test_attach_context_after_clamps_to_available():
    lines = ["match\n", "only_one_after\n"]
    full = "".join(lines).encode()
    match_end = len("match\n")
    f = io.BytesIO(full)
    result = attach_context_from_file(f, 0, match_end, before=0, after=10)
    assert result == ["match\n", "only_one_after\n"]
