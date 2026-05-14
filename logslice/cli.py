"""Command-line interface for logslice."""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from logslice.extractor import extract_lines
from logslice.timestamp_parser import parse_timestamp


DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
]


def parse_cli_datetime(value: str) -> datetime:
    """Parse a datetime string from CLI arguments."""
    for fmt in DATETIME_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Cannot parse datetime: {value!r}. "
        f"Expected formats: YYYY-MM-DD, YYYY-MM-DD HH:MM, YYYY-MM-DD HH:MM:SS"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Extract time-range segments from log files.",
    )
    parser.add_argument(
        "logfile",
        type=Path,
        help="Path to the log file to slice.",
    )
    parser.add_argument(
        "--start",
        type=parse_cli_datetime,
        default=None,
        metavar="DATETIME",
        help="Start of the time range (inclusive). Format: YYYY-MM-DD [HH:MM[:SS]]",
    )
    parser.add_argument(
        "--end",
        type=parse_cli_datetime,
        default=None,
        metavar="DATETIME",
        help="End of the time range (inclusive). Format: YYYY-MM-DD [HH:MM[:SS]]",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.logfile.exists():
        print(f"logslice: error: file not found: {args.logfile}", file=sys.stderr)
        return 2

    if args.start is None and args.end is None:
        print("logslice: error: at least one of --start or --end is required.", file=sys.stderr)
        return 2

    lines = extract_lines(args.logfile, start=args.start, end=args.end)

    if args.output:
        with args.output.open("w") as fh:
            for line in lines:
                fh.write(line)
    else:
        for line in lines:
            sys.stdout.write(line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
