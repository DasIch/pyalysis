# coding: utf-8
"""
    pyalysis.analysers.raw
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import codecs

from pyalysis.utils import detect_encoding
from pyalysis.warnings import LineTooLong


class LineAnalyser(object):
    """
    Line-level analyser of Python source code.
    """
    def __init__(self, module):
        self.module = module

        self.encoding = detect_encoding(module)
        self.warnings = []

    def emit(self, warning_cls, message, lineno):
        self.warnings.append(warning_cls(message, self.module.name, lineno))

    def analyse(self):
        reader = codecs.lookup(self.encoding).streamreader(self.module)
        for i, line in enumerate(reader, 1):
            self.analyse_line(i, line)
        return self.warnings

    def analyse_line(self, lineno, line):
        if len(line.rstrip()) > 79:
            self.emit(
                LineTooLong,
                u'Line is longer than 79 characters. '
                u'You should keep it below that',
                lineno
            )
