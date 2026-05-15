"""Core extraction logic: read a byte range from a log file as lines."""

from typing import IO, Iterator, List, Optional

from logslice.binary_search import find_start_offset, find_end_offset
from logslice.context_lines import attach_context_from_file


def extract_lines(
    file_obj: IO[bytes],
    file_size: int,
    start_dt,
    end_dt,
    context_before: int = 0,
    context_after: int = 0,
) -> List[str]:
    """Extract lines from *file_obj* whose timestamps fall in [start_dt, end_dt].

    Optionally includes *context_before* lines immediately preceding the matched
    range and *context_after* lines immediately following it.

    Args:
        file_obj: Seekable binary file-like object.
        file_size: Total byte length of the file.
        start_dt: Inclusive lower bound (datetime).
        end_dt: Inclusive upper bound (datetime).
        context_before: Extra lines to prepend from before the match window.
        context_after: Extra lines to append from after the match window.

    Returns:
        List of decoded log lines (with newlines preserved).
    """
    start_offset = find_start_offset(file_obj, file_size, start_dt)
    end_offset = find_end_offset(file_obj, file_size, end_dt)

    if start_offset is None or end_offset is None:
        return []
    if start_offset >= end_offset:
        return []

    if context_before == 0 and context_after == 0:
        file_obj.seek(start_offset)
        raw = file_obj.read(end_offset - start_offset)
        lines = raw.splitlines(keepends=True)
        return [line.decode(errors="replace") for line in lines]

    return attach_context_from_file(
        file_obj,
        match_start_offset=start_offset,
        match_end_offset=end_offset,
        before=context_before,
        after=context_after,
    )


def iter_lines(
    file_obj: IO[bytes],
    file_size: int,
    start_dt,
    end_dt,
) -> Iterator[str]:
    """Streaming variant of extract_lines — yields one decoded line at a time.

    Useful for very large files where loading everything into memory is
    undesirable.  Context lines are not supported in streaming mode.

    Args:
        file_obj: Seekable binary file-like object.
        file_size: Total byte length of the file.
        start_dt: Inclusive lower bound (datetime).
        end_dt: Inclusive upper bound (datetime).

    Yields:
        Decoded log lines.
    """
    start_offset = find_start_offset(file_obj, file_size, start_dt)
    end_offset = find_end_offset(file_obj, file_size, end_dt)

    if start_offset is None or end_offset is None:
        return
    if start_offset >= end_offset:
        return

    file_obj.seek(start_offset)
    remaining = end_offset - start_offset
    while remaining > 0:
        raw_line = file_obj.readline(remaining)
        if not raw_line:
            break
        remaining -= len(raw_line)
        yield raw_line.decode(errors="replace")
