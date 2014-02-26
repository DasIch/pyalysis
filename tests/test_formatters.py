# coding: utf-8
"""
    tests.test_formatters
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from io import StringIO

from pyalysis.formatters import JSONFormatter, TextFormatter
from pyalysis.warnings import TokenWarning, ASTWarning, CSTWarning
from pyalysis.ignore.verifier import IgnoreVerificationWarning
from pyalysis.analysers.token import Location


class TestJSONFormatter(object):
    def test_token_warning(self):
        output = StringIO()
        formatter = JSONFormatter(output)
        formatter.format(
            TokenWarning(
                u'a message', '<test>', Location(1, 0), Location(1, 10),
                [u'0123456789']
            )
        )
        formatter.format(
            TokenWarning(
                u'b message', '<test>', Location(2, 0), Location(2, 20),
                [u'01234567890123456789']
            )
        )
        formatter.format(
            TokenWarning(
                u'c message', '<test>', Location(2, 0), Location(3, 20),
                [u'01234567890123456789']
            )
        )
        assert output.getvalue() == textwrap.dedent(u"""\
        {
            "end": [
                1, 
                10
            ], 
            "file": "<test>", 
            "message": "a message", 
            "start": [
                1, 
                0
            ]
        }
        {
            "end": [
                2, 
                20
            ], 
            "file": "<test>", 
            "message": "b message", 
            "start": [
                2, 
                0
            ]
        }
        {
            "end": [
                3, 
                20
            ], 
            "file": "<test>", 
            "message": "c message", 
            "start": [
                2, 
                0
            ]
        }
        """)

    def test_ast_warning(self):
        output = StringIO()
        formatter = JSONFormatter(output)
        formatter.format(
            ASTWarning(
                u'a message', '<test>', Location(1, 0), Location(1, 10),
                [u'0123456789']
            )
        )
        formatter.format(
            ASTWarning(
                u'b message', '<test>', Location(2, 0), Location(2, 10),
                [u'0123456789']
            )
        )
        assert output.getvalue() == textwrap.dedent(u"""\
        {
            "end": [
                1, 
                10
            ], 
            "file": "<test>", 
            "message": "a message", 
            "start": [
                1, 
                0
            ]
        }
        {
            "end": [
                2, 
                10
            ], 
            "file": "<test>", 
            "message": "b message", 
            "start": [
                2, 
                0
            ]
        }
        """)

    def test_cst_warning(self):
        output = StringIO()
        formatter = JSONFormatter(output)
        formatter.format(
            CSTWarning(
                u'a message', '<test>', Location(1, 0), Location(1, 10),
                [u'0123456789']
            )
        )
        formatter.format(
            CSTWarning(
                u'b message', '<test>', Location(2, 0), Location(2, 10),
                [u'0123456789']
            )
        )
        assert output.getvalue() == textwrap.dedent(u"""\
        {
            "end": [
                1, 
                10
            ], 
            "file": "<test>", 
            "message": "a message", 
            "start": [
                1, 
                0
            ]
        }
        {
            "end": [
                2, 
                10
            ], 
            "file": "<test>", 
            "message": "b message", 
            "start": [
                2, 
                0
            ]
        }
        """)


class TestTextFormatter(object):
    def test_token_warning(self):
        output = StringIO()
        formatter = TextFormatter(output)
        formatter.format(
            TokenWarning(
                u'a message', '<test>', Location(1, 0), Location(1, 10),
                [u'0123456789']
            )
        )
        formatter.format(
            TokenWarning(
                u'b message', '<test>', Location(2, 0), Location(2, 20),
                [u'01234567890123456789']
            )
        )
        formatter.format(
            TokenWarning(
                u'c message', '<test>', Location(2, 0), Location(3, 20),
                [u'01234567890123456789', u'01234567890123456789']
            )
        )
        assert output.getvalue() == textwrap.dedent(u"""\
        File "<test>", line 1
          0123456789
        a message

        File "<test>", line 2
          01234567890123456789
        b message

        File "<test>", lines 2-3
          2 01234567890123456789
          3 01234567890123456789
        c message

        """)

    def test_ast_warning(self):
        output = StringIO()
        formatter = TextFormatter(output)
        formatter.format(
            ASTWarning(
                u'a message', '<test>', Location(1, 0), Location(1, 10),
                [u'0123456789']
            )
        )
        formatter.format(
            ASTWarning(
                u'b message', '<test>', Location(2, 0), Location(2, 10),
                [u'0123456789']
            )
        )
        assert output.getvalue() == textwrap.dedent(u"""\
        File "<test>", line 1
          0123456789
        a message

        File "<test>", line 2
          0123456789
        b message

        """)

    def test_cst_warning(self):
        output = StringIO()
        formatter = TextFormatter(output)
        formatter.format(
            CSTWarning(
                u'a message', '<test>', Location(1, 0), Location(1, 10),
                [u'0123456789']
            )
        )
        formatter.format(
            CSTWarning(
                u'b message', '<test>', Location(2, 0), Location(2, 10),
                [u'0123456789']
            )
        )
        assert output.getvalue() == textwrap.dedent(u"""\
        File "<test>", line 1
          0123456789
        a message

        File "<test>", line 2
          0123456789
        b message

        """)

    def test_ignore_verification_warning(self):
        output = StringIO()
        formatter = TextFormatter(output)
        formatter.format(
            IgnoreVerificationWarning(
                u'a message',
                '<test>',
                Location(1, 0),
                Location(1, 10),
                [u'abcdefghij']
            )
        )
        formatter.format(
            IgnoreVerificationWarning(
                u'b message',
                '<test>',
                Location(2, 0),
                Location(2, 10),
                [u'klmnopqrst']
            )
        )
        formatter.format(
            IgnoreVerificationWarning(
                u'c message',
                '<test>',
                Location(3, 0),
                Location(4, 4),
                [u'spam', u'eggs']
            )
        )
        assert output.getvalue() == textwrap.dedent(u"""\
            File "<test>", line 1
              abcdefghij
            a message

            File "<test>", line 2
              klmnopqrst
            b message

            File "<test>", lines 3-4
              3 spam
              4 eggs
            c message

        """)
