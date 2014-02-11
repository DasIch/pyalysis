# coding: utf-8
"""
    pyalysis.ignore.tokens
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from collections import namedtuple


Location = namedtuple('Location', ['line', 'column'])
Token = namedtuple('Token', ['lexeme', 'start', 'end'])


class Name(Token):
    pass


class Newline(Token):
    pass
