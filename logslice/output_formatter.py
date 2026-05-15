"""Output formatting for extracted log lines."""

from __future__ import annotations

import sys
from enum import Enum
from typing import Iterable, TextIO


class OutputFormat(str, Enum):
    RAW = "raw"
    NUMBERED = "numbered"
    COUNT = "count"


def format_lines(
    lines: Iterable[str],
    fmt: OutputFormat = OutputFormat.RAW,
    out: TextIO | None = None,
    start_number: int = 1,
) -> int:
    """Write *lines* to *out* (default: stdout) using the given format.

    Returns the total number of lines written.
    """
    if out is None:
        out = sys.stdout

    count = 0

    if fmt == OutputFormat.COUNT:
        # Consume the iterable just to count; write nothing yet.
        for _ in lines:
            count += 1
        out.write(f"{count}\n")
        return count

    for i, line in enumerate(lines, start=start_number):
        count += 1
        if fmt == OutputFormat.NUMBERED:
            out.write(f"{i:>8}  {line}")
        else:  # RAW
            out.write(line)
        # Ensure each line ends with a newline.
        if not line.endswith("\n"):
            out.write("\n")

    return count


def format_name_from_string(value: str) -> OutputFormat:
    """Parse a format name string, raising ValueError for unknown values."""
    try:
        return OutputFormat(value.lower())
    except ValueError:
        valid = ", ".join(f.value for f in OutputFormat)
        raise ValueError(f"Unknown output format {value!r}. Valid options: {valid}")
