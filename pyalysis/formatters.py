# coding: utf-8
"""
    pyalysis.formatters
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import json
import textwrap

from pyalysis.utils import count_digits
from pyalysis._compat import PYPY, text_type


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
            u'file': warning.file
        }
        for attribute in ['start', 'end', 'lineno']:
            if hasattr(warning, attribute):
                result.update({attribute: getattr(warning, attribute)})
        self.dump(result)

    def dump(self, d):
        js = json.dumps(d, ensure_ascii=False, sort_keys=True, indent=4)
        if PYPY:
            # PyPy seems to have a bug that makes json.dumps produce bytes,
            # even if ensure_ascii=True is passed.
            js = js.decode('utf-8')
        self.output.write(js)
        self.output.write(u'\n')


class TextFormatter(object):
    """
    Formats warnings as human readable text.
    """
    def __init__(self, output):
        self.output = output

    def format(self, warning):
        """
        Formats a single `warning`.
        """
        if hasattr(warning, 'start') and hasattr(warning, 'end'):
            if warning.start.line == warning.end.line:
                location = u'line {}'.format(warning.start.line)
            else:
                location = u'lines {}-{}'.format(
                    warning.start.line,
                    warning.end.line
                )
        else:
            location = u'line {}'.format(warning.lineno)
        if hasattr(warning, 'lines'):
            lines = warning.lines
            template = textwrap.dedent(u"""\
                File "{file}", {location}
                {lines}
                {message}

            """)
        else:
            lines = []
            template = textwrap.dedent(u"""\
                File "{file}", {location}
                {message}

            """)
        if len(lines) > 1:
            lineno_length = count_digits(warning.end.line)
            lines_with_lineno = []
            for lineno, line in enumerate(lines, warning.start.line):
                lines_with_lineno.append(
                    u'  {} {}'.format(
                        text_type(lineno).rjust(lineno_length),
                        line
                    )
                )
            lines = lines_with_lineno
        else:
            lines = [u' ' * 2 + line for line in lines]
        self.output.write(
            template.format(
                file=warning.file,
                location=location,
                lines=u'\n'.join(lines),
                message=textwrap.fill(warning.message)
            )
        )
