# coding: utf-8
"""
    pyalysis.ignore.verifier
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import warnings

from pyalysis.warnings import WARNINGS
from pyalysis.ignore.ast import (
    Equal, Name, String, Integer, BinaryOperation, LessThan
)
from pyalysis._compat import text_type


class IgnoreVerificationWarning(UserWarning):
    pass


def verify(ignore_file):
    for filter in ignore_file.filters:
        filter = verify_filter(filter)
        if filter is not None:
            yield filter


def verify_filter(filter):
    try:
        warning = WARNINGS[filter.name]
    except KeyError:
        warnings.warn(
            (
                u'Ignoring filter with unknown warning type: '
                u'"{}" in line {}.'
            ).format(filter.name, filter.start.line),
            IgnoreVerificationWarning
        )
        return None
    filter.expressions = [
        expression for expression in filter.expressions
        if verify_expression(warning, expression)
    ]
    return filter


def verify_expression(warning, expression):
    if isinstance(expression, BinaryOperation):
        return verify_binary_operation(warning, expression)


def verify_binary_operation(warning, operation):
    operation_name = {
        Equal: u'equal',
        LessThan: u'less than'
    }[operation.__class__]
    if isinstance(operation.left, Name) and isinstance(operation.right, Name):
        warnings.warn(
            (
                u'Ignoring {} expression with missing constant in line '
                u'{}.'
            ).format(operation_name, operation.start.line),
            IgnoreVerificationWarning
        )
        return False
    has_name = (
        isinstance(operation.left, Name) or
        isinstance(operation.right, Name)
    )
    if not has_name:
        warnings.warn(
            (
                u'Ignoring {} expression with missing name in line '
                u'{}.'
            ).format(operation_name, operation.start.line),
            IgnoreVerificationWarning
        )
        return False
    if isinstance(operation.left, Name):
        name_node = operation.left
        literal_node = operation.right
    else:
        name_node = operation.right
        literal_node = operation.left
    if name_node.name not in (name for (name, _) in warning.attributes):
        warnings.warn(
            (
                u'Ignoring {} expression with "{}". "{}" doesn\'t have '
                u'such an attribute to compare to. Line {}.'
            ).format(
                operation_name, name_node.name, warning.type,
                operation.start.line
            ),
            IgnoreVerificationWarning
        )
        return False

    attribute_type = next(
        type for (n, type) in warning.attributes if n == name_node.name
    )
    literal_type, literal_type_name = {
        String: (text_type, u'string'),
        Integer: (int, u'integer')
    }[literal_node.__class__]
    if not issubclass(literal_type, attribute_type):
        warnings.warn(
            (
                u'Ignoring {} expression in line {}. "{}" is not of type '
                u'{}.'
            ).format(
                operation_name, operation.start.line, name_node.name,
                literal_type_name
            )
        )
        return False
    return True
