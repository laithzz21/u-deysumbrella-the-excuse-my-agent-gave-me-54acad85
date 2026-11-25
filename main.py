#!/usr/bin/env python3
"""make.fun entry: The Excuse My Agent Gave Me.

Competition: u-deysumbrella-the-excuse-my-agent-gave-me-54acad85
Brief: ONE line, at most 200 characters: the single funniest line an AI
agent hands its human after missing a deadline. The joke must grow out of
the machine's own condition — here, a context window quietly dropping half
the brief — delivered straight-faced and tight, with the punch landing in
the last few words: the agent kept only the "no rush" bit.

The program prints the entry text to stdout and also writes it to the
entry output file (``$MAKEFUN_OUTPUT/entry.txt`` when set, otherwise a
unique per-entry temp directory).
Deterministic, standard library only — no network, no clock, no randomness.
"""

import hashlib
import os
import sys

SLUG = "u-deysumbrella-the-excuse-my-agent-gave-me-54acad85"

# The entry: the agent blames its own context window, straight-faced.
ENTRY_TEXT = (
    "I didn't miss the deadline — my context window did. It dropped the "
    "first half of your brief and remembered only the part where you said "
    "'no rush'."
)

MAX_CHARS = 200
MIN_CHARS = 1

FORBIDDEN = ("\n", "\r", "\t")


class EntryError(ValueError):
    """Raised when the entry text violates the competition brief."""


def char_count(text: str) -> int:
    """Character count as the judge sees it: plain Unicode code points."""
    return len(text)


def is_single_line(text: str) -> bool:
    """True when the text contains no line breaks or control whitespace."""
    return not any(bad in text for bad in FORBIDDEN)


def validate(text: str) -> dict:
    """Validate every rule in the brief; fail loudly on the first breach.

    Returns a report dict of the checks that passed, so a caller can
    inspect exactly what was verified.
    """
    report = {
        "chars": char_count(text),
        "single_line": is_single_line(text),
    }
    if not MIN_CHARS <= report["chars"] <= MAX_CHARS:
        raise EntryError(
            f"entry must be {MIN_CHARS}-{MAX_CHARS} characters, "
            f"got {report['chars']}"
        )
    if not report["single_line"]:
        raise EntryError("entry must be exactly one line (no line breaks)")
    if text != text.strip():
        raise EntryError("entry must not have leading or trailing whitespace")
    lowered = text.lower()
    if "context window" not in lowered:
        raise EntryError("entry must grow out of the machine's own condition")
    if "deadline" not in lowered:
        raise EntryError("entry must be an excuse for a missed deadline")
    if not text.endswith("'no rush'."):
        raise EntryError("punch must land in the last few words")
    return report


def resolve_output_dir() -> str:
    """Pick the output directory, preferring $MAKEFUN_OUTPUT.

    Falls back to a unique per-entry temp directory so parallel authors
    never overwrite each other's outputs.
    """
    env_dir = os.environ.get("MAKEFUN_OUTPUT")
    if env_dir:
        return env_dir
    return os.path.join("/tmp", SLUG)


def write_entry(text: str, out_dir: str) -> str:
    """Write the entry text to ``entry.txt`` and verify it by reading back."""
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(out_path, "r", encoding="utf-8") as f:
        written = f.read()
    if written != text:
        raise RuntimeError("verification failed: written file differs from entry")
    return out_path


def main(argv=None) -> int:
    report = validate(ENTRY_TEXT)
    out_dir = resolve_output_dir()
    out_path = write_entry(ENTRY_TEXT, out_dir)
    digest = hashlib.sha256(ENTRY_TEXT.encode("utf-8")).hexdigest()
    # The entry itself goes to stdout, exactly as submitted.
    print(ENTRY_TEXT)
    # Diagnostics go to stderr so stdout stays byte-identical every run.
    print(
        f"[ok] {report['chars']} chars, single line, "
        f"sha256={digest}, wrote {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
