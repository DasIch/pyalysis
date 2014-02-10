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
from pyalysis.warnings import TokenWarning


class TestJSONFormatter(object):
    def test_token_warning(self):
        output = StringIO()
        formatter = JSONFormatter(output)
        formatter.format(TokenWarning(u'a message', (1, 0), (1, 10), '<test>'))
        formatter.format(TokenWarning(u'b message', (2, 0), (2, 20), '<test>'))
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
        """)
