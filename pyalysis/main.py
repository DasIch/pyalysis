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
import codecs

from argvard import Argvard

from pyalysis import __version__
from pyalysis.formatters import JSONFormatter
from pyalysis.analysers import TokenAnalyser
from pyalysis._compat import PY2


if PY2:
    stdout = codecs.lookup(
        sys.stdout.encoding or 'utf-8'
    ).streamwriter(sys.stdout)
else:
    stdout = sys.stdout


application = Argvard(defaults={
    'format': JSONFormatter,
    'output': stdout
})


@application.option('--version')
def version(context):
    print(__version__)
    sys.exit(0)


@application.main('files...')
def main(context, files):
    warned = False
    formatter = context['format'](context['output'])
    for path in files:
        with open(path, 'rb') as module:
            analyser = TokenAnalyser(module)
            for warning in analyser.analyse():
                warned = True
                formatter.format(warning)
    if warned:
        sys.exit(1)
    else:
        sys.exit(0)
