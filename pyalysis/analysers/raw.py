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
from pyalysis.analysers.base import AnalyserBase


class LineAnalyser(AnalyserBase):
    """
    Line-level analyser of Python source code.
    """

    #: :class:`blinker.Signal` instance that will be emitted for each line in
    #: the module with the line number (`lineno`) and `line` as argument.
    on_line = Signal()

    def __init__(self, module):
        AnalyserBase.__init__(self, module)

        self.encoding = detect_encoding(module)

    def emit(self, warning_cls, message):
        start = Location(self.lineno, 0)
        end = Location(self.lineno, len(self.line))
        AnalyserBase.emit(self, warning_cls, message, start, end)

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
