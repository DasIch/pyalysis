# coding: utf-8
"""
    pyalysis.formatters
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import json

from pyalysis.warnings import TokenWarning
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
        if isinstance(warning, TokenWarning):
            self.format_token_warning(warning)
        else:
            raise NotImplementedError(warning)

    def format_token_warning(self, warning):
        js = json.dumps(
            {
                u'message': warning.message,
                u'start': warning.start,
                u'end': warning.end,
                u'file': warning.file
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=4
        )
        if PYPY:
            # PyPy seems to have a bug that makes json.dumps produce bytes,
            # even if ensure_ascii=True is passed.
            js = js.decode('utf-8')
        self.output.write(js)
        self.output.write(u'\n')
