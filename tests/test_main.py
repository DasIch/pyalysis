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


def check_output(command):
    return subprocess.check_output(command).decode('utf-8')


def test_version():
    output = check_output(['pyalysis', '--version'])
    assert output.strip() == __version__


def test_main_successful():
    output = check_output(['pyalysis', __file__])
    assert output == u''


def test_main_unsuccessful(tmpdir):
    module = os.path.join(str(tmpdir), 'dirty.py')
    with open(module, 'wb') as f:
        f.write(b'"' + b'x' * 80 + b'"' +
                b'\nimport os, sys\ndef foo():\n  pass')
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        check_output(['pyalysis', module])
    error = exc_info.value
    assert error.returncode == 1
    print error.output.decode('utf-8')
    assert error.output.decode('utf-8') == textwrap.dedent(u"""\
    {{
        "file": "{0}", 
        "lineno": 1, 
        "message": "{1}"
    }}
    {{
        "end": [
            4, 
            2
        ], 
        "file": "{0}", 
        "lineno": 4, 
        "message": "Indented by 2 spaces instead of 4 as demanded by PEP 8", 
        "start": [
            4, 
            0
        ]
    }}
    {{
        "file": "{0}", 
        "lineno": 2, 
        "message": "Multiple imports on one line. Should be on separate ones."
    }}
    """.format(
        module,
        u'Line is longer than 79 characters. You should keep it below that'
    ))
