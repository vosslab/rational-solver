# Changelog

## 2026-04-23

### Behavior or Interface Changes

- End-behavior classification now uses the *reduced* numerator and
  denominator (after cancelling shared factors into holes). New labels
  `Constant:`, `Linear:`, and `Polynomial:` replace the misleading
  `Slant:` label when the reduced denominator is a constant. Example:
  `(3x^2-27)/(x-3)` now reports `Linear: y=3x+9` rather than calling
  the same line a slant asymptote. True slant cases (e.g. `x^2/(x-1)`)
  still report `Slant:`.
- Friendlier prompts. The UI now prints a short example line,
  `Enter numerator:` / `Enter denominator:` on their own line, and
  reads input from the next line so nothing wraps on the TI-84 screen.

### Developer Tests and Notes

- Added tests for the Linear-over-hole (`(3x^2-27)/(x-3)`),
  constant-denominator (`(x-4)/3`), Constant-via-hole (`(x-5)/(x-5)`),
  and true-slant (`x^2/(x-1)`) end-behavior branches.

## 2026-04-22

### Additions and New Features

- Added `rational.py`, a TI-84 Plus CE Python analyzer for rational
  functions. Parses factored or expanded numerator and denominator
  expressions, factors each polynomial (rational root theorem plus
  quadratic formula plus Newton-with-deflation for degree 3+), and
  reports vertical asymptotes, holes (shared roots), x- and y-intercepts,
  horizontal or slant asymptote, and a sign chart per interval.
- Added `tests/test_rational.py` covering parser modes, polynomial
  arithmetic, factorer branches (rational, irrational quadratic,
  repeated root, irreducible residual), and full analyzer pipeline on
  the user example plus hole and slant cases.
- Added [docs/USAGE.md](USAGE.md) with input grammar, sample session,
  and TI Connect CE transfer steps.
- Added `README.md` pointing at [docs/USAGE.md](USAGE.md).

### Decisions and Failures

- Grammar was deliberately narrowed after first draft. The parser now
  only accepts factored-form products (any polynomial inside each paren)
  or a single expanded polynomial, but not mixed free-form algebra. The
  parser was the riskiest part of the design, so keeping its job small
  traded expressiveness for reliability on the calculator.
- Replaced `math.isclose` with a local `close()` helper because TI's
  published TI-Python `math` module does not include it. Same reasoning
  drove avoiding `math.gcd`, `math.hypot`, and hyperbolic functions.
- Newton's method uses an incremental sign-change scan rather than
  building a 201-point grid, because TI-Python caps list length at 100.

### Developer Tests and Notes

- `source source_me.sh && python3 -m pytest tests/test_rational.py` (20
  passed).
- `pyflakes rational.py tests/test_rational.py` clean.
- Manual smoke on three cases: `(x+2)(x-3)/((x+6)(x-1))`, `(3x^2-27)/(x-3)`
  (slant y = 3x + 9, hole at x=3), and `(x-2)(x+1)/((x-2)(x+3))` (hole
  at x=2, VA at x=-3). All matched expected output.
