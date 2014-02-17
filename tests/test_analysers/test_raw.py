# coding: utf-8
"""
    tests.test_analysers.test_raw
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from io import BytesIO

from pyalysis.analysers import LineAnalyser


class LineAnalyserTest(object):
    def analyse_source(self, source):
        module = BytesIO(
            textwrap.dedent(source).encode('utf-8')
        )
        module.name = '<test>'
        analyser = LineAnalyser(module)
        return analyser.analyse()


class TestLineLength(LineAnalyserTest):
    def test(self):
        source = u'a' * 80
        warnings = self.analyse_source(source)
        assert len(warnings) == 1

        source = u'a' * 79 + u'\n'
        warnings = self.analyse_source(source)
        assert not warnings

