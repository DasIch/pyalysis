# coding: utf-8
"""
    tests.test_analysers.test_ast
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from io import BytesIO

import pytest

from pyalysis.analysers import ASTAnalyser
from pyalysis.warnings import (
    MultipleImports, StarImport, IndiscriminateExcept, GlobalKeyword,
    PrintStatement, DivStatement
)
from pyalysis._compat import PY2


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
