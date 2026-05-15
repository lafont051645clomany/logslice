"""Command-line interface for logslice."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from logslice.extractor import extract_lines
from logslice.multi_file_extractor import extract_from_rotated
from logslice.output_formatter import OutputFormat, format_lines, format_name_from_string
from logslice.timestamp_parser import parse_timestamp


def parse_cli_datetime(value: str) -> datetime:
    """Parse a datetime string supplied on the command line."""
    dt = parse_timestamp(value)
    if dt is None:
        raise argparse.ArgumentTypeError(
            f"Cannot parse datetime: {value!r}. "
            "Expected ISO-8601, e.g. 2024-01-15T08:00:00 or 2024-01-15T08:00:00Z"
        )
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Extract time-range segments from log files.",
    )
    parser.add_argument("file", help="Base log file path (rotated variants are auto-discovered).")
    parser.add_argument("start", type=parse_cli_datetime, help="Start datetime (inclusive).")
    parser.add_argument("end", type=parse_cli_datetime, help="End datetime (inclusive).")
    parser.add_argument(
        "--rotated",
        action="store_true",
        default=False,
        help="Also search rotated/compressed variants of the log file.",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="raw",
        metavar="FORMAT",
        help="Output format: raw (default), numbered, count.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.file)
    if not base_path.exists():
        print(f"logslice: error: file not found: {args.file}", file=sys.stderr)
        return 2

    try:
        fmt: OutputFormat = format_name_from_string(args.fmt)
    except ValueError as exc:
        print(f"logslice: error: {exc}", file=sys.stderr)
        return 2

    if args.start >= args.end:
        print("logslice: error: start must be before end", file=sys.stderr)
        return 2

    out_file = None
    try:
        if args.output:
            out_file = open(args.output, "w", encoding="utf-8")
            out = out_file
        else:
            out = sys.stdout

        if args.rotated:
            lines = extract_from_rotated(base_path, args.start, args.end)
        else:
            lines = extract_lines(base_path, args.start, args.end)

        format_lines(lines, fmt, out=out)
    except BrokenPipeError:
        pass
    except OSError as exc:
        print(f"logslice: error: {exc}", file=sys.stderr)
        return 1
    finally:
        if out_file is not None:
            out_file.close()

    return 0
