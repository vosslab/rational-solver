#!/usr/bin/env python3
"""
Rational function analyzer for TI-84 Plus CE Python.

Takes numerator and denominator expressions (factored or expanded) and
reports vertical asymptotes, holes, x/y intercepts, horizontal or slant
asymptote, and a sign chart.
"""

# Standard Library (TI-Python ships only a subset of math)
import math


#============================================
# Float helpers (TI-Python lacks math.isclose)
#============================================

def close(a, b, tol=1e-9):
	"""Tolerant equality test for floats."""
	return math.fabs(a - b) < tol + tol * math.fabs(b)


def fmt_num(x):
	"""Format a float compactly; drop decimals when integral."""
	# snap near-integer values to int for cleaner output
	if close(x, round(x), 1e-6):
		return str(int(round(x)))
	return '{:.3f}'.format(x)


#============================================
# Polynomial arithmetic (lists, highest degree first)
#============================================

def poly_trim(p):
	"""Remove leading zeros but keep at least one coefficient."""
	while len(p) > 1 and close(p[0], 0, 1e-12):
		p = p[1:]
	return p


def poly_add(a, b):
	"""Add two polynomial coefficient lists."""
	la, lb = len(a), len(b)
	n = max(la, lb)
	# left-pad shorter list with zeros so degrees line up
	ap = [0] * (n - la) + list(a)
	bp = [0] * (n - lb) + list(b)
	result = [ap[i] + bp[i] for i in range(n)]
	return poly_trim(result)


def poly_mul(a, b):
	"""Multiply two polynomial coefficient lists."""
	result = [0] * (len(a) + len(b) - 1)
	for i in range(len(a)):
		for j in range(len(b)):
			result[i + j] += a[i] * b[j]
	return poly_trim(result)


def poly_pow(p, k):
	"""Raise polynomial to a non-negative integer power."""
	result = [1]
	for _ in range(k):
		result = poly_mul(result, p)
	return result


def poly_eval(p, x):
	"""Evaluate polynomial at x using Horner's method."""
	result = 0
	for c in p:
		result = result * x + c
	return result


def poly_deriv(p):
	"""Return derivative coefficient list."""
	n = len(p) - 1
	if n == 0:
		return [0]
	# each coefficient scaled by its degree
	return [p[i] * (n - i) for i in range(n)]


def poly_divmod(num, den):
	"""Polynomial long division. Returns (quotient, remainder)."""
	n_deg = len(num) - 1
	d_deg = len(den) - 1
	if n_deg < d_deg:
		return [0], list(num)
	q = [0] * (n_deg - d_deg + 1)
	rem = list(num)
	# standard long-division loop
	for i in range(n_deg - d_deg + 1):
		c = rem[i] / den[0]
		q[i] = c
		for j in range(len(den)):
			rem[i + j] -= c * den[j]
	# trailing entries of rem form the true remainder
	tail = rem[n_deg - d_deg + 1:]
	if not tail:
		tail = [0]
	return q, poly_trim(tail)


#============================================
# Tokenizer and parser (phase 1 grammar)
#============================================

def tokenize(s):
	"""Split expression string into a list of typed tokens."""
	# drop whitespace and normalize variable name
	s = s.replace(' ', '').replace('\t', '').replace('[', '(').replace(']', ')')
	s = s.replace('X', 'x')
	tokens = []
	i = 0
	n = len(s)
	while i < n:
		c = s[i]
		if c.isdigit():
			# collect multi-digit integer
			j = i
			while j < n and s[j].isdigit():
				j += 1
			tokens.append(('num', int(s[i:j])))
			i = j
		elif c == 'x':
			tokens.append(('x',))
			i += 1
		elif c in '+-^':
			tokens.append(('op', c))
			i += 1
		elif c == '*':
			# explicit multiplication is treated same as juxtaposition
			i += 1
		elif c == '(':
			tokens.append(('lp',))
			i += 1
		elif c == ')':
			tokens.append(('rp',))
			i += 1
		else:
			raise ValueError('unexpected character: ' + c)
	return tokens


def parse_expanded(tokens):
	"""Parse an expanded polynomial like 3x^2-27 or -2x^2+5x-1."""
	poly = [0]
	i = 0
	n = len(tokens)
	# leading optional sign
	sign = 1
	if i < n and tokens[i] == ('op', '-'):
		sign = -1
		i += 1
	elif i < n and tokens[i] == ('op', '+'):
		i += 1
	while i < n:
		# each term is [coef]?[x[^k]]?
		coef = 1
		has_coef = False
		if tokens[i][0] == 'num':
			coef = tokens[i][1]
			has_coef = True
			i += 1
		deg = 0
		if i < n and tokens[i] == ('x',):
			deg = 1
			i += 1
			if i < n and tokens[i] == ('op', '^'):
				i += 1
				if i >= n or tokens[i][0] != 'num':
					raise ValueError('expected exponent after ^')
				deg = tokens[i][1]
				i += 1
		elif not has_coef:
			raise ValueError('empty term in polynomial')
		# build signed term and add to running polynomial
		term = [sign * coef] + [0] * deg
		poly = poly_add(poly, term)
		# next must be + or - or end
		if i < n:
			if tokens[i] == ('op', '+'):
				sign = 1
				i += 1
			elif tokens[i] == ('op', '-'):
				sign = -1
				i += 1
			else:
				raise ValueError('unexpected token in expanded mode')
	return poly_trim(poly)


def parse_factored(tokens):
	"""
	Parse an expression that contains at least one parenthesized factor.

	Tokens before the first `(` are treated as an expanded-polynomial
	prefix, so both `3(x-1)` and `-x(x-4)` and `2x^2(x+1)` work. After
	the first `(`, only a sequence of `(...)^k` factors is allowed.
	"""
	n = len(tokens)
	# locate the prefix / first factor boundary
	first_lp = -1
	for idx in range(n):
		if tokens[idx] == ('lp',):
			first_lp = idx
			break
	prefix = tokens[:first_lp] if first_lp >= 0 else tokens
	# prefix is either empty, a sign-only run, or an expanded monomial/poly
	if not prefix:
		poly = [1]
	elif all(t[0] == 'op' and t[1] in '+-' for t in prefix):
		sign = 1
		for t in prefix:
			if t[1] == '-':
				sign = -sign
		poly = [sign]
	else:
		poly = parse_expanded(prefix)
	i = first_lp if first_lp >= 0 else n
	while i < n:
		if tokens[i] != ('lp',):
			raise ValueError('expected ( in factored expression')
		i += 1
		# walk to matching close paren, tracking depth for safety
		depth = 1
		j = i
		while j < n and depth > 0:
			if tokens[j] == ('lp',):
				depth += 1
			elif tokens[j] == ('rp',):
				depth -= 1
			if depth > 0:
				j += 1
		if depth != 0:
			raise ValueError('unmatched parenthesis')
		inner = tokens[i:j]
		i = j + 1
		# optional ^k after the factor
		k = 1
		if i < n and tokens[i] == ('op', '^'):
			i += 1
			if i >= n or tokens[i][0] != 'num':
				raise ValueError('expected exponent')
			k = tokens[i][1]
			i += 1
		factor_poly = parse_expanded(inner)
		poly = poly_mul(poly, poly_pow(factor_poly, k))
	return poly


def parse(s):
	"""Top-level parse entry. Classifies factored vs expanded."""
	tokens = tokenize(s)
	if not tokens:
		raise ValueError('empty expression')
	# presence of any ( triggers factored-mode parser
	has_paren = False
	for t in tokens:
		if t == ('lp',):
			has_paren = True
			break
	if has_paren:
		return parse_factored(tokens)
	return parse_expanded(tokens)


#============================================
# Factorer
#============================================

def divisors(n):
	"""Positive divisors of |n|, or [1] when n is zero."""
	if n == 0:
		return [1]
	n = abs(int(n))
	result = []
	i = 1
	# trial-divide up to sqrt(n); add both sides of each pair
	while i * i <= n:
		if n % i == 0:
			result.append(i)
			if i != n // i:
				result.append(n // i)
		i += 1
	return result


def find_rational_root(coeffs):
	"""Return a rational root of integer-coefficient polynomial, or None."""
	# x=0 is a root when the constant term is zero
	if coeffs[-1] == 0:
		return 0.0
	p_divs = divisors(coeffs[-1])
	q_divs = divisors(coeffs[0])
	# search ordered smallest numerator first; signed; no dedup needed for correctness
	for p in p_divs:
		for q in q_divs:
			for sgn in (1, -1):
				r = sgn * p / q
				if close(poly_eval(coeffs, r), 0, 1e-7):
					return float(r)
	return None


def synth_divide(coeffs, root):
	"""Synthetic division by (x - root). Returns (quotient, remainder)."""
	q = [coeffs[0]]
	for i in range(1, len(coeffs)):
		q.append(coeffs[i] + q[-1] * root)
	remainder = q[-1]
	return q[:-1], remainder


def newton(coeffs, x0, max_iter=60):
	"""Newton's method seeded at x0; None if it fails to converge."""
	dp = poly_deriv(coeffs)
	x = x0
	for _ in range(max_iter):
		fx = poly_eval(coeffs, x)
		if math.fabs(fx) < 1e-11:
			return x
		dfx = poly_eval(dp, x)
		if dfx == 0:
			return None
		x = x - fx / dfx
		if not math.isfinite(x):
			return None
	# final tolerance check
	if math.fabs(poly_eval(coeffs, x)) < 1e-6:
		return x
	return None


def find_newton_root(coeffs):
	"""Scan [-50,50] step 0.5 for a sign change, then Newton from the midpoint."""
	prev_x = -50.0
	prev_y = poly_eval(coeffs, prev_x)
	x = -49.5
	# incremental scan keeps list length bounded (TI-Python 100-element cap)
	while x <= 50.0 + 1e-9:
		y = poly_eval(coeffs, x)
		if prev_y == 0:
			return prev_x
		if prev_y * y < 0:
			# found a sign change; refine with Newton from the midpoint
			r = newton(coeffs, (prev_x + x) / 2)
			if r is not None:
				return r
		prev_x = x
		prev_y = y
		x += 0.5
	return None


def _deflate(coeffs, r, tol):
	"""Divide out the root r as many times as synthetic division cleanly allows."""
	mult = 0
	while len(coeffs) > 1:
		q, rem = synth_divide(coeffs, r)
		if math.fabs(rem) < tol:
			coeffs = q
			mult += 1
		else:
			break
	return coeffs, mult


def factor(coeffs):
	"""
	Factor polynomial into real roots with multiplicities plus an optional
	irreducible residual (degree 2 with negative discriminant).

	Returns (leading, roots, residual). roots is a list of (root, multiplicity).
	"""
	coeffs = poly_trim(list(coeffs))
	# keep original leading coefficient for reporting
	lead_overall = coeffs[0]
	roots = []
	# pass 1: rational roots (only when coefficients are integer)
	while len(coeffs) > 1:
		int_coeffs = [int(round(c)) for c in coeffs]
		ok = True
		for idx in range(len(coeffs)):
			if math.fabs(coeffs[idx] - int_coeffs[idx]) > 1e-7:
				ok = False
				break
		if not ok:
			break
		r = find_rational_root(int_coeffs)
		if r is None:
			break
		coeffs, mult = _deflate(coeffs, r, 1e-6)
		if mult == 0:
			break
		roots.append((r, mult))
	# pass 2: numeric roots for degree >= 3 via Newton
	while len(coeffs) - 1 >= 3:
		r = find_newton_root(coeffs)
		if r is None:
			break
		coeffs, mult = _deflate(coeffs, r, 1e-5)
		if mult == 0:
			break
		roots.append((r, mult))
	# pass 3: resolve remaining degree 1 or 2 directly
	deg = len(coeffs) - 1
	if deg == 1:
		r = -coeffs[1] / coeffs[0]
		roots.append((r, 1))
		coeffs = [coeffs[0]]
	elif deg == 2:
		a, b, c = coeffs
		disc = b * b - 4 * a * c
		if disc >= 0:
			sq = math.sqrt(disc)
			r1 = (-b + sq) / (2 * a)
			r2 = (-b - sq) / (2 * a)
			if close(r1, r2):
				roots.append((r1, 2))
			else:
				roots.append((r1, 1))
				roots.append((r2, 1))
			coeffs = [a]
		# else: leave as irreducible residual (no real roots)
	return lead_overall, roots, coeffs


#============================================
# Analyzer
#============================================

def merge_roots(roots):
	"""Combine near-equal roots, summing their multiplicities, and sort."""
	merged = []
	for r, m in roots:
		found = False
		for idx in range(len(merged)):
			r2, m2 = merged[idx]
			if close(r, r2, 1e-6):
				merged[idx] = (r2, m2 + m)
				found = True
				break
		if not found:
			merged.append((r, m))
	merged.sort(key=lambda rm: rm[0])
	return merged


def compute_holes_and_remainders(num_roots, den_roots):
	"""Pair up shared roots as holes; return (holes, num_left, den_left)."""
	holes = []
	den_left = list(den_roots)
	num_left = []
	for r, m in num_roots:
		matched_idx = -1
		for idx in range(len(den_left)):
			if close(r, den_left[idx][0], 1e-6):
				matched_idx = idx
				break
		if matched_idx < 0:
			num_left.append((r, m))
			continue
		r2, m2 = den_left[matched_idx]
		hole_mult = min(m, m2)
		holes.append((r, hole_mult))
		# leftover multiplicities stay on whichever side had more
		if m2 - hole_mult > 0:
			den_left[matched_idx] = (r2, m2 - hole_mult)
		else:
			den_left.pop(matched_idx)
		if m - hole_mult > 0:
			num_left.append((r, m - hole_mult))
	return holes, num_left, den_left


def reduce_by_holes(coeffs, holes):
	"""Divide out each hole factor (x - r)^m via synthetic division."""
	reduced = list(coeffs)
	for r, m in holes:
		for _ in range(m):
			q, _ = synth_divide(reduced, r)
			reduced = q
	return reduced


def _is_zero_poly(coeffs):
	"""True when the polynomial is identically zero."""
	return all(c == 0 for c in coeffs)


def _zero_numerator_result(num_coeffs, den_coeffs):
	"""Build the result for 0 / D(x): constant 0 with holes at den roots."""
	_, den_roots_raw, _ = factor(den_coeffs)
	den_roots = merge_roots(den_roots_raw)
	# every denominator root is a removable hole, not a VA
	holes = list(den_roots)
	result = {
		'holes': holes,
		'vas': [],
		'xints': [],
		'yint': 0.0 if poly_eval(den_coeffs, 0) != 0 else None,
		'end': ('constant', 0.0),
		'num_coeffs': num_coeffs,
		'den_coeffs': den_coeffs,
		'red_num': [0],
		'red_den': [1],
		'crit': sorted(r for r, _ in holes),
	}
	return result


def analyze(num_coeffs, den_coeffs):
	"""Full analysis pipeline. Returns a result dict."""
	# zero denominator: function is undefined everywhere, no analysis to do
	if _is_zero_poly(den_coeffs):
		raise ValueError('denominator is identically zero')
	# zero numerator: f(x) = 0 everywhere, with removable undefined points
	# at every root of the denominator; skip factoring logic entirely
	if _is_zero_poly(num_coeffs):
		return _zero_numerator_result(num_coeffs, den_coeffs)
	_num_lead, num_roots_raw, _num_res = factor(num_coeffs)
	_den_lead, den_roots_raw, _den_res = factor(den_coeffs)
	num_roots = merge_roots(num_roots_raw)
	den_roots = merge_roots(den_roots_raw)
	holes, xints, vas = compute_holes_and_remainders(num_roots, den_roots)
	# reduce both sides by shared factors so downstream analysis sees
	# the cancelled function, not the raw one
	red_num = reduce_by_holes(num_coeffs, holes)
	red_den = reduce_by_holes(den_coeffs, holes)
	red_num_deg = len(red_num) - 1
	red_den_deg = len(red_den) - 1
	# y-intercept of the reduced function (holes don't produce a y-value)
	den0 = poly_eval(red_den, 0)
	if den0 != 0:
		yint = poly_eval(red_num, 0) / den0
	else:
		yint = None
	# when the reduced denominator is a constant, the function is a
	# polynomial; label by its degree rather than calling it an asymptote
	if red_den_deg == 0:
		# divide out the constant so the quotient has unit denominator
		c = red_den[0]
		quot = [v / c for v in red_num]
		if red_num_deg == 0:
			end = ('constant', quot[0])
		elif red_num_deg == 1:
			end = ('linear', quot)
		else:
			end = ('polynomial', quot)
	elif red_num_deg < red_den_deg:
		end = ('ha', 0.0)
	elif red_num_deg == red_den_deg:
		end = ('ha', red_num[0] / red_den[0])
	elif red_num_deg == red_den_deg + 1:
		quot, _ = poly_divmod(red_num, red_den)
		end = ('slant', quot)
	else:
		end = ('poly', red_num_deg - red_den_deg)
	# breakpoints for sign chart: VAs, x-intercepts, AND holes (any
	# discontinuity splits the sign row, even when the reduced function
	# has a finite limit across the hole)
	crit = [r for r, _ in vas] + [r for r, _ in xints] + [r for r, _ in holes]
	crit.sort()
	result = {
		'holes': holes,
		'vas': vas,
		'xints': xints,
		'yint': yint,
		'end': end,
		'num_coeffs': num_coeffs,
		'den_coeffs': den_coeffs,
		'red_num': red_num,
		'red_den': red_den,
		'crit': crit,
	}
	return result


#============================================
# Sign chart
#============================================

def sign_chart(result):
	"""
	Return a list of (side, interval_str) tuples describing the sign of
	the reduced function on each interval between critical x-values.

	`side` is one of 'above', 'below', 'zero', 'undef'. `interval_str`
	looks like "(-inf, -2)".
	"""
	crit = result['crit']
	# evaluate the reduced function so cancelled factors don't distort signs
	num_coeffs = result['red_num']
	den_coeffs = result['red_den']
	# pick a test point per interval: one outside each end, midpoints inside
	if not crit:
		points = [0.0]
	else:
		points = [crit[0] - 1.0]
		for i in range(len(crit) - 1):
			points.append((crit[i] + crit[i + 1]) / 2)
		points.append(crit[-1] + 1.0)
	labels = ['-inf'] + [fmt_num(c) for c in crit] + ['inf']
	intervals = []
	for i in range(len(points)):
		tp = points[i]
		nv = poly_eval(num_coeffs, tp)
		dv = poly_eval(den_coeffs, tp)
		if dv == 0:
			side = 'undef'
		elif nv / dv > 0:
			side = 'above'
		elif nv / dv < 0:
			side = 'below'
		else:
			side = 'zero'
		interval = '(' + labels[i] + ', ' + labels[i + 1] + ')'
		intervals.append((side, interval))
	return intervals


#============================================
# Output formatting
#============================================

def fmt_poly(p):
	"""Format polynomial coefficient list as a human-readable string."""
	p = poly_trim(p)
	n = len(p) - 1
	parts = []
	for i in range(len(p)):
		c = p[i]
		deg = n - i
		if close(c, 0, 1e-9):
			continue
		# variable piece
		if deg == 0:
			var = ''
		elif deg == 1:
			var = 'x'
		else:
			var = 'x^' + str(deg)
		# coefficient piece, with +1/-1 suppression for non-constant terms
		if deg > 0 and close(c, 1):
			cstr = ''
		elif deg > 0 and close(c, -1):
			cstr = '-'
		else:
			cstr = fmt_num(c)
		term = cstr + var
		# glue with + separator except when the term already starts with '-'
		if parts and not term.startswith('-'):
			parts.append('+' + term)
		else:
			parts.append(term)
	if not parts:
		return '0'
	return ''.join(parts)


def _print_section(title, value_lines):
	"""Print a section with a heading and one value per line."""
	print(title)
	for line in value_lines:
		print(line)
	# blank line separator between sections; TI Home-screen scrolls
	print('')


def print_result(result):
	"""Print analysis in a TI-friendly full-label format."""
	# vertical asymptotes
	vas = result['vas']
	if vas:
		lines = ['x = ' + fmt_num(r) for r, _ in vas]
	else:
		lines = ['none']
	_print_section('Vertical asymptote', lines)
	# holes
	holes = result['holes']
	if holes:
		lines = ['x = ' + fmt_num(r) for r, _ in holes]
	else:
		lines = ['none']
	_print_section('Hole', lines)
	# x-intercepts
	xints = result['xints']
	if xints:
		lines = ['x = ' + fmt_num(r) for r, _ in xints]
	else:
		lines = ['none']
	_print_section('X-intercepts', lines)
	# y-intercept
	if result['yint'] is not None:
		_print_section('Y-intercept', ['y = ' + fmt_num(result['yint'])])
	else:
		_print_section('Y-intercept', ['undefined'])
	# end behavior
	end = result['end']
	if end[0] == 'ha':
		_print_section('Horizontal asymptote', ['y = ' + fmt_num(end[1])])
	elif end[0] == 'slant':
		_print_section('Slant asymptote', ['y = ' + fmt_poly(end[1])])
	elif end[0] == 'constant':
		_print_section('Constant function', ['y = ' + fmt_num(end[1])])
	elif end[0] == 'linear':
		_print_section('Linear function', ['y = ' + fmt_poly(end[1])])
	elif end[0] == 'polynomial':
		_print_section('Polynomial function', ['y = ' + fmt_poly(end[1])])
	else:
		_print_section('End behavior', ['no linear asymptote'])
	# sign chart, in prose form
	for side, interval in sign_chart(result):
		if side == 'above':
			print('Above x-axis on')
		elif side == 'below':
			print('Below x-axis on')
		elif side == 'zero':
			print('On x-axis on')
		else:
			print('Undefined on')
		print(interval)


#============================================
# Main entry
#============================================

def main():
	print('Rational analyzer')
	print('Integer coefs only.')
	print('Use x, ^, and ( ).')
	print('Ex: (x+2)(x-3)')
	print('')
	# two-line prompts avoid wrapping on the narrow TI-84 screen
	print('Enter numerator:')
	num_str = input()
	print('Enter denominator:')
	den_str = input()
	num_coeffs = parse(num_str)
	den_coeffs = parse(den_str)
	result = analyze(num_coeffs, den_coeffs)
	print_result(result)


if __name__ == '__main__':
	main()
