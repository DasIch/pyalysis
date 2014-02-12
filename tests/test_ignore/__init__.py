# coding: utf-8
"""
    tests.test_ignore
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from io import StringIO

import pytest

from pyalysis.ignore import load_ignore_filter
from pyalysis.warnings import PrintStatement, DivStatement



@pytest.mark.parametrize(('source', 'warning', 'allowed'), [
    (u'print-statement', PrintStatement(u'message', '<test>', 1), False),
    (u'print-statement', DivStatement(u'message', '<test>', 1), True)
])
def test_load_ignore_filer(source, warning, allowed):
    file = StringIO(source)
    file.name = '<test>'
    assert load_ignore_filter(file)(warning) == allowed
