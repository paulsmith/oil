---
in_progress: true
---

Oil Expressions vs. Python
==========================

Oil's expression language borrows heavily from Python.  In fact, it literally
started with Python's `Grammar/Grammar` file.

This doc describes some differences, which may help Python users learn Oil.

If you don't know Python, see [A Tour of the Oil
Language](oil-language-tour.html).

<div id="toc">
</div>

## Literals for Data Types

### Same as Python

- Integers: `123`, `1_000_000`, `0b1100_0010`, `0o755`, `0xff`
- Floats: `1.023e6` (not in the first cut of Oil)
- Lists: `['pea', 'nut']`

### Changed

- `true`, `false`, and `null` (like JavaScript) rather than `True`, `False`,
  and `None` (like Python).  In Oil, types are spelled with capital letters.
- String literals are like **shell** string literals, not like Python.
  - Double Quoted: `"hello $name"`
  - Single quoted: `r'c:\Program Files\'` 
  - C-style: `$'line\n'`.
    - Unicode literals are `\u{3bc}` instead of `\u03bc` and `\U000003bc`
- Dicts: use **JavaScript** syntax, not Python
  - Unquoted keys: `{age: 42}`
  - Bracketed keys: `{[myvar + 1]: 'value'}`
  - "Punning": `{age}`

### New

- Character literals are **integers**
  - Unicode `\u{03bc}`
  - Backslash: `\n`  `\\`  `\'`
  - Pound `#'a'`
- Shell-like list literals: `%(pea nut)` is equivalent to `['pea', 'nut']`
- Unevaluated expressions
  - Block `^(ls | wc -l)`
  - Unevaluated expression: `^[1 + a[i] + f(x)]`
  - Arg list: `^{42, verbose = true}`

<!--
`%symbol` (used in eggex now, but could also be used as interned strings)
-->

### Removed

- No tuple type for now.  We might want Go-like multiple return values.

<!--
- Tuples (TODO): Does Oil have true tuples?
  - Singleton tuples like `42,` are disallowed, in favor of the more explicit
    `tup(42)`.
-->

## Operators

### Note: Oil Does Less Operator Overloading

Oil doesn't overload operators as much because it often does automatic string
<-> int conversion (like Awk):

- `a + b` is for addition, while `a ++ b` is for concatenation.
- `a < b` does numeric comparison (with conversion).  `cmp()` could be for
  strings.

### Same as Python

- Arithmetic `+ - * / // %`, and `**` for exponentiation
- Comparison `< > <= =>`
- Bitwise `& | ~ ^ << >>`
- Logical `and or not`
- Ternary `0 if cond else 1`
- Indexing: `s[i]` evaluates to an integer?
- Slicing: `s[i:j]` evaluates to a string
- Membership `in  not in`
- Function Call: `f(x, y)`
  - What about splat `*` and `**`?

### Changed

- Equality `=== !==` because we also have `~==`
- String Concenation: `++` (not `+`, which is always addition)

### New

- Eggex match `s ~ /d+/`
- Glob match `s ~~ '*.py'`
- Approximate Equality `42 ~== '42'`
- Oil sigils: `$` and `@`
- `mydict->key` as an alias for `mydict['key']`

### Removed

- No string formatting with `%`.  Use `${x %.3f}` instead.
- No `@` for matrix multiply.
- I removed slice step syntax `1:5:2` because `0::2` conflicts with
  `module::name`.  This was only necessary for Tea, not Oil.

<!--
Do we need `is` and `is not` for identity?
-->

## Oil vs. JavaScript

- Oil uses `==` and `~==` for exact and type-converting equality, while JS uses
  `===` and `==`.
- `mydict->key` instead of `mydict.key`.  We want to distinguish between
  attributes and keys (like Python does).
- Where Oil is consistent with Python
  - Oil expressions use `and or not` while JS uses `&& || !`.  In shell, `&& ||
    !` are already used in the command language (but they're somewhat less
    important than in Oil).
  - Oil's ternary operator is `0 if cond else 1`, while in JS it's `cond ? 0 :
    1`.
  - Precedence rules are probably slightly different (but still C-like), and
    follows Python's grammar
- Same differences as Oil vs. Python
  - `s ++ t` for string concatenation rather than `s + t`
  - Shell string literals rather than JS string literals

## Semantics

Oil's syntax is a mix of Python and JavaScript, but the **semantics** are
closer to Python.

### Differences vs. Python

- Iterating over a string yields code points, not one-character strings.
  - `s[i]` returns an integer code point ("rune").
  - TODO: maybe this should be `runeAt()` and `byteAt()`?
- Bools and integers are totally separate types.  Oil is like JavaScript, where
  they aren't equal: `true !== 1`.  In Python, they are equal: `True == 1`.
- No "accidentally quadratic"
  - No `in` for array/list membership.  Only dict membership.
  - The `++=` operator on strings doesn't exist.

## TODO

- `100 MiB`?  This should be multiplication?
- Unevaluated Expr, Block, ArgList
