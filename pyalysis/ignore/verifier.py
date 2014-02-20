# coding: utf-8
"""
    pyalysis.ignore.verifier
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from pyalysis.warnings import Warning, WARNINGS
from pyalysis.ignore.ast import (
    Equal, String, Integer, BinaryOperation, LessThan, GreaterThan,
    LessOrEqualThan, GreaterOrEqualThan
)
from pyalysis._compat import text_type


class IgnoreVerificationWarning(Warning):
    """
    Represents a warning for semantic issue with the contents of an ignore
    file.
    """
    def __init__(self, message, file, start, end, lines):
        Warning.__init__(self, message, file)
        self.start = start
        self.end = end
        self.lines = lines

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                self.message == other.message and
                self.file == other.file and
                self.start == other.start and
                self.end == other.end and
                self.lines == other.lines
            )
        return NotImplemented


def verify(ignore_file, ast):
    """
    Takes a file-like object `ignore_file` and a
    :class:`pyalysis.ignore.ast.IgnoreFile` instance `ast`.

    Returns a tuple with a list of :class:`pyalysis.ignore.ast.Filter` objects
    and a list of :class:`IgnoreVerificationWarning` objects.

    The filters are taken from the given `ast`. Individual filters will have
    invalid expressions removed and filters that cannot be coerced into valid
    filters will be removed entirely.
    """
    return _Verifier(ignore_file, ast).verify()


class _Verifier(object):
    def __init__(self, ignore_file, ast):
        self.ignore_file = ignore_file
        self.ast = ast

        self.warnings = []
        self.ignore_file.seek(0)
        self._lines = self.ignore_file.readlines()

    def get_lines(self, start, end):
        return self._lines[start.line-1:end.line]

    def emit(self, message, node):
        self.warnings.append(IgnoreVerificationWarning(
            message,
            self.ignore_file.name,
            node.start,
            node.end,
            self.get_lines(node.start, node.end)
        ))

    def verify(self):
        filters = list(filter(None, map(self.verify_filter, self.ast.filters)))
        return filters, self.warnings

    def verify_filter(self, filter):
        try:
            warning = WARNINGS[filter.name]
        except KeyError:
            self.emit(
                u'Ignoring filter with unknown warning type "{}".'
                .format(filter.name),
                filter
            )
            return None
        filter.expressions = [
            expression for expression in filter.expressions
            if self.verify_expression(warning, expression)
        ]
        return filter

    def verify_expression(self, warning, expression):
        if isinstance(expression, BinaryOperation):
            return self.verify_binary_operation(warning, expression)

    def verify_binary_operation(self, warning, operation):
        operation_name = {
            Equal: u'equal',
            LessThan: u'less than',
            GreaterThan: u'greater than',
            LessOrEqualThan: u'less or equal than',
            GreaterOrEqualThan: u'greater or equal than'
        }[operation.__class__]
        if operation.literal is None:
            self.emit(
                u'Ignoring {} expression with missing constant.'
                .format(operation_name),
                operation
            )
            return False
        if operation.name is None:
            self.emit(
                u'Ignoring {} expression with missing name.'
                .format(operation_name),
                operation
            )
            return False
        if (
            operation.name.name not in (
                name for (name, _) in warning.attributes
            )
        ):
            self.emit(
                (
                    u'Ignoring {} expression with "{}". "{}" doesn\'t have '
                    u'such an attribute to compare to.'
                ).format(operation_name, operation.name.name, warning.type),
                operation
            )
            return False

        attribute_type = next(
            type for (n, type) in warning.attributes
            if n == operation.name.name
        )
        literal_type, literal_type_name = {
            String: (text_type, u'string'),
            Integer: (int, u'integer')
        }[operation.literal.__class__]
        if not issubclass(literal_type, attribute_type):
            self.emit(
                u'Ignoring {} expression. "{}" is not of type {}.'
                .format(
                    operation_name, operation.name.name,
                    literal_type_name
                ),
                operation
            )
            return False
        return True
