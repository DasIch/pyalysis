# coding: utf-8
"""
    tests.conftest
    ~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import os

import pytest


@pytest.yield_fixture
def tmpcwd(tmpdir):
    tmpdir = str(tmpdir)
    cwd = os.getcwd()
    os.chdir(tmpdir)
    yield tmpdir
    os.chdir(cwd)
