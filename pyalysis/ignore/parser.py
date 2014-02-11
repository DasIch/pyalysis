# coding: utf-8
"""
    pyalysis.ignore.parser
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from pyalysis.ignore.tokens import Name, Newline
from pyalysis.ignore.ast import IgnoreFile, Filter


def parse(tokens, filename='<unknown>'):
    return IgnoreFile(filename, list(parse_filters(tokens)))


def parse_filters(tokens):
    while True:
        yield parse_filter(tokens)


def parse_filter(tokens):
    name = expect(Name, tokens)
    try:
        end = expect(Newline, tokens).end
    except StopIteration:
        end = name.end
    return Filter(name.lexeme, name.start, end)


class ParsingError(Exception):
    pass


def expect(token_cls, tokens):
    token = next(tokens)
    if isinstance(token, token_cls):
        return token
    raise ParsingError(
        u'got an unexpected token {} at line {}, column {}'.format(
            token.__class__.__name, token.start.line, token.start.column
        )
    )
