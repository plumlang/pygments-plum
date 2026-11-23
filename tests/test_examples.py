"""Every Plumlang program lexes without Error tokens and round-trips."""

import os
from pathlib import Path

import pytest
from pygments.token import Error

from pygments_plum import PlumLexer

HERE = Path(__file__).parent


def programs():
    """tests/examples/**/*.plum, plus a Plumlang checkout's examples and
    language tests when PLUM_SOURCE points at one."""
    found = sorted((HERE / "examples").rglob("*.plum"))
    source = os.environ.get("PLUM_SOURCE")
    if source:
        root = Path(source)
        for sub in ("examples", "tests/lang"):
            found += sorted((root / sub).rglob("*.plum"))
    return found


PROGRAMS = programs()


def test_found_programs():
    assert len(PROGRAMS) >= 50


@pytest.mark.parametrize(
    "path", PROGRAMS, ids=lambda p: str(p.relative_to(p.parents[2]))
)
def test_program(path):
    # newline="" keeps any \r\n; "replace" keeps the invalid-UTF-8 test file
    # readable (as Pygments itself does with encoding="guess").
    text = path.read_text(encoding="utf-8", errors="replace", newline="")
    lexer = PlumLexer(stripnl=False, ensurenl=False)
    tokens = list(lexer.get_tokens(text))

    errors = [(t, v) for t, v in tokens if t in Error]
    assert errors == []
    assert "".join(v for _, v in tokens) == text
