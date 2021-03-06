# coding: utf-8
"""
    tests.test_main
    ~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import os
import codecs
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
        f.write(b'"' + b'x' * 80 + b'"\n' +
                b'import os, sys\n' +
                b'def foo():\n  pass\n' +
                b'[ 1, 2]')
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        check_output(['pyalysis', module])
    error = exc_info.value
    assert error.returncode == 1
    assert error.output.decode('utf-8') == textwrap.dedent(u"""\
    File "{0}", line 1
      {1}
    Line is longer than 79 characters. You should keep it below that

    File "{0}", line 4
        pass
    Indented by 2 spaces instead of 4 as demanded by PEP 8

    File "{0}", line 5
      [ 1, 2]
    Extraneous whitespace at the beginning of a list.

    File "{0}", line 2
      import os, sys
    Multiple imports on one line. Should be on separate ones.

    """.format(module, u'"' + u'x' * 80 + u'"'))


def test_main_ignore(tmpcwd):
    ignore_path = os.path.join(tmpcwd, '.pyalysis.ignore')
    with codecs.open(ignore_path, 'w', encoding='utf-8') as ignore_file:
        ignore_file.write(u'wrong-number-of-indentation-spaces')

    module_path = os.path.join(tmpcwd, 'foo.py')
    with codecs.open(module_path, 'w', encoding='utf-8') as foo:
        foo.write(u'def foo():\n  pass')

    check_output(['pyalysis', module_path]) == u''


def test_main_directory(tmpcwd):
    os.mkdir('foo')
    with codecs.open('foo/spam.py', 'w', encoding='utf-8') as spam:
        spam.write(u'def foo():\n pass')

    with codecs.open('foo/eggs.py', 'w', encoding='utf-8') as eggs:
        eggs.write(u'def foo():\n pass')

    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        check_output(['pyalysis', 'foo'])
    error = exc_info.value
    assert error.returncode == 1
    messages = error.output.decode('utf-8').rstrip().split(u'\n\n')
    assert textwrap.dedent(u"""\
    File "foo/spam.py", line 2
       pass
    Indented by 1 spaces instead of 4 as demanded by PEP 8""") in messages
    assert textwrap.dedent(u"""\
    File "foo/eggs.py", line 2
       pass
    Indented by 1 spaces instead of 4 as demanded by PEP 8""") in messages
