# coding: utf-8
"""
    pyalysis.analysers.raw
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import codecs

from blinker import Signal

from pyalysis.utils import detect_encoding, Location
from pyalysis.warnings import LineTooLong


class LineAnalyser(object):
    """
    Line-level analyser of Python source code.
    """
    on_analyse = Signal()
    on_line = Signal()

    def __init__(self, module):
        self.module = module

        self.encoding = detect_encoding(module)
        self.warnings = []

    def emit(self, warning_cls, message):
        self.warnings.append(
            warning_cls(
                message, self.module.name,
                Location(self.lineno, 0),
                Location(self.lineno, len(self.line))
            )
        )

    def analyse(self):
        self.on_analyse.send(self)
        reader = codecs.lookup(self.encoding).streamreader(self.module)
        for i, line in enumerate(reader, 1):
            self.lineno = i
            self.line = line
            self.on_line.send(self, lineno=i, line=line)
        return self.warnings


@LineAnalyser.on_line.connect
def check_line_length(analyser, lineno, line):
    if len(line.rstrip()) > 79:
        analyser.emit(
            LineTooLong,
            u'Line is longer than 79 characters. '
            u'You should keep it below that',
        )
