# coding: utf-8
"""
    pyalysis.ignore
    ~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from pyalysis.ignore.lexer import lex
from pyalysis.ignore.parser import parse
from pyalysis.ignore.verifier import verify
from pyalysis.ignore.compiler import compile


def load_ignore_filter(file):
    return compile(verify(parse(lex(file.read()), file.name)))
