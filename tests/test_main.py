# coding: utf-8
"""
    tests.test_main
    ~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import subprocess

import pytest

from pythonic import __version__


def test_version():
    output = subprocess.check_output(['pythonic', '--version']).decode('ascii')
    assert output.strip() == __version__
