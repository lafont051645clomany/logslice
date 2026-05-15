"""Tests for the transparent compressed/plain log file reader."""

import gzip
import pytest
from pathlib import Path

from logslice.compressed_reader import open_log_file, file_size


SAMPLE = b"line one\nline two\nline three\n"


@pytest.fixture()
def plain_log(tmp_path: Path) -> Path:
    p = tmp_path / "app.log"
    p.write_bytes(SAMPLE)
    return p


@pytest.fixture()
def gz_log(tmp_path: Path) -> Path:
    p = tmp_path / "app.log.gz"
    p.write_bytes(gzip.compress(SAMPLE))
    return p


def test_open_plain_reads_content(plain_log: Path) -> None:
    with open_log_file(plain_log) as fh:
        assert fh.read() == SAMPLE


def test_open_gz_reads_decompressed_content(gz_log: Path) -> None:
    fh = open_log_file(gz_log)
    assert fh.read() == SAMPLE


def test_open_gz_supports_seek(gz_log: Path) -> None:
    fh = open_log_file(gz_log)
    fh.seek(9)  # start of "line two\n"
    assert fh.read(8) == b"line two"


def test_open_plain_supports_seek(plain_log: Path) -> None:
    with open_log_file(plain_log) as fh:
        fh.seek(9)
        assert fh.read(8) == b"line two"


def test_file_size_plain(plain_log: Path) -> None:
    assert file_size(plain_log) == len(SAMPLE)


def test_file_size_gz_returns_decompressed_size(gz_log: Path) -> None:
    assert file_size(gz_log) == len(SAMPLE)
