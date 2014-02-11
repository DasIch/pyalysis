# coding: utf-8
"""
    pyalysis.ignore.lexer
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import re

from pyalysis.ignore.tokens import Location, Name, Newline


TOKEN_DEFINITIONS = [
    (re.compile(regex), token_cls) for regex, token_cls in [
        (r'[a-zA-Z][a-zA-Z\-]*', Name),
        (r'\n', Newline)
    ]
]


IGNORE_DEFINITIONS = []


class LexingError(Exception):
    pass


def lex(source):
    line = 1
    column = 0
    offset = 0

    def update_location(lexeme):
        if u'\n' in lexeme:
            return (
                line + lexeme.count(u'\n'),
                len(lexeme.rsplit(u'\n', 1)[1])
            )
        else:
            return (line, column + len(lexeme))

    while source[offset:]:
        for regex, token_cls in TOKEN_DEFINITIONS:
            match = regex.match(source[offset:])
            if match is not None:
                break
        if match is None:
            for regex in IGNORE_DEFINITIONS:
                match = regex.match(source[offset:])
                if match is not None:
                    break
            if match is None:
                raise LexingError(
                    u'cannot find matching token at line {}, column {}'.format(
                        line, column
                    )
                )
            else:
                offset += match.end()
                line, column = update_location(match.group(0))
        else:
            offset += match.end()
            lexeme = match.group(0)
            start = Location(line, column)
            line, column = update_location(lexeme)
            end = Location(line, column)
            yield token_cls(lexeme, start, end)
