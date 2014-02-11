# coding: utf-8
"""
    pyalysis.ignore.compiler
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from pyalysis.warnings import WARNINGS


def compile(filters):
    compiled = map(compile_filter, filters)
    return lambda warning: any(f(warning) for f in compiled)


def compile_filter(filter):
    warning_cls = WARNINGS[filter.name]
    return lambda warning: not isinstance(warning, warning_cls)
