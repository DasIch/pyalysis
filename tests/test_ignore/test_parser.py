# coding: utf-8
"""
    tests.test_ignore.parser
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import pytest

from pyalysis.ignore import ast
from pyalysis.ignore.tokens import Location
from pyalysis.ignore.lexer import lex
from pyalysis.ignore.parser import parse


@pytest.mark.parametrize(('source', 'ast'), [
    (u'foo', ast.IgnoreFile('<test>', [
        ast.Filter(u'foo', [], Location(1, 0), Location(1, 3))
    ])),
    (u'foo\nbar', ast.IgnoreFile('<test>', [
        ast.Filter(u'foo', [], Location(1, 0), Location(1, 3)),
        ast.Filter(u'bar', [], Location(2, 0), Location(2, 3))
    ])),
    (u'foo\n    spam = "eggs"', ast.IgnoreFile('<test>', [
        ast.Filter(
            u'foo',
            [
                ast.Equal(
                    ast.Name(u'spam', Location(2, 4), Location(2, 8)),
                    ast.String(u'eggs', Location(2, 11), Location(2, 17)),
                    Location(2, 4),
                    Location(2, 17)
                )
            ],
            Location(1, 0),
            Location(2, 17)
        )
    ])),
    (u'foo\n    spam = 1', ast.IgnoreFile('<test>', [
        ast.Filter(
            u'foo',
            [
                ast.Equal(
                    ast.Name(u'spam', Location(2, 4), Location(2, 8)),
                    ast.Integer(1, Location(2, 11), Location(2, 12)),
                    Location(2, 4),
                    Location(2, 12)
                )
            ],
            Location(1, 0),
            Location(2, 12)
        )
    ])),
    (u'foo\n    spam < 1', ast.IgnoreFile('<test>', [
        ast.Filter(
            u'foo',
            [
                ast.LessThan(
                    ast.Name(u'spam', Location(2, 4), Location(2, 8)),
                    ast.Integer(1, Location(2, 11), Location(2, 12)),
                    Location(2, 4),
                    Location(2, 12)
                )
            ],
            Location(1, 0),
            Location(2, 12)
        )
    ])),
    (u'foo\n    spam > 1', ast.IgnoreFile('<test>', [
        ast.Filter(
            u'foo',
            [
                ast.GreaterThan(
                    ast.Name(u'spam', Location(2, 4), Location(2, 8)),
                    ast.Integer(1, Location(2, 11), Location(2, 12)),
                    Location(2, 4),
                    Location(2, 12)
                )
            ],
            Location(1, 0),
            Location(2, 12)
        )
    ])),
    (u'foo\n    spam <= 1', ast.IgnoreFile('<test>', [
        ast.Filter(
            u'foo',
            [
                ast.LessOrEqualThan(
                    ast.Name(u'spam', Location(2, 4), Location(2, 8)),
                    ast.Integer(1, Location(2, 12), Location(2, 13)),
                    Location(2, 4),
                    Location(2, 13)
                )
            ],
            Location(1, 0),
            Location(2, 13)
        )
    ])),
    (u'foo\n    spam >= 1', ast.IgnoreFile('<test>', [
        ast.Filter(
            u'foo',
            [
                ast.GreaterOrEqualThan(
                    ast.Name(u'spam', Location(2, 4), Location(2, 8)),
                    ast.Integer(1, Location(2, 12), Location(2, 13)),
                    Location(2, 4),
                    Location(2, 13)
                )
            ],
            Location(1, 0),
            Location(2, 13)
        )
    ]))
])
def test_parser(source, ast):
    assert parse(lex(source), '<test>') == ast
