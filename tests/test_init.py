# coding: utf-8
"""
    tests.test_init
    ~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst
"""
import re

import pyalysis


def test_version():
    assert re.match(r'\d+\.\d+\.\d+(-\w+)?', pyalysis.__version__)


def test_version_info():
    assert len(pyalysis.__version_info__) == 3
    assert all(isinstance(part, int) for part in pyalysis.__version_info__)
