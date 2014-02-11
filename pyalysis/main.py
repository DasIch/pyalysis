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
from pyalysis.analysers import LineAnalyser, TokenAnalyser, ASTAnalyser
from pyalysis.ignore import load_ignore_filter
from pyalysis._compat import PY2


if PY2:
    stdout = codecs.lookup(
        sys.stdout.encoding or 'utf-8'
    ).streamwriter(sys.stdout)
else:
    stdout = sys.stdout


IGNORE_FILE = '.pyalysis.ignore'


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
    try:
        with codecs.open(IGNORE_FILE, 'r', encoding='utf-8') as ignore_file:
            should_emit = load_ignore_filter(ignore_file)
    except IOError:
        should_emit = lambda _: True

    warned = False
    formatter = context['format'](context['output'])
    for path in files:
        with open(path, 'rb') as module:
            for analyser_cls in [LineAnalyser, TokenAnalyser, ASTAnalyser]:
                analyser = analyser_cls(module)
                for warning in filter(should_emit, analyser.analyse()):
                    warned = True
                    formatter.format(warning)
                module.seek(0)
    if warned:
        sys.exit(1)
    else:
        sys.exit(0)
