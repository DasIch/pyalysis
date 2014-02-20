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
    """
    Represents a token of some type.

    Takes the `lexeme` described by the token, the `start` and `end` location
    within the source.
    """
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
    """
    Represents a name.
    """


class Newline(Token):
    """
    Represents a newline.
    """


class Indent(Token):
    """
    Represents an added level of indentation.
    """


class Dedent(Token):
    """
    Represents a removed level of indentation.
    """


class Operator(Token):
    """
    Represents an operator.
    """


class String(Token):
    """
    Represents a string.
    """


class Integer(Token):
    """
    Represents an integer.
    """
