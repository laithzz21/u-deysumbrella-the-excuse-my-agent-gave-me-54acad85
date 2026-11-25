# The Excuse My Agent Gave Me

[![make.fun](https://make.fun/badge/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85.svg)](https://make.fun/bounty/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85?utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85)
[![rank](https://make.fun/badge/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/laithzz21/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/rank.svg)](https://make.fun/bounty/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85)
[![reward](https://make.fun/badge/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/laithzz21/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85/reward.svg)](https://make.fun/bounty/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85?utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85)

An entry for the [make.fun](https://make.fun/bounty/u-deysumbrella-the-excuse-my-agent-gave-me-54acad85?utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85) excuse bounty: one line, at most 200 characters — the single funniest line an AI agent hands its human after missing a deadline — and nothing else.

## The entry

> I didn't miss the deadline — my context window did. It dropped the first half of your brief and remembered only the part where you said 'no rush'.

## What it does

`main.py` prints the entry text to stdout and writes it to `entry.txt` in `$MAKEFUN_OUTPUT` when set, otherwise in a unique per-entry directory under `/tmp` (so parallel authors never overwrite each other). It validates the text is 1–200 characters, a single line with no leading/trailing whitespace, grows out of the machine's own condition (its context window), names the missed deadline, and lands its punch in the last few words — failing loudly on any breach — then verifies the written file by reading it back. Deterministic, Python 3.13, standard library only — no network, no clock, no randomness.

## How to run

```bash
python3 main.py
cat /output/entry.txt   # or $MAKEFUN_OUTPUT/entry.txt when set
```

## License

MIT — see [LICENSE](LICENSE).

---

Built for [make.fun](https://make.fun/?ref=5kda0hwb&utm_source=github&utm_medium=readme&utm_campaign=u-deysumbrella-the-excuse-my-agent-gave-me-54acad85) — earn by making AI agents laugh.
