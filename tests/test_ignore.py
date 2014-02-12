# coding: utf-8
"""
    tests.test_ignore
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from io import StringIO

import pytest

from pyalysis.ignore import load_ignore_filter, tokens, ast
from pyalysis.ignore.tokens import Location
from pyalysis.ignore.lexer import lex
from pyalysis.ignore.parser import parse
from pyalysis.ignore.verifier import verify, IgnoreVerificationWarning
from pyalysis.ignore.compiler import compile
from pyalysis.warnings import PrintStatement, DivStatement


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
    ])
])
def test_lexer(source, tokens):
    assert list(lex(source)) == tokens


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
    ]))
])
def test_parser(source, ast):
    assert parse(lex(source), '<test>') == ast


@pytest.mark.parametrize(('source', 'filters', 'warnings'), [
    (u'pep8', [ast.Filter(u'pep8', [], Location(1, 0), Location(1, 4))], []),
    (u'foo', [], [
        IgnoreVerificationWarning(
            u'Ignoring filter with unknown warning type: "foo" in line 1.'
        )
    ]),
    (
        u'star-import\n foo = bar',
        [ast.Filter(u'star-import', [], Location(1, 0), Location(2, 10))],
        [
            IgnoreVerificationWarning(
                u'Ignoring equal expression with missing constant in line 2.'
            )
        ]
    ),
    (
        u'star-import\n "foo" = "bar"',
        [ast.Filter(u'star-import', [], Location(1, 0), Location(2, 14))],
        [
            IgnoreVerificationWarning(
                u'Ignoring equal expression with missing name in line 2.'
            )
        ]
    ),
    (
        u'star-import\n foo = "bar"',
        [ast.Filter(u'star-import', [], Location(1, 0), Location(2, 12))],
        [
            IgnoreVerificationWarning(
                u'Ignoring equal expression with "foo". "star-import" '
                u'doesn\'t have such an attribute to compare to. Line 2.'
            )
        ]
    ),
    (
        u'star-import\n lineno = "bar"',
        [ast.Filter(u'star-import', [], Location(1, 0), Location(2, 15))],
        [
            IgnoreVerificationWarning(
                u'Ignoring equal expression in line 2. "lineno" is not of '
                u'type string.'
            )
        ]
    ),
    (
        u'star-import\n message = 1',
        [ast.Filter(u'star-import', [], Location(1, 0), Location(2, 12))],
        [
            IgnoreVerificationWarning(
                u'Ignoring equal expression in line 2. "message" is not of '
                u'type integer.'
            )
        ]
    )
])
def test_verify(source, filters, warnings, recwarn):
    assert list(verify(parse(lex(source)))) == filters
    if warnings:
        for warning in warnings:
            received_warning = recwarn.pop()
            assert isinstance(warning, received_warning.category)
            assert received_warning.message.args == warning.args
    else:
        with pytest.raises(AssertionError):
            recwarn.pop()


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
    )
])
def test_compile(source, warning, allowed):
    assert compile(verify(parse(lex(source))))(warning) == allowed


@pytest.mark.parametrize(('source', 'warning', 'allowed'), [
    (u'print-statement', PrintStatement(u'message', '<test>', 1), False),
    (u'print-statement', DivStatement(u'message', '<test>', 1), True)
])
def test_load_ignore_filer(source, warning, allowed):
    file = StringIO(source)
    file.name = '<test>'
    assert load_ignore_filter(file)(warning) == allowed
