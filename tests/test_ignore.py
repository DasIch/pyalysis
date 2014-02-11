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
from pyalysis.ignore.verifier import verify, IgnoreVerificationWarning
from pyalysis.ignore.compiler import compile
from pyalysis.warnings import PrintStatement, DivStatement


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


@pytest.mark.parametrize(('source', 'filters', 'warnings'), [
    (u'pep8', [Filter(u'pep8', Location(1, 0), Location(1, 4))], []),
    (u'foo', [], [
        IgnoreVerificationWarning(
            u'Ignoring filter with unknown warning type: "foo" in line 1.'
        )
    ])
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
    (u'print-statement', DivStatement(u'message', '<test>', 1), True)
])
def test_compile(source, warning, allowed):
    assert compile(verify(parse(lex(source))))(warning) == allowed
