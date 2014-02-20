# coding: utf-8
"""
    pyalysis.ignore.compiler
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from io import StringIO
from contextlib import contextmanager
import __builtin__

from pyalysis.warnings import WARNINGS
from pyalysis.ignore.ast import (
    BinaryOperation, Equal, LessThan, GreaterThan, LessOrEqualThan,
    GreaterOrEqualThan, Name, String, Integer
)
from pyalysis._compat import text_type


def compile(filters):
    """
    Given a list of :class:`pyalysis.ignore.ast.Filter` instances as returned
    by :class:`pyalysis.ignore.verifier.verify`, returns a callable that called
    with a warning returns `True`, if the warning didn't match.
    """
    return Compiler(filters).compile()


class Compiler(object):
    def __init__(self, filters):
        self.filters = filters
        self.source = StringIO()
        self.indentation = 0

    @contextmanager
    def indented(self):
        self.indentation += 4
        yield
        self.indentation -= 4

    def write(self, source):
        self.source.write(source)

    def write_indentation(self):
        self.write(u' ' * self.indentation)

    def write_newline(self):
        self.write(u'\n')

    def write_line(self, line):
        self.write_indentation()
        self.write(line)
        self.write_newline()

    def compile(self):
        self.write_line(u'from pyalysis.warnings import WARNINGS')
        self.write_line(u'def predicate(warning):')
        with self.indented():
            for filter in self.filters:
                self.compile_filter(filter)
            self.write_line(u'return True')
        print self.source.getvalue()
        code = __builtin__.compile(self.source.getvalue(), '', 'exec')
        locals = {}
        exec(code, {'WARNINGS': WARNINGS}, locals)
        return locals['predicate']

    def compile_filter(self, filter):
        self.write_line(
            u'if isinstance(warning, WARNINGS["{}"]):'.format(filter.name)
        )
        with self.indented():
            self.write_indentation()
            self.write(u'return ')
            if filter.expressions:
                self.write(u'not (')
                for expression in filter.expressions[:-1]:
                    self.compile_expression(expression)
                    self.write(u' or ')
                self.compile_expression(filter.expressions[-1])
                self.write(u')')
            else:
                self.write(u'False')
            self.write_newline()

    def compile_expression(self, expression):
        if isinstance(expression, BinaryOperation):
            return self.compile_binary_operation(expression)
        raise NotImplementedError(expression)

    def compile_binary_operation(self, operation):
        op = {
            Equal: u'==',
            LessThan: u'<',
            GreaterThan: u'>',
            LessOrEqualThan: u'<=',
            GreaterOrEqualThan: u'>='
        }[operation.__class__]
        self.write(u'(')
        if isinstance(operation.left, Name):
            self.compile_name(operation.left)
        else:
            self.compile_literal(operation.left)
        self.write(u' ')
        self.write(op)
        self.write(u' ')
        if isinstance(operation.right, Name):
            self.compile_name(operation.right)
        else:
            self.compile_literal(operation.right)
        self.write(u')')

    def compile_name(self, name):
        self.write(u'warning.')
        self.write(name.name)

    def compile_literal(self, literal):
        if isinstance(literal, String):
            self.write(u'"{}"'.format(literal.value))
        elif isinstance(literal, Integer):
            self.write(text_type(literal.value))
        else:
            raise NotImplementedError(literal)
