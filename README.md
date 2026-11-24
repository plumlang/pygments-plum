# Plumlang for Pygments

A [Pygments](https://pygments.org) lexer plugin for
[Plumlang](https://plum.elixpo.com), for `.plum` files. Once it is
installed, everything that highlights code with Pygments knows Plumlang:
Sphinx, MkDocs (Material included), `pygmentize`, Jupyter, and the many
static site generators and chat tools built on Pygments.

It highlights:

- **Keywords**: declarations (`plant`, `root`, `branch`, `tree`, `trait`,
  `kind`), `seed` imports with their module paths and aliases, control flow,
  `and`/`or`/`not`/`in`/`is`/`as`, and the constants `good`, `bad` and
  `none`.
- **Names at declarations**: functions and methods after `branch`, trees,
  traits and kinds after their keyword, constants after `root`.
- **Types and built-ins**: `int`, `str`, `list`, `map`, ...; the built-in
  functions (`drop`, `ask`, `len`, ...); conversions such as `int(text)`;
  the built-in error trees (`ValueError`, `IOError`, ...); `self` and
  `super`.
- **Strings** with escapes (`\n`, `\{`, `\u{1F351}`) and `{interpolation}`,
  whose expression is highlighted like any other code, with format specs
  (`{total:.2}`, `{n:>5}`); `"""` strings across lines.
- **Numbers** in every form (`1_000`, `0xFF`, `0o755`, `0b1010`, `6.022e23`),
  operators, punctuation and `#` comments.

The rules follow the reference lexer in
[plumlang/plumlang](https://github.com/plumlang/plumlang). The lexer never
produces Pygments' `Error` token: code the compiler would reject (`&&`, a
`'single-quoted'` string, a bad escape) is still highlighted sensibly.

## Install

```sh
pip install pygments-plum
```

The package registers itself with Pygments through the `pygments.lexers`
entry point, so nothing else needs configuring. Check it with:

```sh
pygmentize -L lexers | grep -A1 Plumlang
```

## Use

The lexer's names are `plum` and `plumlang`; it is picked for `*.plum` files
and the `text/x-plum` MIME type.

### On the command line

```sh
pygmentize -l plum hello.plum                 # to the terminal
pygmentize -l plum -f terminal256 -O style=monokai hello.plum
pygmentize -l plum -f html -O full -o hello.html hello.plum
pygmentize hello.plum                         # picked by the .plum suffix
```

### In Sphinx

Add `pygments-plum` to your docs' requirements (for example
`docs/requirements.txt` on Read the Docs), then write:

````rst
.. code-block:: plum

   plant name = "Ada"
   drop("Hello, {name}!")
````

or, with MyST Markdown, a ```` ```plum ```` fence.

### In MkDocs

With [`pymdownx.highlight`](https://facelessuser.github.io/pymdown-extensions/extensions/highlight/)
and `pymdownx.superfences` (Material for MkDocs turns them on in its
recommended setup), add `pygments-plum` to the requirements your docs are
built with and use ```` ```plum ```` fences:

```yaml
# mkdocs.yml
markdown_extensions:
  - pymdownx.highlight:
      use_pygments: true
  - pymdownx.superfences
```

````markdown
```plum
tree Account {
    owner: str
    balance: float = 0.0

    branch to_str() -> str => "{self.owner}: {self.balance:.2}"
}
```
````

### From Python

```python
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

html = highlight('drop("Hello, {name}!")', get_lexer_by_name("plum"), HtmlFormatter())
```

`from pygments_plum import PlumLexer` works too.

## Development

```sh
python -m venv .venv
.venv/bin/pip install -e '.[test]'
.venv/bin/pytest
```

The tests lex every program in `tests/examples/` (a copy of Plumlang's
examples and language tests), checking that no `Error` token appears and
that the tokens put back together give the input unchanged, then check the
tokens of keywords, strings, interpolation, numbers and comments one by one,
and that Pygments finds the lexer through its entry point. To run the first
test over a full Plumlang checkout as well, point `PLUM_SOURCE` at it:

```sh
PLUM_SOURCE=../plumlang .venv/bin/pytest
```

`tests/test_sample.py` checks the lexer against Plumlang's shared
highlighting sample ([`tests/highlight/`](https://github.com/plumlang/plumlang/tree/main/tests/highlight),
downloaded from `main`, or the folder in `PLUM_HIGHLIGHT`): every keyword in
the lexer is a keyword here, `sample.plum` has no `Error` token and
round-trips, and, with `plum` installed, every token `plum tokens` reports
has the right type. CI runs it on every push and weekly, so a keyword added
to Plumlang fails here until the lexer knows it.

```sh
PLUM_HIGHLIGHT=../plumlang/tests/highlight .venv/bin/pytest tests/test_sample.py
```

## Links

- Plumlang: <https://plum.elixpo.com>
- Docs: <https://plum.elixpo.com/docs/>
- Language specification: <https://github.com/plumlang/plumlang/blob/main/docs/spec.md>
- Tree-sitter grammar: <https://github.com/plumlang/tree-sitter-plum>
- Writing Pygments plugins: <https://pygments.org/docs/plugins/>

## Licence

The code in this repository is under the [MIT licence](LICENSE). The
Plumlang name and logo are trademarks of Elixpo and are not licensed by it;
see [NOTICE](NOTICE).
