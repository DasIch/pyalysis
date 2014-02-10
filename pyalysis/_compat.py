# coding: utf-8
"""
    pyalysis._compat
    ~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
"""
import sys
try:
    import __pypy__
    PYPY = True
except ImportError:
    PYPY = False


PY2 = sys.version_info[0] == 2
