# Usage

`rational.py` analyzes a rational function `N(x) / D(x)` and prints the
vertical asymptotes, holes, x- and y-intercepts, horizontal or slant
asymptote, and a sign chart.

## Desktop

```
python3 rational.py
```

Sample session:

```
Rational analyzer
Integer coefs only.
Use x, ^, and ( ).
Ex: (x+2)(x-3)

Enter numerator:
(x+2)(x-3)
Enter denominator:
(x+6)(x-1)
Vertical asymptote
x = -6
x = 1

Hole
none

X-intercepts
x = -2
x = 3

Y-intercept
y = 1

Horizontal asymptote
y = 1

Above x-axis on
(-inf, -6)
Below x-axis on
(-6, -2)
Above x-axis on
(-2, 1)
Below x-axis on
(1, 3)
Above x-axis on
(3, inf)
```

Output is one value per line with blank lines between sections, matching
the TI-84 Plus CE Home screen's 26-column width. Older rows scroll off
the top and are reachable with the arrow keys.

## TI-84 Plus CE Python

1. Connect the calculator via USB and open TI Connect CE.
2. Send `rational.py` to the calculator (Send To Calculator > Python Program).
3. On the calculator, press `[prgm]` and open the Python app.
4. Select `rational`, press `Run`.
5. Enter numerator and denominator when prompted.

## Accepted input forms

- Fully factored with integer-coefficient linear factors:
  `(x+2)(x-3)`, `(2x-1)(x+5)`, `-3(x-1)^2(x+4)`
- Factored with any expanded polynomial inside each paren:
  `(x-1)(x^2+1)`, `(x^2-4)(x+3)`
- Single expanded polynomial: `3x^2-27`, `x^3-x`, `-2x^2+5x-1`

Powers use `^`, the variable must be `x`, and coefficients must be integers.
Square brackets `[ ]` are accepted as an alias for `( )`.

## What the analysis reports

| Line | Meaning |
| --- | --- |
| `VA:` | Vertical asymptotes (roots of reduced denominator) |
| `Hole:` | Shared roots between numerator and denominator |
| `X-int:` | X-intercepts (roots of reduced numerator) |
| `Y-int:` | Value `f(0)`, or `undef` if denominator is zero at x=0 |
| `Vertical asymptote` | Roots of the reduced denominator |
| `Hole` | Shared roots cancelled between numerator and denominator |
| `X-intercepts` | Roots of the reduced numerator |
| `Y-intercept` | Value of the reduced function at `x = 0` |
| `Horizontal asymptote` | When reduced `deg N <= deg D` |
| `Slant asymptote` | When reduced `deg N == deg D + 1` and `deg D >= 1` |
| `Constant / Linear / Polynomial function` | Reduced function when `deg D == 0` |
| `Above / Below x-axis on` | Sign of the reduced function on each interval |

End-behavior classification uses the *reduced* numerator and denominator
(after shared factors are cancelled into holes), so `(3x^2-27)/(x-3)`
reports `Linear function y = 3x+9` rather than a slant asymptote. When
reduced `deg N > deg D + 1`, `no linear asymptote` is reported.

## Edge cases and limits

- `denominator is identically zero` is raised before any analysis; the
  function is undefined everywhere.
- A zero numerator like `0 / (x-1)` is reported as `Constant function
  y = 0` with a hole at every root of the denominator.
- Rational roots inside Newton's fallback scan are only searched on
  `[-50, 50]`; polynomials with roots outside that range will leave an
  irreducible residual rather than reporting the missing root.

## TI-Python limitations

- Only the `math` functions listed in TI's selected-content appendix are used.
- `math.isclose` is not present on TI-Python; a local `close()` helper is
  used for tolerant comparisons.
- The Newton-method scan is incremental so it never builds a list longer
  than the TI-Python 100-element cap.

See [docs/INSTALL.md](docs/INSTALL.md) for environment setup and
[docs/CHANGELOG.md](docs/CHANGELOG.md) for the history of changes.
