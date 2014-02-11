# coding: utf-8
"""
    pyalysis.ignore.tokens
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from collections import namedtuple


Location = namedtuple('Location', ['line', 'column'])
TokenBase = namedtuple('TokenBase', ['lexeme', 'start', 'end'])


class Token(TokenBase):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return TokenBase.__eq__(self, other)
        elif isinstance(other, Token):
            return False
        raise TypeError(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return (
            self.__class__.__name__ +
            TokenBase.__repr__(self).lstrip('TokenBase')
        )



class Name(Token):
    pass


class Newline(Token):
    pass
