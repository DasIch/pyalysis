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
        file.seek(0)
        return encoding
else:
    def detect_encoding(file):
        try:
            encoding = tokenize.detect_encoding(file.readline)[0]
        finally:
            file.seek(0)
        return encoding
