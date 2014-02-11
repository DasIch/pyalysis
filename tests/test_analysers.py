# coding: utf-8
"""
    tests.test_analysers
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from io import BytesIO

from pyalysis.analysers import LineAnalyser, TokenAnalyser, ASTAnalyser
from pyalysis.warnings import (
    WrongNumberOfIndentationSpaces, MixedTabsAndSpaces, MultipleImports,
    StarImport
)


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


class TokenAnalyserTest(object):
    def analyse_source(self, source):
        module = BytesIO(
            textwrap.dedent(source).encode('utf-8')
        )
        module.name = '<test>'
        analyser = TokenAnalyser(module)
        return analyser.analyse()


class TestIndentation(TokenAnalyserTest):
    def test_4_space_indent(self):
        source = u"""
        def foo():
            pass
        """
        warnings = self.analyse_source(source)
        assert warnings == []

    def test_non_4_space_top_level_indent(self):
        source = u"""
        def foo():
          pass
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, WrongNumberOfIndentationSpaces)
        assert warning.message == (
            u'Indented by 2 spaces instead of 4 as demanded by PEP 8'
        )
        assert warning.start == (3, 0)
        assert warning.end == (3, 2)

    def test_non_4_space_lower_level_indent(self):
        source = u"""
        def foo():
            if True:
              pass
            if True:
              pass
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 2

        first = warnings[0]
        assert isinstance(first, WrongNumberOfIndentationSpaces)
        assert first.message == (
            u'Indented by 2 spaces instead of 4 as demanded by PEP 8'
        )
        assert first.start == (4, 0)
        assert first.end == (4, 6)

        second = warnings[1]
        assert isinstance(second, WrongNumberOfIndentationSpaces)
        assert second.message == (
            u'Indented by 2 spaces instead of 4 as demanded by PEP 8'
        )
        assert second.start == (6, 0)
        assert second.end == (6, 6)

    def test_mix_spaces_and_tabs(self):
        source = u"""
        def foo():
        \t  1
        \t  pass
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 3
        assert any(
            isinstance(w, WrongNumberOfIndentationSpaces) for w in warnings
        )
        mixed_warnings = [
            w for w in warnings if isinstance(w, MixedTabsAndSpaces)
        ]
        assert len(mixed_warnings) == 2

        first = mixed_warnings[0]
        assert first.start == (3, 4)
        assert first.end == (3, 5)

        second = mixed_warnings[1]
        assert second.start == (4, 7)
        assert second.end == (4, 8)


class ASTAnalyserTest(object):
    def analyse_source(self, source):
        module = BytesIO(
            textwrap.dedent(source).encode('utf-8')
        )
        module.name = '<test>'
        analyser = ASTAnalyser(module)
        return analyser.analyse()


class TestImport(ASTAnalyserTest):
    def test_multi_import(self):
        source = u"""
        import foo, bar
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, MultipleImports)
        assert warning.message == (
            u'Multiple imports on one line. Should be on separate ones.'
        )
        assert warning.lineno == 2
        assert warning.file == '<test>'

    def test_star_import(self):
        source = u"""
        from foo import *
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, StarImport)
        assert warning.message == u'from ... import * should be avoided.'
        assert warning.lineno == 2
        assert warning.file == '<test>'
