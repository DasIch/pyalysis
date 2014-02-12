# coding: utf-8
"""
    pyalysis.ignore.compiler
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from pyalysis.warnings import WARNINGS
from pyalysis.ignore.ast import Equal, Name, String, LessThan


def compile(filters):
    compiled = map(compile_filter, filters)
    return lambda warning: any(f(warning) for f in compiled)


def compile_filter(filter):
    warning_cls = WARNINGS[filter.name]
    matches_expressions = compile_expressions(filter.expressions)
    def _(warning):
        if isinstance(warning, warning_cls):
            return not matches_expressions(warning)
        return True
    return _


def compile_expressions(expressions):
    matchers = list(map(compile_expression, expressions))
    return lambda warning: all(matcher(warning) for matcher in matchers)


def compile_expression(expression):
    if isinstance(expression, Equal):
        return compile_equal(expression)
    elif isinstance(expression, LessThan):
        return compile_less_than(expression)
    else:
        raise NotImplementedError(expression)


def compile_equal(equal):
    if isinstance(equal.left, Name):
        name = equal.left.name
        value = equal.right.value
    else:
        name = equal.right.name
        value = equal.left.value
    return lambda warning: getattr(warning, name) == value


def compile_less_than(less_than):
    if isinstance(less_than.left, Name):
        name = less_than.left.name
        value = less_than.right.value
    else:
        name = less_than.right.name
        value = less_than.left.value
    return lambda warning: getattr(warning, name) < value
