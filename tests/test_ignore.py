# coding: utf-8
"""
    tests.test_ignore
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import pytest

from pyalysis.ignore.lexer import lex
from pyalysis.ignore.tokens import Name, Location


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
