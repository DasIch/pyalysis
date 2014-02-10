# coding: utf-8
"""
    tests.test_main
    ~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import subprocess

import pytest

from pyalysis import __version__


def test_version():
    output = subprocess.check_output(['pyalysis', '--version']).decode('ascii')
    assert output.strip() == __version__
