# coding: utf-8
"""
    tests.test_utils
    ~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import codecs
from io import BytesIO

import pytest

from pyalysis.utils import detect_encoding, classproperty


@pytest.mark.parametrize(('source', 'expected'), [
    (b'', 'utf-8'),
    (codecs.BOM_UTF8, 'utf-8-sig'),
    (b'# coding: iso-8859-1', 'iso-8859-1'),
    (b'# foobar\n# coding: ascii', 'ascii')
])
def test_detect_encoding(source, expected):
    file = BytesIO(source)
    assert detect_encoding(file) == expected
    assert file.read() == source


def test_detect_encoding_bom_conflict():
    file = BytesIO(codecs.BOM_UTF8 + b'# coding: ascii')
    with pytest.raises(SyntaxError):
        detect_encoding(file)


def test_classproperty():
    class Foo(object):
        @classproperty
        def spam(cls):
            return 'spam'

    assert Foo.spam == 'spam'
    assert Foo().spam == 'spam'
