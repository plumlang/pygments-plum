"""The tokens of particular constructs."""

import pytest
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Text,
    Whitespace,
)

from pygments_plum import PlumLexer


def lex(code):
    """The tokens of `code`, without whitespace, merging neighbours of the
    same type."""
    out = []
    for token, value in PlumLexer().get_tokens(code):
        if token in Whitespace or (token in Text and value.isspace()):
            continue
        if out and out[-1][0] is token:
            out[-1] = (token, out[-1][1] + value)
        else:
            out.append((token, value))
    return out


def kinds(code):
    return dict((value, token) for token, value in lex(code))


# Keywords


@pytest.mark.parametrize(
    "word, token",
    [
        ("plant", Keyword.Declaration),
        ("root", Keyword.Declaration),
        ("branch", Keyword.Declaration),
        ("tree", Keyword.Declaration),
        ("trait", Keyword.Declaration),
        ("kind", Keyword.Declaration),
        ("seed", Keyword.Namespace),
        ("good", Keyword.Constant),
        ("bad", Keyword.Constant),
        ("true", Keyword.Constant),
        ("false", Keyword.Constant),
        ("none", Keyword.Constant),
        ("if", Keyword),
        ("else", Keyword),
        ("match", Keyword),
        ("for", Keyword),
        ("while", Keyword),
        ("break", Keyword),
        ("continue", Keyword),
        ("return", Keyword),
        ("try", Keyword),
        ("catch", Keyword),
        ("finally", Keyword),
        ("throw", Keyword),
        ("spawn", Keyword),
        ("weak", Keyword),
        ("and", Operator.Word),
        ("or", Operator.Word),
        ("not", Operator.Word),
        ("in", Operator.Word),
        ("is", Operator.Word),
        ("as", Operator.Word),
        ("self", Name.Builtin.Pseudo),
        ("super", Name.Builtin.Pseudo),
        ("_", Keyword.Pseudo),
    ],
)
def test_keyword(word, token):
    assert lex(word) == [(token, word)]


@pytest.mark.parametrize(
    "word",
    ["elif", "void", "plants", "planter", "_private", "name2", "good_bye", "nonexistent"],
)
def test_not_a_keyword(word):
    assert lex(word) == [(Name, word)]


def test_declarations():
    assert lex("branch area(r: float) -> float") == [
        (Keyword.Declaration, "branch"),
        (Name.Function, "area"),
        (Punctuation, "("),
        (Name, "r"),
        (Punctuation, ":"),
        (Keyword.Type, "float"),
        (Punctuation, ")"),
        (Operator, "->"),
        (Keyword.Type, "float"),
    ]
    assert kinds("tree Circle : Shape {")["Circle"] is Name.Class
    assert kinds("trait Shape {")["Shape"] is Name.Class
    assert kinds("kind Direction { North }")["Direction"] is Name.Class
    assert kinds("root limit = 10")["limit"] is Name.Constant
    assert kinds("plant total = 0")["total"] is Name.Variable


def test_seed():
    assert lex("seed net.http as web") == [
        (Keyword.Namespace, "seed"),
        (Name.Namespace, "net.http"),
        (Keyword.Namespace, "as"),
        (Name.Namespace, "web"),
    ]
    assert lex("seed ./models/user") == [
        (Keyword.Namespace, "seed"),
        (Name.Namespace, "./models/user"),
    ]
    tokens = lex("seed math { sqrt, PI }")
    assert tokens[:3] == [
        (Keyword.Namespace, "seed"),
        (Name.Namespace, "math"),
        (Punctuation, "{"),
    ]
    assert (Name.Constant, "PI") in tokens
    # The seed state ends with the line.
    assert lex("seed io\nplant x = 1")[2] == (Keyword.Declaration, "plant")


def test_builtins_and_types():
    assert kinds("drop(len(xs))")["drop"] is Name.Builtin
    assert kinds("drop(len(xs))")["len"] is Name.Builtin
    # A conversion is a built-in function when called, a type otherwise.
    assert kinds("int(text)")["int"] is Name.Builtin
    assert kinds("n: int")["int"] is Keyword.Type
    assert kinds("m: map[str, bool]")["map"] is Keyword.Type
    assert kinds("m: map[str, bool]")["bool"] is Keyword.Type
    assert kinds("throw ValueError(msg)")["ValueError"] is Name.Exception
    assert kinds("plant c = Circle(1.0)")["Circle"] is Name.Class
    assert kinds("drop(MAX_SIZE)")["MAX_SIZE"] is Name.Constant
    # After a dot, a name is a member, even a built-in's name.
    assert lex("s.len()")[:3] == [
        (Name, "s"),
        (Punctuation, "."),
        (Name.Attribute, "len"),
    ]
    assert lex("p?.name")[1:] == [(Operator, "?."), (Name.Attribute, "name")]


# Strings


def test_plain_string_and_escapes():
    assert lex(r'"a\tb \{x\} \u{1F351} \q"') == [
        (String.Double, '"a'),
        (String.Escape, r"\t"),
        (String.Double, "b "),
        (String.Escape, r"\{"),
        (String.Double, "x"),
        (String.Escape, r"\}"),
        (String.Double, " "),
        (String.Escape, r"\u{1F351}"),
        # An unknown escape is plain string text, not an Error token.
        (String.Double, r' \q"'),
    ]


def test_interpolation_is_an_expression():
    assert lex('"Hi {user.name + "!"}"') == [
        (String.Double, '"Hi '),
        (String.Interpol, "{"),
        (Name, "user"),
        (Punctuation, "."),
        (Name.Attribute, "name"),
        (Operator, "+"),
        (String.Double, '"!"'),
        (String.Interpol, "}"),
        (String.Double, '"'),
    ]


def test_interpolation_format_spec():
    assert lex('"{self.area():.2} {n:>5}"') == [
        (String.Double, '"'),
        (String.Interpol, "{"),
        (Name.Builtin.Pseudo, "self"),
        (Punctuation, "."),
        (Name.Attribute, "area"),
        (Punctuation, "()"),
        (String.Interpol, ":.2}"),
        (String.Double, " "),
        (String.Interpol, "{"),
        (Name, "n"),
        (String.Interpol, ":>5}"),
        (String.Double, '"'),
    ]


def test_interpolation_nesting():
    # A map literal and a string with its own interpolation inside one.
    tokens = lex('"{f({"a": 1})} {"in {x}"} end"')
    assert (Punctuation, ":") in tokens  # inside brackets, not a format
    assert tokens[-1] == (String.Double, ' end"')
    assert [v for t, v in tokens if t is String.Interpol] == ["{", "}", "{", "{", "}", "}"]


def test_unclosed_string_ends_at_newline():
    assert lex('"never closed\nplant x = 1')[1] == (Keyword.Declaration, "plant")


def test_triple_quoted_string_spans_lines():
    code = 'root POEM = """\n    Roses are "red",\n    {colour}.\n    """\ndrop(POEM)'
    tokens = lex(code)
    assert tokens[:3] == [
        (Keyword.Declaration, "root"),
        (Name.Constant, "POEM"),
        (Operator, "="),
    ]
    assert tokens[3] == (String.Double, '"""\n    Roses are "red",\n    ')
    assert tokens[4:7] == [
        (String.Interpol, "{"),
        (Name, "colour"),
        (String.Interpol, "}"),
    ]
    assert tokens[7] == (String.Double, '.\n    """')
    assert tokens[8] == (Name.Builtin, "drop")


def test_single_quotes_are_still_a_string():
    assert lex("'single'") == [(String.Single, "'single'")]


# Numbers


@pytest.mark.parametrize(
    "text, token",
    [
        ("0", Number.Integer),
        ("42", Number.Integer),
        ("1_000_000", Number.Integer),
        ("0xFF", Number.Hex),
        ("0xdead_BEEF", Number.Hex),
        ("0o755", Number.Oct),
        ("0b1010_0101", Number.Bin),
        ("3.14", Number.Float),
        ("1e9", Number.Float),
        ("6.022e23", Number.Float),
        ("2.5e-3", Number.Float),
        ("1E+2", Number.Float),
        ("1_000.000_5", Number.Float),
    ],
)
def test_number(text, token):
    assert lex(text) == [(token, text)]


def test_ranges_and_methods_on_numbers():
    assert lex("1..5") == [(Number.Integer, "1"), (Operator, ".."), (Number.Integer, "5")]
    assert lex("0..=3") == [(Number.Integer, "0"), (Operator, "..="), (Number.Integer, "3")]
    assert lex("2.max(3)")[:3] == [
        (Number.Integer, "2"),
        (Punctuation, "."),
        (Name.Attribute, "max"),
    ]


# Comments


def test_comment():
    assert lex("plant x = 1  # the answer, {not} \"interpolated\"") == [
        (Keyword.Declaration, "plant"),
        (Name.Variable, "x"),
        (Operator, "="),
        (Number.Integer, "1"),
        (Comment.Single, '# the answer, {not} "interpolated"'),
    ]


def test_hash_in_string_is_not_a_comment():
    assert lex('drop("#1 {n} # not a comment")  # a comment') == [
        (Name.Builtin, "drop"),
        (Punctuation, "("),
        (String.Double, '"#1 '),
        (String.Interpol, "{"),
        (Name, "n"),
        (String.Interpol, "}"),
        (String.Double, ' # not a comment"'),
        (Punctuation, ")"),
        (Comment.Single, "# a comment"),
    ]
    tokens = lex('"""\n# still the string\n"""')
    assert tokens == [(String.Double, '"""\n# still the string\n"""')]


# Operators


def test_operators_longest_first():
    code = "// //= ** **= << <<= >> >>= == != <= >= -> => ?. ?? .. ..= += %= ^= ~"
    tokens = [(t, v) for t, v in PlumLexer().get_tokens(code) if not v.isspace()]
    assert tokens == [(Operator, op) for op in code.split()]
