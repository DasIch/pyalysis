# coding: utf-8
"""
    pyalysis.main
    ~~~~~~~~~~~~~

    The Pyalysis command line interface.

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst
"""
from __future__ import print_function
import os
import sys

from argvard import Argvard

from pyalysis import __version__
from pyalysis.application import Pyalysis


application = Argvard()


@application.option('--version')
def version(context):
    print(__version__)
    sys.exit(0)


def iter_python_files(path):
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                yield os.path.join(root, file)


@application.main('paths...')
def main(context, paths):
    pyalysis = Pyalysis()
    files = []
    for path in paths:
        if os.path.isdir(path):
            files.extend(iter_python_files(path))
        else:
            files.append(path)
    pyalysis.analyse(files)
