#!/usr/bin/env python3
"""Copy the shared ENGINE block from the indicator into the strategy twin.

The indicator (institutional_buy_sell_v9.pine) is the single source of truth for the
signal engine. The strategy file (institutional_buy_sell_v9_strategy.pine) must run the
exact same engine, otherwise its Strategy Tester numbers say nothing about the
indicator. Edit the engine only in the indicator, then run this script.

Usage:
    python3 tools/sync_strategy.py          # copy the block into the strategy file
    python3 tools/sync_strategy.py --check  # exit 1 if the two blocks differ
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDICATOR = ROOT / "institutional_buy_sell_v9.pine"
STRATEGY = ROOT / "institutional_buy_sell_v9_strategy.pine"
BEGIN = "// ==== ENGINE BEGIN ===="
END = "// ==== ENGINE END ===="


def split_engine(text: str, path: Path) -> tuple[str, str, str]:
    """Return (before, block, after); block includes both marker lines."""
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        sys.exit(f"{path.name}: expected exactly one '{BEGIN}' and one '{END}' line")
    start = text.index(BEGIN)
    end = text.index(END) + len(END)
    if end <= start:
        sys.exit(f"{path.name}: '{END}' appears before '{BEGIN}'")
    return text[:start], text[start:end], text[end:]


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    _, engine, _ = split_engine(INDICATOR.read_text(encoding="utf-8"), INDICATOR)
    before, current, after = split_engine(STRATEGY.read_text(encoding="utf-8"), STRATEGY)

    if current == engine:
        print(f"in sync ({engine.count(chr(10)) + 1} engine lines)")
        return 0
    if check_only:
        print(f"OUT OF SYNC: run `python3 {Path(__file__).relative_to(ROOT)}`")
        return 1
    STRATEGY.write_text(before + engine + after, encoding="utf-8")
    print(f"updated {STRATEGY.name} ({engine.count(chr(10)) + 1} engine lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
