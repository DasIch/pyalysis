# coding: utf-8
"""
    pyalysis.ignore.lexer
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import re
from collections import deque

from pyalysis.ignore.tokens import (
    Location, Name, Newline, Indent, Dedent, Operator, String
)
from pyalysis._compat import implements_iterator


indentation_re = re.compile(r'\s+')


TOKEN_DEFINITIONS = [
    (re.compile(regex), token_cls) for regex, token_cls in [
        (r'[a-zA-Z][a-zA-Z0-9\-]*', Name),
        (r'\n', Newline),
        (r'=', Operator),
        (r'"[^"]*"', String)
    ]
]


IGNORE_DEFINITIONS = list(map(re.compile, [r'\s']))


class LexingError(Exception):
    pass


@implements_iterator
class TokenStream(object):
    def __init__(self, iterator):
        self.iterator = iterator

        self._remaining = deque()

    def __iter__(self):
        return self

    def __next__(self):
        if self._remaining:
            return self._remaining.popleft()
        return next(self.iterator)

    def lookahead(self, n=1):
        while len(self._remaining) < n:
            self._remaining.append(next(self))
        return [self._remaining[i] for i in range(n)]


def lex(source):
    return TokenStream(_lex(source))


def _lex(source):
    indentation_stack = []
    for lineno, line in enumerate(source.splitlines(True), 1):
        column = 0
        token, lineno, column = lex_indentation(
            lineno, column, line, indentation_stack
        )
        if token:
            yield token
        for token in lex_line_content(lineno, column, line):
            yield token
        column = token.end.column
    for _ in indentation_stack:
        yield Dedent(u'', Location(lineno, column), Location(lineno, column))


def lex_indentation(lineno, column, line, indentation_stack):
    match = indentation_re.match(line)
    if match is None:
        return (None, lineno, column)
    lexeme = match.group(0)
    column += len(lexeme)
    if len(lexeme) > sum(indentation_stack):
        indentation_stack.append(len(lexeme) - sum(indentation_stack))
        token = Indent(
            lexeme, Location(lineno, 0), Location(lineno, column)
        )
    elif len(lexeme) < sum(indentation_stack):
        last_added = indentation_stack.pop()
        if len(lexeme) - sum(indentation_stack) != last_added:
            raise LexingError(
                (
                    u'unindent does not match outer indentation level '
                    u'in line {}'
                ).format(lineno)
            )
        token = Dedent(
            lexeme, Location(lineno, 0), Location(lineno, column)
        )
    else:
        token = None
    return token, lineno, column


def lex_line_content(lineno, column, line):
    while line[column:]:
        for regex, token_cls in TOKEN_DEFINITIONS:
            match = regex.match(line[column:])
            if match is not None:
                break
        if match is None:
            for regex in IGNORE_DEFINITIONS:
                match = regex.match(line[column:])
                if match is not None:
                    break
            if match is None:
                raise LexingError(
                    u'cannot find matching token at line {}, column {}'.format(
                        lineno, column
                    )
                )
            else:
                column += match.end()
        else:
            lexeme = match.group(0)
            start = Location(lineno, column)
            if u'\n' in lexeme:
                lineno += lexeme.count(u'\n')
                column = 0
            else:
                column += match.end()
            end = Location(lineno, column)
            yield token_cls(lexeme, start, end)
            if column == 0:
                break
