# coding: utf-8
"""
    pyalysis.application
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst
"""
import sys
import codecs

from pyalysis.analysers import (
    LineAnalyser, TokenAnalyser, CSTAnalyser, ASTAnalyser
)
from pyalysis.formatters import TextFormatter
from pyalysis.ignore import load_ignore_filter
from pyalysis._compat import stdout


class Pyalysis(object):
    def __init__(self):
        self.analyser_classes = [
            LineAnalyser, TokenAnalyser, CSTAnalyser, ASTAnalyser
        ]
        self.formatter_class = TextFormatter
        self.ignore_file_path = '.pyalysis.ignore'
        self.output = stdout
        self.warned = False

        self._should_emit = None

    @property
    def should_emit(self):
        if self._should_emit is None:
            try:
                with codecs.open(self.ignore_file_path,
                                 'r',
                                 encoding='utf-8') as ignore_file:
                    self._should_emit = load_ignore_filter(ignore_file)
            except IOError:
                self._should_emit = lambda _: True
        return self._should_emit

    def analyse_file(self, file_path):
        formatter = self.formatter_class(self.output)
        with open(file_path, 'rb') as file:
            for analyser_class in self.analyser_classes:
                analyser = analyser_class(file)
                for warning in filter(self.should_emit, analyser.analyse()):
                    self.warned = True
                    formatter.format(warning)
                file.seek(0)

    def analyse(self, files):
        for file in files:
            self.analyse_file(file)
        if self.warned:
            sys.exit(1)
