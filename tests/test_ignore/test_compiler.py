# coding: utf-8
"""
    tests.test_ignore.test_compiler
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from io import StringIO

import pytest

from pyalysis.warnings import PrintStatement, DivStatement
from pyalysis.ignore.lexer import lex
from pyalysis.ignore.parser import parse
from pyalysis.ignore.verifier import verify
from pyalysis.ignore.compiler import compile
from pyalysis.utils import Location


@pytest.mark.parametrize(('source', 'warning', 'allowed'), [
    (
        u'print-statement',
        PrintStatement(
            u'message', '<test>', Location(1, 0), Location(1, 10), []
        ),
        False
    ),
    (
        u'print-statement',
        DivStatement(
            u'message', '<test>', Location(1, 0), Location(1, 10), []
        ),
        True
    ),
    (
        u'print-statement \n message = "foo"',
        PrintStatement(u'foo', '<test>', Location(1, 0), Location(1, 10), []),
        False
    ),
    (
        u'print-statement \n message = "foo"',
        PrintStatement(u'bar', '<test>', Location(1, 0), Location(1, 10), []),
        True
    )
])
def test_compile(source, warning, allowed):
    file = StringIO(source)
    file.name = '<test>'
    filter = compile(verify(file, parse(lex(file.read())))[0])
    assert filter(warning) == allowed
