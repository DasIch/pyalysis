# coding: utf-8
"""
    tests.test_ignore.lexer
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import pytest

from pyalysis.ignore import tokens
from pyalysis.ignore.tokens import Location
from pyalysis.ignore.lexer import lex


@pytest.mark.parametrize(('source', 'tokens'), [
    (u'foo', [tokens.Name(u'foo', Location(1, 0), Location(1, 3))]),
    (u'foo\nbar', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Name(u'bar', Location(2, 0), Location(2, 3))
    ]),
    (u'foo\n    spam = "eggs"', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Indent(u'    ', Location(2, 0), Location(2, 4)),
        tokens.Name(u'spam', Location(2, 4), Location(2, 8)),
        tokens.Operator(u'=', Location(2, 9), Location(2, 10)),
        tokens.String(u'"eggs"', Location(2, 11), Location(2, 17)),
        tokens.Dedent(u'', Location(2, 17), Location(2, 17))
    ]),
    (u'foo\n    spam = 1', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Indent(u'    ', Location(2, 0), Location(2, 4)),
        tokens.Name(u'spam', Location(2, 4), Location(2, 8)),
        tokens.Operator(u'=', Location(2, 9), Location(2, 10)),
        tokens.Integer(u'1', Location(2, 11), Location(2, 12)),
        tokens.Dedent(u'', Location(2, 12), Location(2, 12))
    ]),
    (u'foo\n    spam < 1', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Indent(u'    ', Location(2, 0), Location(2, 4)),
        tokens.Name(u'spam', Location(2, 4), Location(2, 8)),
        tokens.Operator(u'<', Location(2, 9), Location(2, 10)),
        tokens.Integer(u'1', Location(2, 11), Location(2, 12)),
        tokens.Dedent(u'', Location(2, 12), Location(2, 12))
    ]),
    (u'foo\n    spam > 1', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Indent(u'    ', Location(2, 0), Location(2, 4)),
        tokens.Name(u'spam', Location(2, 4), Location(2, 8)),
        tokens.Operator(u'>', Location(2, 9), Location(2, 10)),
        tokens.Integer(u'1', Location(2, 11), Location(2, 12)),
        tokens.Dedent(u'', Location(2, 12), Location(2, 12))
    ]),
    (u'foo\n    spam <= 1', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Indent(u'    ', Location(2, 0), Location(2, 4)),
        tokens.Name(u'spam', Location(2, 4), Location(2, 8)),
        tokens.Operator(u'<=', Location(2, 9), Location(2, 11)),
        tokens.Integer(u'1', Location(2, 12), Location(2, 13)),
        tokens.Dedent(u'', Location(2, 13), Location(2, 13))
    ]),
    (u'foo\n    spam >= 1', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Indent(u'    ', Location(2, 0), Location(2, 4)),
        tokens.Name(u'spam', Location(2, 4), Location(2, 8)),
        tokens.Operator(u'>=', Location(2, 9), Location(2, 11)),
        tokens.Integer(u'1', Location(2, 12), Location(2, 13)),
        tokens.Dedent(u'', Location(2, 13), Location(2, 13))
    ])
])
def test_lexer(source, tokens):
    assert list(lex(source)) == tokens

