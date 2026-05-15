"""Support for extracting context lines around matched time-range segments."""

from typing import Iterator, List, Tuple


def extract_with_context(
    lines: List[str],
    before: int = 0,
    after: int = 0,
) -> Iterator[Tuple[int, str, bool]]:
    """Yield (line_number, line, is_match) tuples with optional context lines.

    Args:
        lines: All lines from the matched segment (already filtered by time range).
        before: Number of context lines to include before the first matched line.
        after: Number of context lines to include after the last matched line.

    Yields:
        Tuples of (1-based line index within output, line text, is_in_core_range).
    """
    if not lines:
        return

    total = len(lines)
    start_idx = max(0, before)  # lines before 'before' are context
    end_idx = max(0, total - after)  # lines after 'end_idx' are trailing context

    for i, line in enumerate(lines):
        is_core = start_idx <= i < end_idx
        yield (i + 1, line, is_core)


def attach_context_from_file(
    file_obj,
    match_start_offset: int,
    match_end_offset: int,
    before: int = 0,
    after: int = 0,
) -> List[str]:
    """Read lines from file_obj, prepending/appending context lines around the
    matched byte range [match_start_offset, match_end_offset).

    Args:
        file_obj: A seekable, readable file-like object.
        match_start_offset: Byte offset where matched content starts.
        match_end_offset: Byte offset where matched content ends.
        before: Number of lines to include before match_start_offset.
        after: Number of lines to include after match_end_offset.

    Returns:
        List of lines including context.
    """
    result: List[str] = []

    if before > 0 and match_start_offset > 0:
        file_obj.seek(0)
        pre_bytes = file_obj.read(match_start_offset)
        pre_lines = pre_bytes.splitlines(keepends=True)
        context_before = pre_lines[-before:] if len(pre_lines) >= before else pre_lines
        result.extend(line.decode(errors="replace") if isinstance(line, bytes) else line
                      for line in context_before)

    file_obj.seek(match_start_offset)
    core_bytes = file_obj.read(match_end_offset - match_start_offset)
    core_lines = core_bytes.splitlines(keepends=True)
    result.extend(line.decode(errors="replace") if isinstance(line, bytes) else line
                  for line in core_lines)

    if after > 0:
        post_bytes = file_obj.read()  # read remainder after match_end_offset
        post_lines = post_bytes.splitlines(keepends=True)
        context_after = post_lines[:after]
        result.extend(line.decode(errors="replace") if isinstance(line, bytes) else line
                      for line in context_after)

    return result
