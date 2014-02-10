# coding: utf-8
"""
    pythonic
    ~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst
"""
import pkg_resources


__version__ = pkg_resources.get_distribution('Pythonic').version
__version_info__ = tuple(map(int, __version__.split('-')[0].split('.')))
