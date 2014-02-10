# coding: utf-8
"""
    setup
    ~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from setuptools import setup, find_packages


setup(
    name='Pythonic',
    version='0.1.0-dev',
    url='https://github.com/DasIch/Pythonic',

    author='Daniel Neuhäuser and Contributors',
    author_email='ich@danielneuhaeuser.de',

    install_requires=[
        'Argvard>=0.2.0'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pythonic = pythonic.main:application'
        ]
    }
)
