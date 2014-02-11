# coding: utf-8
"""
    pyalysis.warnings
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""


class Warning(object):
    def __init__(self, message, file):
        self.message = message
        self.file = file


class LineWarning(Warning):
    def __init__(self, message, lineno, file):
        Warning.__init__(self, message, file)
        self.lineno = lineno


class LineTooLong(LineWarning):
    type = 'line-too-long'


class TokenWarning(Warning):
    def __init__(self, message, start, end, file):
        Warning.__init__(self, message, file)
        self.start = start
        self.end = end

    @property
    def lineno(self):
        return self.start[0]


class WrongNumberOfIndentationSpaces(TokenWarning):
    type = 'wrong-number-of-indentation-spaces'


class MixedTabsAndSpaces(TokenWarning):
    type = 'mixed-tabs-and-spaces'


class ASTWarning(Warning):
    def __init__(self, message, lineno, file):
        Warning.__init__(self, message, file)
        self.lineno = lineno


class MultipleImports(ASTWarning):
    type = 'multiple-imports'


class StarImport(ASTWarning):
    type = 'star-import'


class IndiscriminateExcept(ASTWarning):
    type = 'indiscriminate-except'


class GlobalKeyword(ASTWarning):
    type = 'global-keyword'


class PrintStatement(ASTWarning):
    type = 'print-statement'


class DivStatement(ASTWarning):
    type = 'div-statement'
