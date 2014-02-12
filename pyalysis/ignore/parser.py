# coding: utf-8
"""
    pyalysis.ignore.parser
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from pyalysis.ignore import tokens, ast


def parse(tokens, filename='<unknown>'):
    return ast.IgnoreFile(filename, list(parse_filters(tokens)))


def parse_filters(tokens):
    while True:
        yield parse_filter(tokens)


def parse_filter(token_stream):
    name = expect(tokens.Name, token_stream)
    try:
        end = expect(tokens.Newline, token_stream).start
    except StopIteration:
        end = name.end
    try:
        expressions, dedent_end = parse_expressions(token_stream)
    except StopIteration:
        expressions = []
    else:
        if dedent_end:
            end = dedent_end
    return ast.Filter(name.lexeme, expressions, name.start, end)


def parse_expressions(token_stream):
    if isinstance(token_stream.lookahead()[0], tokens.Indent):
        next(token_stream)
        expressions = []
        while not isinstance(token_stream.lookahead()[0], tokens.Dedent):
            expressions.append(parse_expression(token_stream))
        end = expect(tokens.Dedent, token_stream).end
        return expressions, end
    return [], None


def parse_expression(token_stream):
    left = parse_literal(token_stream)
    operator = expect(tokens.Operator, token_stream)
    right = parse_literal(token_stream)
    try:
        final_token = token_stream.lookahead()[0]
    except StopIteration:
        pass
    else:
        if isinstance(final_token, tokens.Newline):
            next(token_stream)
        else:
            if not isinstance(final_token, tokens.Dedent):
                raise ParsingError(
                    (
                        u'expected newline or dedent, got {} at line {}, '
                        u'column {}'
                    ).format(
                        token.__class__.__name__,
                        token.start.line,
                        token.start.column
                    )
                )
    return {
        u'=': ast.Equal,
        u'<': ast.LessThan
    }[operator.lexeme](left, right, left.start, right.end)


def parse_literal(token_stream):
    token = next(token_stream)
    if isinstance(token, tokens.Name):
        return ast.Name(token.lexeme, token.start, token.end)
    elif isinstance(token, tokens.String):
        return ast.String(token.lexeme[1:-1], token.start, token.end)
    elif isinstance(token, tokens.Integer):
        return ast.Integer(int(token.lexeme), token.start, token.end)
    else:
        raise ParsingError(
            u'got an unexpected token {} at line {}, column {}'.format(
                token, token.start.line, token.start.column
            )
        )


class ParsingError(Exception):
    pass


def expect(token_cls, tokens):
    token = next(tokens)
    if isinstance(token, token_cls):
        return token
    raise ParsingError(
        u'got an unexpected token {} at line {}, column {}'.format(
            token.__class__.__name__, token.start.line, token.start.column
        )
    )
