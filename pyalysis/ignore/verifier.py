# coding: utf-8
"""
    pyalysis.ignore.verifier
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import warnings

from pyalysis.warnings import WARNINGS
from pyalysis.ignore.ast import Equal, Name, String, Integer
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
    if isinstance(expression, Equal):
        return verify_equal(warning, expression)


def verify_equal(warning, equal):
    if isinstance(equal.left, Name) and isinstance(equal.right, Name):
        warnings.warn(
            (
                u'Ignoring equal expression with missing constant in line '
                u'{}.'
            ).format(equal.start.line),
            IgnoreVerificationWarning
        )
        return False
    elif not (isinstance(equal.left, Name) or isinstance(equal.right, Name)):
        warnings.warn(
            (
                u'Ignoring equal expression with missing name in line '
                u'{}.'
            ).format(equal.start.line),
            IgnoreVerificationWarning
        )
        return False
    name_node = equal.left if isinstance(equal.left, Name) else equal.right
    if name_node.name not in (name for (name, _) in warning.attributes):
        warnings.warn(
            (
                u'Ignoring equal expression with "{}". "{}" doesn\'t have '
                u'such an attribute to compare to. Line {}.'
            ).format(name_node.name, warning.type, equal.start.line),
            IgnoreVerificationWarning
        )
        return False

    type_node = equal.right if isinstance(equal.left, Name) else equal.left
    attribute_type = next(
        type for (n, type) in warning.attributes if n == name_node.name
    )
    if isinstance(type_node, String):
        comparision_type = text_type
        type_name = u'string'
    elif isinstance(type_node, Integer):
        comparision_type = int
        type_name = u'integer'
    if not issubclass(comparision_type, attribute_type):
        warnings.warn(
            u'Ignoring equal expression in line {}. "{}" is not of type '
            u'{}.' \
                .format(equal.start.line, name_node.name, type_name)
        )
        return False
    return True
