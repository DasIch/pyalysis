# coding: utf-8
"""
    pyalysis
    ~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst
"""
import pkg_resources


try:
    __version__ = pkg_resources.get_distribution('Pyalysis').version
    __version_info__ = tuple(map(int, __version__.split('-')[0].split('.')))
except pkg_resources.DistributionNotFound:
    __version__ = 'development'
    __version_info__ = (0, 0, 0)
