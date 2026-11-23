"""Pygments finds the lexer through the `pygments.lexers` entry point.

These need the package installed (`pip install -e .`), not just importable.
"""

from importlib.metadata import entry_points

import pytest
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import (
    find_lexer_class_by_name,
    get_lexer_by_name,
    get_lexer_for_filename,
    get_lexer_for_mimetype,
)
from pygments.util import ClassNotFound

from pygments_plum import PlumLexer


def test_entry_point_is_registered():
    found = entry_points(group="pygments.lexers")
    plum = [ep for ep in found if ep.name == "plum"]
    assert len(plum) == 1
    assert plum[0].value == "pygments_plum:PlumLexer"
    assert plum[0].load() is PlumLexer


@pytest.mark.parametrize("alias", ["plum", "plumlang"])
def test_get_lexer_by_name(alias):
    lexer = get_lexer_by_name(alias)
    assert type(lexer) is PlumLexer
    assert find_lexer_class_by_name(alias) is PlumLexer


def test_get_lexer_for_filename_and_mimetype():
    assert type(get_lexer_for_filename("examples/hello.plum")) is PlumLexer
    assert type(get_lexer_for_mimetype("text/x-plum")) is PlumLexer


def test_metadata():
    assert PlumLexer.name == "Plumlang"
    assert PlumLexer.url == "https://plum.elixpo.com"
    assert PlumLexer.aliases == ["plum", "plumlang"]
    assert PlumLexer.filenames == ["*.plum"]
    assert PlumLexer.mimetypes == ["text/x-plum"]


def test_unrelated_names_are_not_taken():
    with pytest.raises(ClassNotFound):
        get_lexer_by_name("plumlang-but-not-really")


def test_highlight_html():
    html = highlight('drop("Hi {name}")', get_lexer_by_name("plum"), HtmlFormatter())
    assert '<span class="nb">drop</span>' in html
    assert '<span class="si">{</span>' in html
