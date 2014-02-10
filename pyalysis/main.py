# coding: utf-8
"""
    pyalysis.main
    ~~~~~~~~~~~~~

    The Pyalysis command line interface.

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst
"""
from __future__ import print_function
import sys

from argvard import Argvard

from pyalysis import __version__


application = Argvard()


@application.option('--version')
def version(context):
    print(__version__)
    sys.exit(0)


@application.main('files...')
def main(context, files):
    print(files)
