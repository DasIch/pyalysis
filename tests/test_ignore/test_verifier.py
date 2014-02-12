# coding: utf-8
"""
    tests.test_ignore.test_verifier
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import pytest

from pyalysis.ignore import ast
from pyalysis.ignore.tokens import Location
from pyalysis.ignore.lexer import lex
from pyalysis.ignore.parser import parse
from pyalysis.ignore.verifier import verify, IgnoreVerificationWarning
from pyalysis._compat import text_type


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


class TestVerifyGreaterThan(BinaryOperationVerifyTest):
    @pytest.fixture
    def operation(self):
        return u'>'

    @pytest.fixture
    def operation_name(self):
        return u'greater than'

    @pytest.fixture(params=[int])
    def supported_type(self, request):
        return request.param


class TestVerifyLessOrEqualThen(BinaryOperationVerifyTest):
    @pytest.fixture
    def operation(self):
        return u'<='

    @pytest.fixture
    def operation_name(self):
        return u'less or equal than'

    @pytest.fixture(params=[int])
    def supported_type(self, request):
        return request.param


class TestVerifyGreaterOrEqualThen(BinaryOperationVerifyTest):
    @pytest.fixture
    def operation(self):
        return u'>='

    @pytest.fixture
    def operation_name(self):
        return u'greater or equal than'

    @pytest.fixture(params=[int])
    def supported_type(self, request):
        return request.param
