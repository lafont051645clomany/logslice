"""Tests for rotated_files discovery and ordering utilities."""

import gzip
import os
import pytest
from pathlib import Path

from logslice.rotated_files import find_rotated_files, is_compressed, _rotation_key


@pytest.fixture()
def log_dir(tmp_path: Path) -> Path:
    """Create a realistic rotated log hierarchy."""
    base = tmp_path / "app.log"
    base.write_bytes(b"current log\n")
    (tmp_path / "app.log.1").write_bytes(b"rotation 1\n")
    (tmp_path / "app.log.2").write_bytes(b"rotation 2\n")
    gz = tmp_path / "app.log.3.gz"
    gz.write_bytes(gzip.compress(b"rotation 3\n"))
    # A file that should NOT be picked up
    (tmp_path / "other.log").write_bytes(b"unrelated\n")
    return tmp_path


def test_find_rotated_files_order(log_dir: Path) -> None:
    base = log_dir / "app.log"
    files = find_rotated_files(str(base))
    names = [f.name for f in files]
    assert names == ["app.log", "app.log.1", "app.log.2", "app.log.3.gz"]


def test_find_rotated_files_excludes_unrelated(log_dir: Path) -> None:
    base = log_dir / "app.log"
    files = find_rotated_files(str(base))
    assert all("other" not in f.name for f in files)


def test_find_rotated_files_missing_base(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        find_rotated_files(str(tmp_path / "nonexistent.log"))


def test_find_rotated_files_single(tmp_path: Path) -> None:
    """When no rotated siblings exist, only the base file is returned."""
    base = tmp_path / "solo.log"
    base.write_bytes(b"only log\n")
    files = find_rotated_files(str(base))
    assert files == [base]


def test_find_rotated_files_returns_path_objects(log_dir: Path) -> None:
    """find_rotated_files should always return a list of Path objects."""
    base = log_dir / "app.log"
    files = find_rotated_files(str(base))
    assert all(isinstance(f, Path) for f in files)


def test_is_compressed(tmp_path: Path) -> None:
    assert is_compressed(tmp_path / "app.log.gz") is True
    assert is_compressed(tmp_path / "app.log") is False
    assert is_compressed(tmp_path / "app.log.1") is False


def test_rotation_key_ordering() -> None:
    paths = [
        Path("app.log.2"),
        Path("app.log"),
        Path("app.log.1"),
        Path("app.log.3.gz"),
    ]
    paths.sort(key=_rotation_key)
    assert [p.name for p in paths] == [
        "app.log", "app.log.1", "app.log.2", "app.log.3.gz"
    ]
