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
from pyalysis._compat import text_type


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
    ]),
    (u'foo\n    spam < 1', [
        tokens.Name(u'foo', Location(1, 0), Location(1, 3)),
        tokens.Newline(u'\n', Location(1, 3), Location(2, 0)),
        tokens.Indent(u'    ', Location(2, 0), Location(2, 4)),
        tokens.Name(u'spam', Location(2, 4), Location(2, 8)),
        tokens.Operator(u'<', Location(2, 9), Location(2, 10)),
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
    ])),
    (u'foo\n    spam < 1', ast.IgnoreFile('<test>', [
        ast.Filter(
            u'foo',
            [
                ast.LessThan(
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


class VerifyTest(object):
    _types = [
        (text_type, u'"foo"', u'string'),
        (int, u'1', u'integer')
    ]

    @pytest.fixture
    def attribute(self, supported_type):
        return {
            text_type: u'message',
            int: u'lineno'
        }[supported_type]

    @pytest.fixture
    def type_name(self, supported_type):
        for (type, _, type_name) in self._types:
            if issubclass(type, supported_type):
                return type_name

    @pytest.fixture(params=range(len(_types) - 1))
    def unsupported_literal(self, request, supported_type):
        types = self._types[request.param:] + self._types[:request.param]
        for (type, literal, _) in types:
            if not issubclass(type, supported_type):
                return literal

    @pytest.fixture(params=range(len(_types) - 1))
    def unsupported_type_name(self, request, supported_type):
        types = self._types[request.param:] + self._types[:request.param]
        for (type, _, type_name) in types:
            if not issubclass(type, supported_type):
                return type_name

    def assert_verify(self, source, filters):
        assert list(verify(parse(lex(source)))) == filters

    def assert_warnings(self, recwarn, warnings):
        if warnings:
            for warning in warnings:
                received_warning = recwarn.pop()
                assert isinstance(warning, received_warning.category)
                assert received_warning.message.args == warning.args
        else:
            with pytest.raises(AssertionError):
                recwarn.pop()


class TestVerifyType(VerifyTest):
    @pytest.mark.parametrize(('type', 'passes', 'warnings'), [
        (u'pep8', True, []),
        (u'foo', False, [IgnoreVerificationWarning(
            u'Ignoring filter with unknown warning type: "foo" in line 1.'
        )])
    ])
    def test(self, type, passes, warnings, recwarn):
        filters = [
            ast.Filter(type, [], Location(1, 0), Location(1, len(type)))
        ]
        self.assert_verify(type, filters if passes else [])
        self.assert_warnings(recwarn, warnings)


class BinaryOperationVerifyTest(VerifyTest):
    def test_name_and_literal(self, operation, operation_name, recwarn):
        source = u'star-import\n foo {} bar'.format(operation)
        filters = [
            ast.Filter(
                u'star-import',
                [],
                Location(1, 0),
                Location(2, 9 + len(operation))
            )
        ]
        self.assert_verify(source, filters)
        self.assert_warnings(recwarn, [
            IgnoreVerificationWarning(
                u'Ignoring {} expression with missing constant in line 2.' \
                    .format(operation_name)
            )
        ])

        source = u'star-import\n "foo" {} "bar"'.format(operation)
        filters = [
            ast.Filter(
                u'star-import',
                [],
                Location(1, 0),
                Location(2, 13 + len(operation))
            )
        ]
        self.assert_verify(source, filters)
        self.assert_warnings(recwarn, [
            IgnoreVerificationWarning(
                u'Ignoring {} expression with missing name in line 2.' \
                    .format(operation_name)
            )
        ])

    def test_missing_attribute(self, operation, operation_name, recwarn):
        source = u'star-import\n foo {} "bar"'.format(operation)
        filters = [
            ast.Filter(
                u'star-import',
                [],
                Location(1, 0),
                Location(2, 11 + len(operation))
            )
        ]
        self.assert_verify(source, filters)
        self.assert_warnings(recwarn, [
            IgnoreVerificationWarning(
                (
                    u'Ignoring {} expression with "foo". "star-import" '
                    u'doesn\'t have such an attribute to compare to. Line 2.'
                ).format(operation_name)
            )
        ])

    def test_typing(self, attribute, operation, unsupported_literal,
                    operation_name, unsupported_type_name, recwarn):
        source = u'star-import\n {} {} {}'.format(
            attribute, operation, unsupported_literal
        )
        filters = [
            ast.Filter(
                u'star-import',
                [],
                Location(1, 0),
                Location(2, 3 + sum(map(len, [attribute, operation,
                                              unsupported_literal]))))
        ]
        self.assert_verify(source, filters)
        self.assert_warnings(recwarn, [
            IgnoreVerificationWarning(
                (
                    u'Ignoring {} expression in line 2. "{}" is not of '
                    u'type {}.'
                ).format(operation_name, attribute, unsupported_type_name)
            )
        ])


class TestVerifyEqual(BinaryOperationVerifyTest):
    @pytest.fixture
    def operation(self):
        return u'='

    @pytest.fixture
    def operation_name(self):
        return u'equal'

    @pytest.fixture(params=[text_type, int])
    def supported_type(self, request):
        return request.param


class TestVerifyLessThan(BinaryOperationVerifyTest):
    @pytest.fixture
    def operation(self):
        return u'<'

    @pytest.fixture
    def operation_name(self):
        return u'less than'

    @pytest.fixture(params=[int])
    def supported_type(self, request):
        return request.param



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
    ),
    (
        u'print-statement \n lineno < 3',
        PrintStatement(u'foo', '<test>', 1),
        False
    ),
    (
        u'print-statement \n lineno < 3',
        PrintStatement(u'foo', '<test>', 2),
        False
    ),
    (
        u'print-statement \n lineno < 3',
        PrintStatement(u'foo', '<test>', 3),
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
