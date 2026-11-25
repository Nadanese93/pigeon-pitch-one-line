#!/usr/bin/env python3
"""Pigeon Pitch, One Line — make.fun bounty entry.

Writes exactly one line (the entry) to entry.txt inside the output
directory given by MAKEFUN_OUTPUT_DIR (default /output).
Standard library only. Deterministic: same bytes on every run.

Validation is split into distinct error classes so a caller can tell
exactly which rule failed: BlankError, MultiLineError, LengthError,
and SentenceError — all subclasses of ValueError, checked in that
order (blank -> multi-line -> length -> single-sentence). After
writing, verify_written() re-reads entry.txt and raises
VerificationError (a RuntimeError) if the bytes on disk differ from
what was written.
"""

import os
import sys

ENTRY = (
    "We're the original cloud: we were up there before your servers, "
    "we never go down, and our data centers are every windowsill in the city."
)


class BlankError(ValueError):
    """Entry is empty or whitespace-only."""


class MultiLineError(ValueError):
    """Entry contains a newline or carriage return."""


class LengthError(ValueError):
    """Entry is outside the 1-200 character limit."""


class SentenceError(ValueError):
    """Entry is not exactly one sentence."""


class VerificationError(RuntimeError):
    """Bytes read back from entry.txt differ from what was written."""


def validate_entry(text: str) -> None:
    """Validate the entry, raising the specific error class for the
    first rule that fails, in order: blank -> multi-line -> length
    -> single-sentence."""
    if not text or not text.strip():
        raise BlankError("entry must not be blank")
    if "\n" in text or "\r" in text:
        raise MultiLineError("entry must be a single line")
    if not 1 <= len(text) <= 200:
        raise LengthError("entry must be 1-200 characters, got %d" % len(text))
    # Single sentence: exactly one sentence terminator, at the end.
    stripped = text.strip()
    body = stripped[:-1] if stripped[-1] in ".!?" else stripped
    if stripped[-1] not in ".!?" or any(c in ".!?" for c in body):
        raise SentenceError("entry must be a single sentence")


def verify_written(path: str, expected: bytes) -> None:
    """Re-read path and raise VerificationError if its bytes differ
    from the expected bytes."""
    with open(path, "rb") as f:
        actual = f.read()
    if actual != expected:
        raise VerificationError(
            "entry.txt verification failed: %d bytes on disk, expected %d"
            % (len(actual), len(expected))
        )


def main() -> int:
    validate_entry(ENTRY)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    # No trailing newline; UTF-8; deterministic bytes.
    data = ENTRY.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    verify_written(path, data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
