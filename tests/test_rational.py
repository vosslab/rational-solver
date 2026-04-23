"""Tests for rational.py parser, factorer, and analyzer helpers."""

# Standard Library
import sys
import math

# local repo modules
import git_file_utils

REPO_ROOT = git_file_utils.get_repo_root()
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

import rational


#============================================
# Parser
#============================================

def test_parse_expanded_simple():
	assert rational.parse('3x^2-27') == [3, 0, -27]


def test_parse_expanded_signs():
	assert rational.parse('-2x^2+5x-1') == [-2, 5, -1]


def test_parse_factored_two_linears():
	assert rational.parse('(x+2)(x-3)') == [1, -1, -6]


def test_parse_factored_with_leading_coef():
	assert rational.parse('3(x-1)^2') == [3, -6, 3]


def test_parse_factored_negative_lead():
	# -(x+1)^2 = -(x^2 + 2x + 1) = [-1, -2, -1]
	assert rational.parse('-(x+1)^2') == [-1, -2, -1]


def test_parse_factored_quadratic_inside():
	# (x-1)(x^2+1) -> x^3 - x^2 + x - 1
	assert rational.parse('(x-1)(x^2+1)') == [1, -1, 1, -1]


def test_tokenize_rejects_junk():
	try:
		rational.parse('x@2')
	except ValueError:
		return
	raise AssertionError('expected ValueError')


#============================================
# Polynomial arithmetic
#============================================

def test_poly_eval_horner():
	# 3x^2 - 27 at x=3 is zero
	assert rational.poly_eval([3, 0, -27], 3) == 0


def test_poly_divmod_slant():
	# (3x^2 - 27) / (x - 3) = 3x + 9 remainder 0
	q, r = rational.poly_divmod([3, 0, -27], [1, -3])
	assert q == [3, 9]
	assert all(abs(v) < 1e-9 for v in r)


#============================================
# Factorer
#============================================

def test_factor_rational_roots():
	# x^2 - x - 6 factors as (x+2)(x-3)
	lead, roots, res = rational.factor([1, -1, -6])
	vals = sorted(r for r, _ in roots)
	assert lead == 1
	assert math.isclose(vals[0], -2.0)
	assert math.isclose(vals[1], 3.0)


def test_factor_irrational_quadratic():
	# x^2 - 2 -> roots +/- sqrt(2)
	_, roots, _ = rational.factor([1, 0, -2])
	vals = sorted(r for r, _ in roots)
	assert math.isclose(vals[0], -math.sqrt(2), abs_tol=1e-9)
	assert math.isclose(vals[1], math.sqrt(2), abs_tol=1e-9)


def test_factor_repeated_root():
	# (x-1)^2 -> single root 1 with multiplicity 2
	_, roots, _ = rational.factor([1, -2, 1])
	assert len(roots) == 1
	r, m = roots[0]
	assert math.isclose(r, 1.0)
	assert m == 2


def test_factor_irreducible_remains():
	# x^2 + 1 has no real roots; residual survives
	_, roots, res = rational.factor([1, 0, 1])
	assert roots == []
	assert len(res) == 3


#============================================
# Analyzer (full pipeline)
#============================================

def test_analyze_basic_rational():
	num = rational.parse('(x+2)(x-3)')
	den = rational.parse('(x+6)(x-1)')
	result = rational.analyze(num, den)
	vas = sorted(r for r, _ in result['vas'])
	xints = sorted(r for r, _ in result['xints'])
	assert [round(v, 6) for v in vas] == [-6.0, 1.0]
	assert [round(v, 6) for v in xints] == [-2.0, 3.0]
	assert result['holes'] == []
	assert result['end'][0] == 'ha'
	assert math.isclose(result['end'][1], 1.0)
	assert math.isclose(result['yint'], 1.0)


def test_analyze_hole_detection():
	# (x-2)(x+1) / ((x-2)(x+3)) -> hole at x=2, VA at x=-3
	num = rational.parse('(x-2)(x+1)')
	den = rational.parse('(x-2)(x+3)')
	result = rational.analyze(num, den)
	holes = [r for r, _ in result['holes']]
	vas = [r for r, _ in result['vas']]
	assert len(holes) == 1
	assert math.isclose(holes[0], 2.0)
	assert len(vas) == 1
	assert math.isclose(vas[0], -3.0)


def test_analyze_reduces_to_linear():
	# (3x^2 - 27) / (x - 3): hole at x=3, reduces to y = 3x+9 (Linear, not Slant)
	num = rational.parse('3x^2-27')
	den = rational.parse('x-3')
	result = rational.analyze(num, den)
	holes = [r for r, _ in result['holes']]
	assert len(holes) == 1
	assert math.isclose(holes[0], 3.0)
	assert result['end'][0] == 'linear'
	q = result['end'][1]
	assert math.isclose(q[0], 3.0, abs_tol=1e-6)
	assert math.isclose(q[1], 9.0, abs_tol=1e-6)


def test_analyze_constant_denominator_is_linear():
	# (x - 4) / 3 -> Linear: y = x/3 - 4/3
	result = rational.analyze(rational.parse('x-4'), rational.parse('3'))
	assert result['end'][0] == 'linear'
	q = result['end'][1]
	assert math.isclose(q[0], 1.0 / 3.0, abs_tol=1e-6)
	assert math.isclose(q[1], -4.0 / 3.0, abs_tol=1e-6)


def test_analyze_true_slant_unchanged():
	# x^2 / (x - 1) has no hole; must remain Slant
	result = rational.analyze(rational.parse('x^2'), rational.parse('x-1'))
	assert result['end'][0] == 'slant'


def test_analyze_reduces_to_constant():
	# (x-5) / (x-5) -> hole at x=5, Constant: y=1
	result = rational.analyze(rational.parse('x-5'), rational.parse('x-5'))
	assert result['end'][0] == 'constant'
	assert math.isclose(result['end'][1], 1.0)


def test_analyze_horizontal_ratio():
	# 2x^2 / (x^2 + 1) -> HA y = 2
	num = rational.parse('2x^2')
	den = rational.parse('x^2+1')
	result = rational.analyze(num, den)
	assert result['end'][0] == 'ha'
	assert math.isclose(result['end'][1], 2.0)


def test_sign_chart_runs():
	num = rational.parse('(x+2)(x-3)')
	den = rational.parse('(x+6)(x-1)')
	result = rational.analyze(num, den)
	intervals = rational.sign_chart(result)
	# every interval string ends with a sign marker
	assert all(iv[-1] in '+-0?' for iv in intervals)


#============================================
# Formatting
#============================================

def test_fmt_num_integral():
	assert rational.fmt_num(3.0) == '3'
	assert rational.fmt_num(-2.0) == '-2'


def test_fmt_poly_mixed():
	# 3x^2 + 0x - 27 -> "3x^2-27"
	assert rational.fmt_poly([3, 0, -27]) == '3x^2-27'
