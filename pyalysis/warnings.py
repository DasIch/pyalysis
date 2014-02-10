# coding: utf-8
"""
    pyalysis.warnings
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""


class TokenWarning(object):
    def __init__(self, message, start, end, file):
        self.message = message
        self.start = start
        self.end = end
        self.file = file


class WrongNumberOfIndentationSpaces(TokenWarning):
    pass


class MixedTabsAndSpaces(TokenWarning):
    pass


class ASTWarning(object):
    def __init__(self, message, line, file):
        self.message = message
        self.line = line
        self.file = file


class MultipleImports(ASTWarning):
    pass
