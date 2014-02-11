# coding: utf-8
"""
    pyalysis.formatters
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import json

from pyalysis.warnings import LineWarning, TokenWarning, ASTWarning
from pyalysis._compat import PYPY


class JSONFormatter(object):
    """
    Formats warnings as JSON objects, each warning will be represented as an
    individual JSON object, objects will be separated by newlines in the given
    file-like `output`.
    """
    def __init__(self, output):
        self.output = output

    def format(self, warning):
        """
        Formats a single `warning`.
        """
        result = {
            u'message': warning.message,
            u'lineno': warning.lineno,
            u'file': warning.file
        }
        if isinstance(warning, TokenWarning):
            result.update({
                u'start': warning.start,
                u'end': warning.end
            })
        self.dump(result)

    def dump(self, d):
        js = json.dumps(d, ensure_ascii=False, sort_keys=True, indent=4)
        if PYPY:
            # PyPy seems to have a bug that makes json.dumps produce bytes,
            # even if ensure_ascii=True is passed.
            js = js.decode('utf-8')
        self.output.write(js)
        self.output.write(u'\n')
