# coding: utf-8
"""
    tests.test_ignore.test_verifier
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from io import StringIO

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
        attributes = {
            text_type: u'message'
        }
        if supported_type in attributes:
            return attributes[supported_type]
        pytest.skip('no fixture')

    @pytest.fixture
    def type_name(self, supported_type):
        for (type, _, type_name) in self._types:
            if issubclass(type, supported_type):
                return type_name

    @pytest.fixture(params=range((len(_types) - 1) or 1))
    def unsupported_literal(self, request, supported_type):
        types = self._types[request.param:] + self._types[:request.param]
        for (type, literal, _) in types:
            if not issubclass(type, supported_type):
                return literal
        pytest.skip('no fixture')

    @pytest.fixture(params=range((len(_types) - 1) or 1))
    def unsupported_type_name(self, request, supported_type):
        types = self._types[request.param:] + self._types[:request.param]
        for (type, _, type_name) in types:
            if not issubclass(type, supported_type):
                return type_name
        pytest.skip('no fixture')

    def assert_verify(self, source, expected_filters, expected_warnings):
        file = StringIO(source)
        file.name = '<test>'
        filters, warnings = verify(file, parse(lex(file.read())))
        assert filters == expected_filters
        assert warnings == expected_warnings

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
            u'Ignoring filter with unknown warning type "foo".',
            '<test>',
            Location(1, 0),
            Location(1, 3),
            [u'foo']
        )])
    ])
    def test(self, type, passes, warnings):
        filters = [
            ast.Filter(type, [], Location(1, 0), Location(1, len(type)))
        ]
        self.assert_verify(type, filters if passes else [], warnings)


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
        self.assert_verify(source, filters, [
            IgnoreVerificationWarning(
                u'Ignoring {} expression with missing constant.'
                .format(operation_name),
                '<test>',
                Location(2, 1),
                Location(2, 9 + len(operation)),
                [u' foo {} bar'.format(operation)]
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
        self.assert_verify(source, filters, [
            IgnoreVerificationWarning(
                u'Ignoring {} expression with missing name.'
                .format(operation_name),
                '<test>',
                Location(2, 1),
                Location(2, 13 + len(operation)),
                [u' "foo" {} "bar"'.format(operation)]
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
        self.assert_verify(source, filters, [
            IgnoreVerificationWarning(
                (
                    u'Ignoring {} expression with "foo". "star-import" '
                    u'doesn\'t have such an attribute to compare to.'
                ).format(operation_name),
                '<test>',
                Location(2, 1),
                Location(2, 11 + len(operation)),
                [u' foo {} "bar"'.format(operation)]
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
        self.assert_verify(source, filters, [
            IgnoreVerificationWarning(
                u'Ignoring {} expression. "{}" is not of type {}.'
                    .format(operation_name, attribute, unsupported_type_name),
                '<test>',
                Location(2, 1),
                filters[0].end,
                [source.splitlines()[1]]
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
