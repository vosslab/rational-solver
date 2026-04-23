# Usage

`rational.py` analyzes a rational function `N(x) / D(x)` and prints the
vertical asymptotes, holes, x- and y-intercepts, horizontal or slant
asymptote, and a sign chart.

## Desktop

```
source source_me.sh && python3 rational.py
```

Sample session:

```
Rational analyzer
Example: (x+2)(x-3)
Use x, ^, and ( )

Enter numerator:
(x+2)(x-3)
Enter denominator:
(x+6)(x-1)
VA: x=-6, x=1
Hole: none
X-int: x=-2, x=3
Y-int: y=1
HA: y=1
Sign:
 (-inf,-6)+
 (-6,-2)-
 (-2,1)+
 (1,3)-
 (3,inf)+
```

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
| `HA:` | Horizontal asymptote when reduced `deg N <= deg D` |
| `Slant:` | Slant asymptote when reduced `deg N == deg D + 1` and `deg D >= 1` |
| `Constant:` / `Linear:` / `Polynomial:` | Reduced function when `deg D == 0` after cancellation |
| `Sign:` | Sign of `f(x)` in each interval between critical values |

End-behavior classification uses the *reduced* numerator and denominator
(after shared factors are cancelled into holes), so `(3x^2-27)/(x-3)`
reports `Linear: y=3x+9` rather than a slant asymptote. When reduced
`deg N > deg D + 1`, `No linear asymp` is reported instead.

## TI-Python limitations

- Only the `math` functions listed in TI's selected-content appendix are used.
- `math.isclose` is not present on TI-Python; a local `close()` helper is
  used for tolerant comparisons.
- The Newton-method scan is incremental so it never builds a list longer
  than the TI-Python 100-element cap.

See [docs/INSTALL.md](docs/INSTALL.md) for environment setup and
[docs/CHANGELOG.md](docs/CHANGELOG.md) for the history of changes.
