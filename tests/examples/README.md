# Test programs

Copied from [plumlang/plumlang](https://github.com/plumlang/plumlang) at
commit 956312b, so the tests don't need a Plumlang checkout:

- `examples/`: the example programs (`examples/` there), all of them.
- `lang/`: a selection of the language tests (`tests/lang/` there): the
  lexer tests, including the ones that are meant to fail, and strings,
  kinds, trees, tasks, errors, control flow, operators, formatting and
  modules.

These files are under Plumlang's licence, Apache-2.0 (see
[LICENSE](LICENSE) here), not the MIT licence of the rest of this
repository. A few are deliberately invalid Plumlang (bad escapes, `&&`,
invalid UTF-8) to check that the lexer copes.
