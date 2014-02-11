# coding: utf-8
"""
    tests.test_ignore
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import pytest

from pyalysis.ignore.lexer import lex
from pyalysis.ignore.tokens import Name, Location
from pyalysis.ignore.parser import parse
from pyalysis.ignore.ast import IgnoreFile, Filter


@pytest.mark.parametrize(('source', 'tokens'), [
    (u'foo', [Name(u'foo', Location(1, 0), Location(1, 3))]),
    (u'foo\nbar', [
        Name(u'foo', Location(1, 0), Location(1, 3)),
        Name(u'\n', Location(1, 3), Location(2, 0)),
        Name(u'bar', Location(2, 0), Location(2, 3))
    ])
])
def test_lexer(source, tokens):
    assert list(lex(source)) == tokens


@pytest.mark.parametrize(('source', 'ast'), [
    (u'foo', IgnoreFile('<test>', [
        Filter(u'foo', Location(1, 0), Location(1, 3))
    ])),
    (u'foo\nbar', IgnoreFile('<test>', [
        Filter(u'foo', Location(1, 0), Location(1, 3)),
        Filter(u'bar', Location(2, 0), Location(2, 3))
    ]))
])
def test_parser(source, ast):
    assert parse(lex(source), '<test>') == ast
