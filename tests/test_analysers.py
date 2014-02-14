# coding: utf-8
"""
    tests.test_analysers
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from io import BytesIO

import pytest

from pyalysis.analysers import (
    LineAnalyser, TokenAnalyser, CSTAnalyser, ASTAnalyser
)
from pyalysis.warnings import (
    WrongNumberOfIndentationSpaces, MixedTabsAndSpaces, MultipleImports,
    StarImport, IndiscriminateExcept, GlobalKeyword, PrintStatement,
    DivStatement, ExtraneousWhitespace
)
from pyalysis._compat import PY2


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


class CSTAnalyserTest(object):
    def analyse_source(self, source):
        module = BytesIO(
            textwrap.dedent(source).encode('utf-8')
        )
        module.name = '<test>'
        analyser = CSTAnalyser(module)
        return analyser.analyse()


class TestExtraneousWhitespace(CSTAnalyserTest):
    def test_list_empty(self):
        source = u'[ ]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace in empty list.'
        )
        assert warning.lineno == 1

    @pytest.mark.parametrize('source', [u'[ 1]', u'[ 1, 2]'])
    def test_list_beginning(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the beginning of a list.'
        )
        assert warning.lineno == 1

    @pytest.mark.parametrize('source', [u'[1 ]', u'[1, 2 ]'])
    def test_list_end(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the end of a list.'
        )
        assert warning.lineno == 1

    def test_list_comma(self):
        source = u'[1 , 2]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before comma in list.'
        )
        assert warning.lineno == 1

    def test_before_slicing_or_indexing(self):
        source = u'foo [0]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before slicing or indexing.'
        )
        assert warning.lineno == 1

    def test_beginning_of_slicing_or_indexing(self):
        source = u'foo[ 0]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the beginning of slicing or indexing.'
        )
        assert warning.lineno == 1

    def test_end_of_slicing_or_indexing(self):
        source = u'foo[0 ]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the end of slicing or indexing.'
        )
        assert warning.lineno == 1

    @pytest.mark.parametrize('source', [u'foo[ 0:]', u'foo[ 0::]'])
    def test_beginning_of_slicing(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the beginning of slicing.'
        )
        assert warning.lineno == 1

    @pytest.mark.parametrize('source', [u'foo[0: ]', u'foo[0:: ]'])
    def test_end_of_slicing(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the end of slicing.'
        )
        assert warning.lineno == 1

    def test_empty_dict(self):
        source = u'{ }'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace in empty dict.'
        )
        assert warning.lineno == 1

    def test_dict_beginning(self):
        source = u'{ 1: 2}'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at beginning of dict.'
        )
        assert warning.lineno == 1

    def test_dict_end(self):
        source = u'{1: 2 }'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at end of dict.'
        )
        assert warning.lineno == 1

    def test_dict_colon(self):
        source = u'{1 : 2}'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before colon in dict.'
        )
        assert warning.lineno == 1

    @pytest.mark.parametrize('source', [u'{ 1}', u'{ 1, 2}'])
    def test_set_beginning(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at beginning of set.'
        )
        assert warning.lineno == 1

    @pytest.mark.parametrize('source', [u'{1 }', u'{1, 2 }'])
    def test_set_end(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at end of set.'
        )
        assert warning.lineno == 1

    def test_set_colon(self):
        source = u'{1 , 2}'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before comma in set.'
        )
        assert warning.lineno == 1

    def test_tuple_beginning(self):
        source = u'( 1,)'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at beginning of tuple.'
        )
        assert warning.lineno == 1

    def test_tuple_end(self):
        source = u'(1, 2 )'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at end of tuple.'
        )
        assert warning.lineno == 1

    def test_tuple_comma(self):
        source = u'(1 , 2)'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before comma in tuple.'
        )
        assert warning.lineno == 1



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


class TestExcept(ASTAnalyserTest):
    def test(self):
        source = u"""
        try:
            foo
        except:
            pass
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, IndiscriminateExcept)
        assert warning.message == (
            u'Never use except without a specific exception.'
        )
        assert warning.lineno == 4
        assert warning.file == '<test>'


class TestGlobalKeyword(ASTAnalyserTest):
    def test(self):
        source = u"""
        def foo():
            global spam
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, GlobalKeyword)
        assert warning.message == u'The global keyword should be avoided.'
        assert warning.lineno == 3
        assert warning.file == '<test>'


class TestPrintStatement(ASTAnalyserTest):
    @pytest.mark.skipif(not PY2, reason='removed in Python 3')
    def test(self):
        source = u"""
        print "foo"
        """
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, PrintStatement)
        assert warning.message == (
            u'The print statement has been removed in Python 3. Import '
            u'print() with from __future__ import print_function instead.'
        )
        assert warning.lineno == 2
        assert warning.file == '<test>'

    def test_future_works(self):
        source = u"""
        from __future__ import print_function
        print("foo")
        """
        warnings = self.analyse_source(source)
        assert not warnings


class TestDivStatement(ASTAnalyserTest):
    def test(self):
        source = u"""
        1 / 1
        """
        warnings = self.analyse_source(source)
        if PY2:
            assert len(warnings) == 1
            warning = warnings[0]
            assert isinstance(warning, DivStatement)
        else:
            assert not warnings

    def test_future_works(self):
        source = u"""
        from __future__ import division
        1 / 1
        """
        warnings = self.analyse_source(source)
        assert not warnings
