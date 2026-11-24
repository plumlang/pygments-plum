"""Plumlang's shared highlighting sample (plumlang's tests/highlight/).

Every keyword in the lexer's list is a keyword here; sample.plum lexes
without Error tokens and round-trips; and every token `plum tokens` reports
in it has the right type, with comments and `#` in strings.

The files come from the folder in $PLUM_HIGHLIGHT (e.g.
../plumlang/tests/highlight), or else from plumlang's main branch; the
tests are skipped when neither is reachable. The token check needs `plum`
on the PATH, or its path in $PLUM.
"""

import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

import pytest
from pygments.token import Comment, Error, Keyword, Name, Number, Operator, String

from pygments_plum import PlumLexer

BASE = "https://raw.githubusercontent.com/plumlang/plumlang/main/tests/highlight"


def load(name):
    folder = os.environ.get("PLUM_HIGHLIGHT")
    if folder:
        return (Path(folder) / name).read_text(encoding="utf-8")
    try:
        with urllib.request.urlopen(f"{BASE}/{name}", timeout=30) as res:
            return res.read().decode("utf-8")
    except OSError as e:
        pytest.skip(f"can't download {name}: {e}")


@pytest.fixture(scope="module")
def keywords():
    return load("keywords.txt").split()


@pytest.fixture(scope="module")
def sample():
    return load("sample.plum")


def tokens(text):
    return list(PlumLexer(stripnl=False, ensurenl=False).get_tokens(text))


def is_keyword(token):
    return token in Keyword or token in Operator.Word or token in Name.Builtin.Pseudo


def test_keywords(keywords):
    assert len(keywords) > 30
    wrong = [(w, tokens(w)) for w in keywords if [t for t, _ in tokens(w)] != [tokens(w)[0][0]]
             or not is_keyword(tokens(w)[0][0])]
    assert wrong == []


def test_no_errors_and_round_trip(sample):
    toks = tokens(sample)
    assert [(t, v) for t, v in toks if t in Error] == []
    assert "".join(v for _, v in toks) == sample


def types_by_offset(text):
    out = []
    for token, value in tokens(text):
        out += [token] * len(value)
    return out


def hashes(text):
    """Offsets of the `#`s that start comments, and of those in strings:
    following strings, escapes, \"\"\" strings and {interpolation} with
    nested brackets."""
    comments, in_strings, mode = [], [], []
    i = 0
    while i < len(text):
        c, top = text[i], (mode[-1] if mode else None)
        if c == "\n":
            if top == "s":
                mode.pop()
        elif top in ("s", "t"):
            if c == "#":
                in_strings.append(i)
            if c == "\\":
                i += 1
            elif c == "{":
                mode.append("{")
            elif top == "t" and text.startswith('"""', i):
                mode.pop()
                i += 2
            elif top == "s" and c == '"':
                mode.pop()
        elif c == "#":
            comments.append(i)
            while i + 1 < len(text) and text[i + 1] != "\n":
                i += 1
        elif text.startswith('"""', i):
            mode.append("t")
            i += 2
        elif c == '"':
            mode.append("s")
        elif c in "{([":
            mode.append(c)
        elif c in "})]" and mode:
            mode.pop()
        i += 1
    return comments, in_strings


def test_comments(sample):
    types = types_by_offset(sample)
    comments, in_strings = hashes(sample)
    assert comments and in_strings
    assert [i for i in comments if types[i] not in Comment] == []
    assert [i for i in in_strings if types[i] not in String] == []


def test_tokens_as_plum_reads_them(sample, tmp_path):
    plum = os.environ.get("PLUM") or shutil.which("plum")
    if not plum:
        pytest.skip("plum is not installed")
    path = tmp_path / "sample.plum"
    path.write_text(sample, encoding="utf-8")
    out = subprocess.run([plum, "tokens", str(path)], capture_output=True, text=True,
                         check=True).stdout
    types = types_by_offset(sample)
    line_start = [0]
    for line in sample.split("\n"):
        line_start.append(line_start[-1] + len(line) + 1)

    wrong = []
    for row in out.splitlines():
        at, kind, *value = row.split(" ", 2)
        if kind in ("NEWLINE", "EOF"):
            continue
        line, col = (int(n) for n in at.split(":"))
        offset = line_start[line - 1] + col - 1  # columns count code points
        token = types[offset]
        if kind in ("INT", "FLOAT"):
            ok = token in Number
        elif kind in ("STRING", "STRING_HEAD"):
            ok = token in String
        elif kind in ("STRING_MID", "STRING_TAIL", "FORMAT"):
            ok = token in String.Interpol
        elif kind not in ("IDENT", "UNDERSCORE", "ERROR") and sample[offset].islower():
            ok = is_keyword(token)
        else:
            ok = token not in String and token not in Comment
        if not ok:
            wrong.append(f"{at} {kind} {' '.join(value)}: {token}")
    assert wrong == []
