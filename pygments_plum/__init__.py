"""
    pygments_plum
    ~~~~~~~~~~~~~

    A Pygments lexer for Plumlang (https://plum.elixpo.com).

    The rules follow the reference lexer in plumlang/plumlang
    (src/lexer/lexer.c): its keyword table, number forms, strings with
    ``{...}`` interpolation and ``:format`` specs, ``\"\"\"`` strings that
    span lines, ``#`` line comments, ``##`` doc comments and ``#[ ... ]#``
    block comments, which nest.

    Where the compiler reports an error (``&&``, ``;``, ``'single'``
    quotes, a bad escape) the lexer still highlights the text sensibly
    and never emits ``Token.Error``: diagnostics are the compiler's job.

    :copyright: Copyright 2026 Elixpo and the Plumlang contributors.
    :license: MIT, see LICENSE for details.
"""

from pygments.lexer import RegexLexer, bygroups, default, include, words
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

__version__ = "1.0.1"
__all__ = ["PlumLexer"]

IDENT = r"[A-Za-z_][A-Za-z0-9_]*"


class PlumLexer(RegexLexer):
    """
    For Plumlang source code.
    """

    name = "Plumlang"
    url = "https://plum.elixpo.com"
    aliases = ["plum", "plumlang"]
    filenames = ["*.plum"]
    mimetypes = ["text/x-plum"]

    # Statements that are mostly control flow.
    keywords = (
        "if", "else", "match", "for", "while", "break", "continue", "return",
        "try", "catch", "finally", "throw", "spawn", "weak",
    )
    # `true`/`false` are accepted spellings of `good`/`bad`.
    constants = ("good", "bad", "true", "false", "none")
    word_operators = ("and", "or", "not", "in", "is", "as")
    # Built-in functions (spec section 7): always available, no `seed`.
    builtin_functions = ("drop", "ask", "len", "type_of", "assert", "exit")
    # Built-in types; the scalar ones double as conversion functions.
    builtin_types = ("int", "float", "bool", "str", "byte", "list", "map", "set",
                     "Channel", "Json")
    conversions = ("int", "float", "str", "byte", "set")
    # Built-in error trees.
    errors = (
        "Error", "ValueError", "ParseError", "IndexError", "KeyError",
        "OverflowError", "ZeroDivisionError", "IOError", "NetError",
        "AssertError",
    )

    tokens = {
        "root": [
            include("expr"),
        ],
        "expr": [
            (r"\s+", Whitespace),
            (r"#\[", Comment.Multiline, "block-comment"),
            # `##` lines document the declaration after them; `###` doesn't.
            (r"##(?!#)[^\n]*", String.Doc),
            (r"#[^\n]*", Comment.Single),

            # Strings. `"""` first, so it isn't read as an empty string.
            (r'"""', String.Double, "tdqs"),
            (r'"', String.Double, "dqs"),
            # Single quotes are an error in Plumlang, but the compiler still
            # reads them as a string up to the end of the line.
            (r"'[^'\n]*'?", String.Single),

            # A member after `.` or `?.`: a field or method, never a
            # keyword or built-in (`s.len()`, `e.message`).
            (r"(\?\.)(" + IDENT + r")", bygroups(Operator, Name.Attribute)),
            (r"(\.)(" + IDENT + r")", bygroups(Punctuation, Name.Attribute)),

            # Declarations.
            (r"(seed)\b", Keyword.Namespace, "seed"),
            (r"(branch)([ \t]+)(" + IDENT + r")",
             bygroups(Keyword.Declaration, Whitespace, Name.Function)),
            (r"(tree|trait|kind)([ \t]+)(" + IDENT + r")",
             bygroups(Keyword.Declaration, Whitespace, Name.Class)),
            (r"(root)([ \t]+)(" + IDENT + r")",
             bygroups(Keyword.Declaration, Whitespace, Name.Constant)),
            (r"(plant)([ \t]+)(" + IDENT + r")",
             bygroups(Keyword.Declaration, Whitespace, Name.Variable)),
            (words(("plant", "root", "branch", "tree", "trait", "kind"),
                   suffix=r"\b"), Keyword.Declaration),

            # Keywords.
            (words(constants, suffix=r"\b"), Keyword.Constant),
            (words(word_operators, suffix=r"\b"), Operator.Word),
            (words(keywords, suffix=r"\b"), Keyword),
            (words(("self", "super"), suffix=r"\b"), Name.Builtin.Pseudo),
            (r"_\b", Keyword.Pseudo),

            # Numbers. A fraction needs a digit after the point: `1..5`
            # is a range and `1.max()` a method call.
            (r"0[xX][0-9a-fA-F_]*", Number.Hex),
            (r"0[oO][0-7_]*", Number.Oct),
            (r"0[bB][01_]*", Number.Bin),
            (r"[0-9][0-9_]*(\.[0-9][0-9_]*)?[eE][+-]?[0-9_]*", Number.Float),
            (r"[0-9][0-9_]*\.[0-9][0-9_]*", Number.Float),
            (r"[0-9][0-9_]*", Number.Integer),

            # Names.
            (words(builtin_functions, suffix=r"\b"), Name.Builtin),
            (words(conversions, suffix=r"\b(?=\s*\()"), Name.Builtin),
            (words(builtin_types, suffix=r"\b"), Keyword.Type),
            (words(errors, suffix=r"\b"), Name.Exception),
            (r"_*[A-Z][A-Z0-9_]*\b", Name.Constant),
            (r"_*[A-Z][A-Za-z0-9_]*", Name.Class),
            (IDENT, Name),

            # Operators, longest first. `&&`, `||`, `++`, `--` and `!` are
            # errors the compiler explains; they still look like operators.
            (r"//=|\*\*=|<<=|>>=|\.\.=|\.\.|->|=>|\?\.|\?\?|//|\*\*|<<|>>"
             r"|[=!<>+\-*/%&|^]=|&&|\|\||\+\+|--|[-+*/%&|^~<>=?!]", Operator),
            (r"[()\[\]{},:.;]", Punctuation),

            # Anything else (stray or non-ASCII characters outside strings).
            (r".", Text),
        ],
        # `#[ ... ]#`: each `#[` inside needs its own `]#`; nothing else,
        # strings included, means anything.
        "block-comment": [
            (r"#\[", Comment.Multiline, "#push"),
            (r"\]#", Comment.Multiline, "#pop"),
            (r"[^#\]]+", Comment.Multiline),
            (r"[#\]]", Comment.Multiline),
        ],
        "seed": [
            (r"[ \t]+", Whitespace),
            (r"as\b", Keyword.Namespace),
            (r"\.{1,2}/[A-Za-z0-9_./-]*", Name.Namespace),
            (IDENT + r"(?:\." + IDENT + r")*", Name.Namespace),
            default("#pop"),
        ],
        "escapes": [
            (r'\\(?:[ntr\\"{}0]|u\{[0-9a-fA-F]{1,6}\})', String.Escape),
            # An unknown escape: an error the compiler reports.
            (r"\\", String.Double),
        ],
        "dqs": [
            (r'"', String.Double, "#pop"),
            # A newline ends an unclosed string, as in the compiler.
            (r"\n", Whitespace, "#pop"),
            include("escapes"),
            (r"\{", String.Interpol, "interp"),
            (r'[^"\\{\n]+', String.Double),
        ],
        "tdqs": [
            (r'"""', String.Double, "#pop"),
            include("escapes"),
            (r"\{", String.Interpol, "interp"),
            (r'[^"\\{]+', String.Double),
            (r'"', String.Double),
        ],
        # Inside `{...}` in a string: an ordinary expression. A `:` at the
        # top level of the interpolation starts a format spec, which runs
        # to the `}` (or a quote or newline): "{x:>5}", "{total:.2}".
        "interp": [
            (r"\}", String.Interpol, "#pop"),
            (r':[^}"\n]*', String.Interpol),
            (r"[(\[{]", Punctuation, "interp-nested"),
            include("expr"),
        ],
        # Brackets inside an interpolation; here `:` and `}` are ordinary.
        "interp-nested": [
            (r"[)\]}]", Punctuation, "#pop"),
            (r"[(\[{]", Punctuation, "#push"),
            include("expr"),
        ],
    }
