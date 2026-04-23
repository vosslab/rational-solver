# Changelog

## 2026-04-25

### Additions and New Features

- Rewrote `print_result` in a verbose TI-friendly format: full section
  labels (`Vertical asymptote`, `Hole`, `X-intercepts`, `Y-intercept`,
  `Horizontal asymptote`, `Slant asymptote`, `Linear function`, etc.),
  one value per line, blank line between sections. The sign chart now
  prints `Above x-axis on` / `Below x-axis on` on the line preceding
  each interval instead of cramming `+`/`-` at the end. The TI-84 Plus
  CE Home screen scrolls, so prioritizing per-line clarity over fitting
  everything on screen is the right tradeoff.

### Fixes and Maintenance

- Zero denominator now raises a clear `ValueError('denominator is
  identically zero')` before any analysis instead of crashing later with
  `ZeroDivisionError`.
- Zero numerator (`0 / D(x)`) is recognized as the constant zero
  function with removable holes at every root of the denominator, not
  a rational function with spurious vertical asymptotes.

### Developer Tests and Notes

- `sign_chart()` now returns a list of `(side, interval_str)` tuples
  so presentation (full labels vs. single-char signs) is decoupled from
  the math. Test `test_sign_chart_runs` updated accordingly.
- Added `test_zero_denominator_raises` and
  `test_zero_numerator_constant_zero`. Total test count 30, all passing.

## 2026-04-24

### Behavior or Interface Changes

- Narrowed scope to integer coefficients only. Decimal inputs such as
  `1.5x+2` now raise a clear `ValueError` at tokenization time. This
  matches the kinds of problems the tool is actually used for and
  removes a class of floating-point edge cases from the parser and
  rational-root logic.
- Sign chart now includes holes as breakpoints, so a hole at x=2 splits
  the sign row the same way a VA or x-intercept does. Graph-shape
  summaries are no longer silently missing a discontinuity.
- Sign chart and y-intercept now evaluate the *reduced* numerator and
  denominator (post hole cancellation), matching the reduced
  end-behavior classification.
- Parser accepts a leading x-monomial prefix before parenthesized
  factors, so `x(x+1)`, `-x(x-4)`, and `2x^2(x+1)` all parse correctly.
  Previously the factored-mode branch demanded only an optional integer
  before the first `(`.

### Fixes and Maintenance

- Dropped `source source_me.sh &&` from documented commands. The script
  was removed; plain `python3` is sufficient for a single-file project.

### Developer Tests and Notes

- Added tests for `x(x+1)`, `-x(x-4)`, `2x^2(x+1)`, decimal rejection,
  and hole-as-breakpoint in the sign chart. Total test count 28, all
  passing.

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
