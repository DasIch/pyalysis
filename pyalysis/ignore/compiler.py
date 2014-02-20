# coding: utf-8
"""
    pyalysis.ignore.compiler
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import operator

from pyalysis.warnings import WARNINGS
from pyalysis.ignore.ast import (
    BinaryOperation, Equal, LessThan, GreaterThan, LessOrEqualThan,
    GreaterOrEqualThan
)


def compile(filters):
    """
    Given a list of :class:`pyalysis.ignore.ast.Filter` instances as returned
    by :class:`pyalysis.ignore.verifier.verify`, returns a callable that called
    with a warning returns `True`, if the warning didn't match.
    """
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
    if isinstance(expression, BinaryOperation):
        return compile_binary_operation(expression)
    raise NotImplementedError(expression)


def compile_binary_operation(operation):
    op = {
        Equal: operator.eq,
        LessThan: operator.lt,
        GreaterThan: operator.gt,
        LessOrEqualThan: operator.le,
        GreaterOrEqualThan: operator.ge
    }[operation.__class__]
    return lambda warning: op(
        getattr(warning, operation.name.name),
        operation.literal.value
    )
