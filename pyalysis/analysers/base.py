# coding: utf-8
"""
    pyalysis.analysers.base
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import absolute_import
import tokenize

from blinker import Signal

from pyalysis.utils import PerClassAttribute, retain_file_position
from pyalysis._compat import PY2


class AnalyserBase(object):
    #: :class:`blinker.Signal` instance that will be called by :meth:`analyse`,
    #: with the :class:`AnalyserBase` instance as sender.
    on_analyse = PerClassAttribute(Signal)

    def __init__(self, module):
        #: The module being analysed as a file-like object opened in read-only
        #: bytes mode.
        self.module = module

        #: A list with the lines in the module.
        with retain_file_position(self.module):
            self.physical_lines = [line.rstrip() for line in self.module]

        with retain_file_position(self.module):
            #: A list with the logical lines in the module.
            self.logical_lines = []
            self.logical_line_linenos = []
            self._index2logical_line_index = []
            for logical_line_index, (start, end, line) in enumerate(
                get_logical_lines(self.module)
            ):
                for _ in range(end - start + 1):
                    self._index2logical_line_index.append(logical_line_index)
                self.logical_line_linenos.append((start, end))
                self.logical_lines.append(line)

        #: A list of warnings generated by the analyser.
        self.warnings = []

    def get_logical_lines(self, start, end):
        """
        Returns an iterator of the logical lines between the given `start` and
        `end` location.
        """
        if start.line == end.line:
            logical_line_indices = [
                self._index2logical_line_index[start.line - 1]
            ]
        else:
            logical_line_indices = sorted({
                self._index2logical_line_index[lineno - 1]
                for lineno in range(start.line, end.line)
            })
        for index in logical_line_indices:
            yield self.logical_lines[index]

    def get_logical_line_range(self, lineno):
        """
        Returns a tuple containing the first and last line number of the
        logical line in which the given `lineno` is contained.
        """
        logical_line_index = self._index2logical_line_index[lineno - 1]
        return self.logical_line_linenos[logical_line_index]

    def emit(self, warning_cls, message, start, end):
        """
        Adds an instance of `warning_cls` to :attr:`warnings`.

        `warning_cls` will be called with the warning `message`, the name of
        the module in which the warning occurred, the `start` and `end`
        location of the code being warned about and a list of logical lines
        corresponding to the given locations.
        """
        self.warnings.append(
            warning_cls(
                message, self.module.name, start, end,
                list(self.get_logical_lines(start, end))
            )
        )

    def analyse(self):
        """
        Analyses the module and returns :attr:`warnings` for convenience.
        """
        return self.warnings


def get_logical_lines(file):
    if PY2:
        generate_tokens = tokenize.generate_tokens
    else:
        generate_tokens = tokenize.tokenize
    seen = 0
    for _, _, start, end, logical_line in generate_tokens(file.readline):
        if start[0] > seen:
            yield start[0], end[0], logical_line.rstrip()
            seen = end[0]
