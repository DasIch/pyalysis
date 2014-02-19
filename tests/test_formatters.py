# coding: utf-8
"""
    tests.test_formatters
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from io import StringIO

from pyalysis.formatters import JSONFormatter
from pyalysis.warnings import TokenWarning, ASTWarning


class TestJSONFormatter(object):
    def test_token_warning(self):
        output = StringIO()
        formatter = JSONFormatter(output)
        formatter.format(TokenWarning(u'a message', '<test>', (1, 0), (1, 10)))
        formatter.format(TokenWarning(u'b message', '<test>', (2, 0), (2, 20)))
        assert output.getvalue() == textwrap.dedent(u"""\
        {
            "end": [
                1, 
                10
            ], 
            "file": "<test>", 
            "lineno": 1, 
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
            "lineno": 2, 
            "message": "b message", 
            "start": [
                2, 
                0
            ]
        }
        """)

    def test_ast_warning(self):
        output = StringIO()
        formatter = JSONFormatter(output)
        formatter.format(ASTWarning(u'a message', '<test>', 1))
        formatter.format(ASTWarning(u'b message', '<test>', 2))
        print output.getvalue()
        assert output.getvalue() == textwrap.dedent(u"""\
        {
            "file": "<test>", 
            "lineno": 1, 
            "message": "a message"
        }
        {
            "file": "<test>", 
            "lineno": 2, 
            "message": "b message"
        }
        """)
