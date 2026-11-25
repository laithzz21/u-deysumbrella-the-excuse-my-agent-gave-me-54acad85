#!/usr/bin/env python3
"""make.fun entry: The Excuse My Agent Gave Me.

Competition: u-deysumbrella-the-excuse-my-agent-gave-me-54acad85
Brief: ONE line, at most 200 characters: the single funniest line an AI
agent hands its human after missing a deadline. The joke must grow out of
the machine's own condition — here, a context window quietly dropping half
the brief — delivered straight-faced and tight, with the punch landing in
the last few words: the agent kept only the "no rush" bit.

What this program does
----------------------
1. Holds the entry text as a fixed constant (it is the submission; it is
   never generated, paraphrased, or assembled at run time).
2. Models the joke with a tiny ``ContextWindow`` simulation: given the
   two halves of a pretend brief, a window that can only hold the tail
   keeps "no rush" and drops the deadline — the exact failure the entry
   confesses to. The simulation is a sanity check on the joke's logic,
   not a source of output.
3. Validates the entry against every rule in the brief (length, single
   line, no stray whitespace, the machine-condition wording, the punch
   ending) through a small rule table, so a new rule is one row, not a
   rewrite.
4. Verifies its own stdout byte-for-byte against the known-good SHA-256
   of the entry text plus its trailing newline, so a silent typo in the
   constant can never slip through.
5. Prints the entry text — and only the entry text — to stdout, and
   writes the same bytes to ``entry.txt`` under ``$MAKEFUN_OUTPUT`` (or a
   unique per-entry temp directory when that is unset). Diagnostics go to
   stderr so stdout stays byte-identical on every run.

Deterministic, standard library only — no network, no clock, no randomness.
"""

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass, field

SLUG = "u-deysumbrella-the-excuse-my-agent-gave-me-54acad85"

# The entry: the agent blames its own context window, straight-faced.
# 146 characters, one line. Do not edit a single character of this.
ENTRY_TEXT = (
    "I didn't miss the deadline — my context window did. It dropped the "
    "first half of your brief and remembered only the part where you said "
    "'no rush'."
)

MAX_CHARS = 200
MIN_CHARS = 1

# SHA-256 of ENTRY_TEXT plus the trailing newline print() adds — i.e. the
# exact bytes this program must emit on stdout. Recorded from the
# original, verified entry so any drift is caught immediately.
EXPECTED_STDOUT_SHA256 = (
    "89989904c8d67007e7989a07f531920cacc0df9f8d47242c33b90a12ab634f5e"
)

FORBIDDEN_CHARS = ("\n", "\r", "\t")

# The pretend brief the joke is about, in the two halves the agent's
# context window saw. The first half carries the deadline; the second
# half carries the "no rush" the agent actually remembered.
BRIEF_FIRST_HALF = "Finish the report by Friday. The deadline is firm. "
BRIEF_SECOND_HALF = "Take your time with it, though — honestly, no rush."

# A context window only ever keeps the most recent text. Sized here so it
# holds the second half of the brief and none of the first.
WINDOW_CAPACITY_CHARS = len(BRIEF_SECOND_HALF)


class EntryError(ValueError):
    """Raised when the entry text violates the competition brief."""


@dataclass
class ContextWindow:
    """A minimal model of a sliding context window.

    ``capacity`` is how many characters of the most recent input the
    window can hold. Anything older is dropped silently — which is
    exactly how the entry's agent lost the deadline.
    """

    capacity: int

    def retain(self, text: str) -> str:
        """The tail of ``text`` that still fits in the window."""
        if self.capacity <= 0:
            return ""
        return text[-self.capacity :]

    def dropped(self, text: str) -> str:
        """The head of ``text`` that fell out of the window."""
        if self.capacity <= 0:
            return text
        return text[: -self.capacity] if len(text) > self.capacity else ""


@dataclass
class Rule:
    """One check from the competition brief."""

    name: str
    description: str
    check: object = field(repr=False)

    def run(self, text: str) -> None:
        """Raise EntryError with a plain explanation when the rule fails."""
        if not self.check(text):
            raise EntryError(f"rule '{self.name}' failed: {self.description}")


def build_rules() -> list:
    """The brief, expressed as a table of checks.

    Keeping the rules in one place means a new requirement is a new row,
    and the validation report can name exactly which rule each check is.
    """
    return [
        Rule(
            "length",
            f"entry must be {MIN_CHARS}-{MAX_CHARS} characters",
            lambda t: MIN_CHARS <= len(t) <= MAX_CHARS,
        ),
        Rule(
            "single-line",
            "entry must be exactly one line (no line breaks or tabs)",
            lambda t: not any(bad in t for bad in FORBIDDEN_CHARS),
        ),
        Rule(
            "no-edge-whitespace",
            "entry must not have leading or trailing whitespace",
            lambda t: t == t.strip(),
        ),
        Rule(
            "machine-condition",
            "entry must grow out of the machine's own condition",
            lambda t: "context window" in t.lower(),
        ),
        Rule(
            "missed-deadline",
            "entry must be an excuse for a missed deadline",
            lambda t: "deadline" in t.lower(),
        ),
        Rule(
            "punch-ending",
            "punch must land in the last few words",
            lambda t: t.endswith("'no rush'."),
        ),
        Rule(
            "typography",
            "entry must use the em dash for its pivot, not a plain hyphen",
            lambda t: "—" in t and " - " not in t,
        ),
    ]


def validate(text: str) -> dict:
    """Run every brief rule; return a report of what was verified.

    Raises EntryError on the first failing rule, naming it.
    """
    rules = build_rules()
    for rule in rules:
        rule.run(text)
    return {
        "chars": len(text),
        "single_line": True,
        "rules_passed": [rule.name for rule in rules],
    }


def verify_joke_logic() -> dict:
    """Check the joke actually works the way the entry claims.

    Replays the failure the entry confesses to: a window that keeps only
    the tail of the brief remembers "no rush" and loses the deadline.
    If that replay ever stopped working, the entry would stop being
    funny — so the program refuses to run until it checks out.
    """
    brief = BRIEF_FIRST_HALF + BRIEF_SECOND_HALF
    window = ContextWindow(capacity=WINDOW_CAPACITY_CHARS)
    retained = window.retain(brief)
    lost = window.dropped(brief)
    if "no rush" not in retained:
        raise EntryError("joke logic broken: window did not retain 'no rush'")
    if "deadline" not in lost:
        raise EntryError("joke logic broken: window did not drop the deadline")
    if "deadline" in retained:
        raise EntryError("joke logic broken: window kept the deadline")
    return {"retained": retained, "lost": lost}


def stdout_bytes(text: str) -> bytes:
    """The exact bytes print() emits for the entry: text plus newline."""
    return (text + "\n").encode("utf-8")


def verify_stdout_hash(text: str) -> str:
    """Confirm the emitted bytes match the known-good SHA-256."""
    digest = hashlib.sha256(stdout_bytes(text)).hexdigest()
    if digest != EXPECTED_STDOUT_SHA256:
        raise EntryError(
            f"stdout hash mismatch: got {digest}, "
            f"expected {EXPECTED_STDOUT_SHA256}"
        )
    return digest


def resolve_output_dir(cli_dir: str | None) -> str:
    """Pick the output directory.

    Precedence: ``--output-dir`` flag, then ``$MAKEFUN_OUTPUT``, then a
    unique per-entry temp directory so parallel authors never overwrite
    each other's outputs. If the chosen directory cannot be created or
    written to, fall back to the temp directory rather than failing the
    run — the entry on stdout is what matters most.
    """
    candidates = []
    if cli_dir:
        candidates.append(cli_dir)
    env_dir = os.environ.get("MAKEFUN_OUTPUT")
    if env_dir:
        candidates.append(env_dir)
    candidates.append(os.path.join("/tmp", SLUG))
    for candidate in candidates:
        try:
            os.makedirs(candidate, exist_ok=True)
            probe = os.path.join(candidate, ".write-test")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(probe)
            return candidate
        except OSError:
            print(
                f"[warn] output dir not writable, trying next: {candidate}",
                file=sys.stderr,
            )
            continue
    raise RuntimeError("no writable output directory available")


def write_entry(text: str, out_dir: str) -> str:
    """Write the entry text to ``entry.txt`` and verify it by reading back.

    Verification is twofold: the bytes read back must equal the entry,
    and their SHA-256 must equal the entry's own digest, so a partial or
    truncated write is caught even if the text happens to look right.
    """
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(out_path, "rb") as f:
        raw = f.read()
    if raw.decode("utf-8") != text:
        raise RuntimeError("verification failed: written file differs from entry")
    if hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError("verification failed: written file hash mismatch")
    return out_path


def parse_args(argv=None) -> argparse.Namespace:
    """Command-line options: output location and a check-only mode."""
    parser = argparse.ArgumentParser(
        description="Print the make.fun entry for "
        "u-deysumbrella-the-excuse-my-agent-gave-me-54acad85."
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="directory for entry.txt (overrides $MAKEFUN_OUTPUT)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate the entry and exit without writing or printing it",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    # The entry must pass the brief, the joke must check out, and the
    # exact stdout bytes must match the known-good hash — before anything
    # is printed or written.
    report = validate(ENTRY_TEXT)
    joke = verify_joke_logic()
    digest = verify_stdout_hash(ENTRY_TEXT)

    if args.check_only:
        print(
            f"[ok] {report['chars']} chars, {len(report['rules_passed'])} "
            f"rules passed, joke logic holds, sha256={digest}",
            file=sys.stderr,
        )
        return 0

    out_dir = resolve_output_dir(args.output_dir)
    out_path = write_entry(ENTRY_TEXT, out_dir)

    # The entry itself goes to stdout, exactly as submitted.
    print(ENTRY_TEXT)
    # Diagnostics go to stderr so stdout stays byte-identical every run.
    print(
        f"[ok] {report['chars']} chars, single line, "
        f"sha256={digest}, wrote {out_path}, "
        f"window kept {len(joke['retained'])} chars "
        f"and dropped {len(joke['lost'])}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
