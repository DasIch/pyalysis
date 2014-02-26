# coding: utf-8
"""
    tests.test_ignore.test_init
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from io import StringIO

import pytest

from pyalysis.ignore import load_ignore_filter
from pyalysis.warnings import PrintStatement, DivStatement
from pyalysis.utils import Location


@pytest.mark.parametrize(('source', 'warning', 'allowed'), [
    (
        u'print-statement',
        PrintStatement(
            u'message', '<test>', Location(1, 0), Location(1, 10), []
        ),
        False
    ),
    (
        u'print-statement',
        DivStatement(
            u'message', '<test>', Location(1, 0), Location(1, 10), []
        ),
        True
    )
])
def test_load_ignore_filter(source, warning, allowed):
    file = StringIO(source)
    file.name = '<test>'
    filter, warnings = load_ignore_filter(file)
    assert filter(warning) == allowed
    assert not warnings
