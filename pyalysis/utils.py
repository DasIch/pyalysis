# coding: utf-8
"""
    pyalysis.utils
    ~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import re
import codecs
import tokenize

from pyalysis._compat import PY2


# as defined in PEP 263
_magic_encoding_comment = re.compile("coding[:=]\s*([-\w.]+)")


if PY2:
    def detect_encoding(file):
        encoding = 'utf-8'
        bom_found = False
        possible_bom = file.read(len(codecs.BOM_UTF8))
        if possible_bom == codecs.BOM_UTF8:
            encoding = 'utf-8-sig'
            bom_found = True
        file.seek(0)
        first = file.readline()
        match = _magic_encoding_comment.search(first)
        if match is None:
            second = file.readline()
            match = _magic_encoding_comment.search(second)
            if match is not None:
                encoding = match.group(1)
        else:
            encoding = match.group(1)
        if bom_found:
            if encoding == 'utf-8' or encoding == 'utf-8-sig':
                encoding = 'utf-8-sig'
            else:
                raise SyntaxError(
                    'Found utf8 BOM in conflict with encoding declaration'
                )
        file.seek(0)
        return encoding
else:
    def detect_encoding(file):
        try:
            encoding = tokenize.detect_encoding(file.readline)[0]
        finally:
            file.seek(0)
        return encoding


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        return self.fget(owner)


def iter_subclasses(cls):
    for subclass in cls.__subclasses__():
        for subsubclass in iter_subclasses(subclass):
            yield subsubclass
    yield cls
