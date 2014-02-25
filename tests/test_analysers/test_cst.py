# coding: utf-8
"""
    tests.test_analysers.test_cst
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import textwrap
from io import BytesIO

import pytest

from pyalysis.analysers import CSTAnalyser
from pyalysis.warnings import ExtraneousWhitespace


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
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    @pytest.mark.parametrize('source', [u'[ 1]', u'[ 1, 2]'])
    def test_list_beginning(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the beginning of a list.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    @pytest.mark.parametrize('source', [u'[1 ]', u'[1, 2 ]'])
    def test_list_end(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the end of a list.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_list_comma(self):
        source = u'[1 , 2]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before comma in list.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_before_slicing_or_indexing(self):
        source = u'foo [0]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before slicing or indexing.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_beginning_of_slicing_or_indexing(self):
        source = u'foo[ 0]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the beginning of slicing or indexing.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_end_of_slicing_or_indexing(self):
        source = u'foo[0 ]'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the end of slicing or indexing.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    @pytest.mark.parametrize('source', [u'foo[ 0:]', u'foo[ 0::]'])
    def test_beginning_of_slicing(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the beginning of slicing.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    @pytest.mark.parametrize('source', [u'foo[0: ]', u'foo[0:: ]'])
    def test_end_of_slicing(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at the end of slicing.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_empty_dict(self):
        source = u'{ }'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace in empty dict.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_dict_beginning(self):
        source = u'{ 1: 2}'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at beginning of dict.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_dict_end(self):
        source = u'{1: 2 }'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at end of dict.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_dict_colon(self):
        source = u'{1 : 2}'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before colon in dict.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    @pytest.mark.parametrize('source', [u'{ 1}', u'{ 1, 2}'])
    def test_set_beginning(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at beginning of set.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    @pytest.mark.parametrize('source', [u'{1 }', u'{1, 2 }'])
    def test_set_end(self, source):
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at end of set.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_set_colon(self):
        source = u'{1 , 2}'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before comma in set.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_tuple_beginning(self):
        source = u'( 1,)'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at beginning of tuple.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_tuple_end(self):
        source = u'(1, 2 )'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at end of tuple.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_tuple_comma(self):
        source = u'(1 , 2)'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before comma in tuple.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_before_function_call(self):
        source = u'foo ()'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before arguments of function call.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_function_call_empty(self):
        source = u'foo( )'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace in arguments of function call.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_function_call_beginning(self):
        source = u'foo( 1)'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at beginning of function call arguments.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_function_call_end(self):
        source = u'foo(1 )'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace at end of function call arguments.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))

    def test_function_call_comma(self):
        source = u'foo(1 , 2)'
        warnings = self.analyse_source(source)
        assert len(warnings) == 1
        warning = warnings[0]
        assert isinstance(warning, ExtraneousWhitespace)
        assert warning.message == (
            u'Extraneous whitespace before comma in function call arguments.'
        )
        assert warning.start == (1, 0)
        assert warning.end == (1, len(source))
