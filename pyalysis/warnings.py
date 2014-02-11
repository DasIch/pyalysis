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
    pass


class TokenWarning(Warning):
    def __init__(self, message, start, end, file):
        Warning.__init__(self, message, file)
        self.start = start
        self.end = end

    @property
    def lineno(self):
        return self.start[0]


class WrongNumberOfIndentationSpaces(TokenWarning):
    pass


class MixedTabsAndSpaces(TokenWarning):
    pass


class ASTWarning(Warning):
    def __init__(self, message, lineno, file):
        Warning.__init__(self, message, file)
        self.lineno = lineno


class MultipleImports(ASTWarning):
    pass


class StarImport(ASTWarning):
    pass


class IndiscriminateExcept(ASTWarning):
    pass
