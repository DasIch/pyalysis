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


@pytest.mark.parametrize(('source', 'warning', 'allowed'), [
    (u'print-statement', PrintStatement(u'message', '<test>', 1), False),
    (u'print-statement', DivStatement(u'message', '<test>', 1), True),
    (
        u'print-statement \n message = "foo"',
        PrintStatement(u'foo', '<test>', 1),
        False
    ),
    (
        u'print-statement \n message = "foo"',
        PrintStatement(u'bar', '<test>', 1),
        True
    ),
    (
        u'print-statement \n lineno = 1',
        PrintStatement(u'foo', '<test>', 1),
        False
    ),
    (
        u'print-statement \n lineno = 1',
        PrintStatement(u'foo', '<test>', 2),
        True
    ),
    (
        u'print-statement \n lineno < 3',
        PrintStatement(u'foo', '<test>', 1),
        False
    ),
    (
        u'print-statement \n lineno < 3',
        PrintStatement(u'foo', '<test>', 2),
        False
    ),
    (
        u'print-statement \n lineno < 3',
        PrintStatement(u'foo', '<test>', 3),
        True
    ),
    (
        u'print-statement \n lineno > 1',
        PrintStatement(u'foo', '<test>', 1),
        True
    ),
    (
        u'print-statement \n lineno > 1',
        PrintStatement(u'foo', '<test>', 2),
        False
    ),
    (
        u'print-statement \n lineno <= 2',
        PrintStatement(u'foo', '<test>', 1),
        False
    ),
    (
        u'print-statement \n lineno <= 2',
        PrintStatement(u'foo', '<test>', 2),
        False
    ),
    (
        u'print-statement \n lineno <= 2',
        PrintStatement(u'foo', '<test>', 3),
        True
    ),
    (
        u'print-statement \n lineno >= 2',
        PrintStatement(u'foo', '<test>', 1),
        True
    ),
    (
        u'print-statement \n lineno >= 2',
        PrintStatement(u'foo', '<test>', 2),
        False
    ),
    (
        u'print-statement \n lineno >= 2',
        PrintStatement(u'foo', '<test>', 3),
        False
    )
])
def test_compile(source, warning, allowed):
    file = StringIO(source)
    file.name = '<test>'
    filter = compile(verify(file, parse(lex(file.read())))[0])
    assert filter(warning) == allowed
