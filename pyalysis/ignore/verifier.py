# coding: utf-8
"""
    pyalysis.ignore.verifier
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import warnings

from pyalysis.warnings import WARNINGS


class IgnoreVerificationWarning(UserWarning):
    pass


def verify(ignore_file):
    for filter in ignore_file.filters:
        filter = verify_filter(filter)
        if filter is not None:
            yield filter


def verify_filter(filter):
    try:
        WARNINGS[filter.name]
    except KeyError:
        warnings.warn(
            (
                u'Ignoring filter with unknown warning type: '
                u'"{}" in line {}.'
            ).format(filter.name, filter.start.line),
            IgnoreVerificationWarning
        )
        return None
    return filter
