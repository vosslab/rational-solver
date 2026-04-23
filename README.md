# rational-solver

Minimal rational-function analyzer for the TI-84 Plus CE Python graphing
calculator. Given a numerator and denominator like `(x+2)(x-3)` over
`(x+6)(x-1)`, it reports vertical asymptotes, holes, x- and
y-intercepts, horizontal or slant asymptote, and a sign chart. Written
for students who want a quick second opinion on a homework rational.

## Quick start

Desktop (for testing the program before sending it to the calculator):

```
source source_me.sh && python3 rational.py
```

To run on a TI-84 Plus CE Python, send `rational.py` to the calculator
with TI Connect CE and open it from the Python app. Full transfer and
input steps are in [docs/USAGE.md](docs/USAGE.md).

## Documentation

- [docs/USAGE.md](docs/USAGE.md): supported input forms, sample session,
  and TI-84 transfer walk-through.
- [docs/CHANGELOG.md](docs/CHANGELOG.md): dated record of changes and
  decisions.
- [docs/AUTHORS.md](docs/AUTHORS.md): maintainers and contributors.

## Testing

```
source source_me.sh && python3 -m pytest tests/test_rational.py
```

## Author

Neil Voss - [bsky.app/profile/neilvosslab.bsky.social](https://bsky.app/profile/neilvosslab.bsky.social)
