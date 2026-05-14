"""Timestamp detection and parsing utilities for log lines."""

import re
from datetime import datetime
from typing import Optional

# Common log timestamp patterns ordered by specificity
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-01-15T13:45:00.123Z or 2024-01-15T13:45:00+00:00
    (
        r"(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)",
        ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"],
    ),
    # Common syslog: Jan 15 13:45:00
    (
        r"(?P<ts>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})",
        ["%b %d %H:%M:%S", "%b  %d %H:%M:%S"],
    ),
    # Apache/Nginx: 15/Jan/2024:13:45:00 +0000
    (
        r"(?P<ts>\d{2}/[A-Z][a-z]{2}/\d{4}:\d{2}:\d{2}:\d{2}\s[+-]\d{4})",
        ["%d/%b/%Y:%H:%M:%S %z"],
    ),
    # Simple datetime: 2024-01-15 13:45:00
    (
        r"(?P<ts>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})",
        ["%Y-%m-%d %H:%M:%S"],
    ),
]

_COMPILED_PATTERNS = [
    (re.compile(pattern), fmts) for pattern, fmts in TIMESTAMP_PATTERNS
]


def parse_line_timestamp(line: str) -> Optional[datetime]:
    """Extract and parse the first timestamp found in a log line.

    Returns a naive or aware datetime, or None if no timestamp is found.
    """
    for regex, formats in _COMPILED_PATTERNS:
        match = regex.search(line)
        if not match:
            continue
        raw = match.group("ts")
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
    return None


def parse_timestamp(value: str) -> datetime:
    """Parse a user-supplied timestamp string into a datetime object.

    Supports ISO 8601 and common date/time formats.
    Raises ValueError if the string cannot be parsed.
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(
        f"Unable to parse timestamp {value!r}. "
        "Expected formats: YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, or ISO 8601."
    )
