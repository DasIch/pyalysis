# coding: utf-8
"""
    tests.test_main
    ~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import os
import subprocess
import textwrap

import pytest

from pyalysis import __version__


def test_version():
    output = subprocess.check_output(['pyalysis', '--version']).decode('utf-8')
    assert output.strip() == __version__


def test_main_successful():
    output = subprocess.check_output(['pyalysis', __file__]).decode('utf-8')
    assert output == u''


def test_main_unsuccessful(tmpdir):
    module = os.path.join(str(tmpdir), 'dirty.py')
    with open(module, 'wb') as f:
        f.write(b'def foo():\n  pass')
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        subprocess.check_output(['pyalysis', module])
    error = exc_info.value
    assert error.returncode == 1
    assert error.output.decode('utf-8') == textwrap.dedent(u"""\
    {{
        "end": [
            2, 
            2
        ], 
        "file": "{0}", 
        "message": "Indented by 2 spaces instead of 4 as demanded by PEP 8", 
        "start": [
            2, 
            0
        ]
    }}
    """.format(module))
