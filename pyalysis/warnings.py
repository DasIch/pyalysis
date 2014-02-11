# coding: utf-8
"""
    pyalysis.warnings
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from abc import ABCMeta

from pyalysis.utils import classproperty
from pyalysis._compat import with_metaclass


class Warning(object):
    def __init__(self, message, file):
        self.message = message
        self.file = file


class AbstractWarningMeta(ABCMeta):
    def __init__(self, name, bases, attributes):
        ABCMeta.__init__(self, name, bases, attributes)
        self.warnings = set()

    def register(self, subclass):
        ABCMeta.register(self, subclass)
        self.warnings.add(subclass)
        return subclass


class AbstractWarning(with_metaclass(AbstractWarningMeta)):
    @classproperty
    def types(cls):
        return {cls.type for cls in cls.mro() if hasattr(cls, 'type')}


class PEP8Warning(AbstractWarning):
    type = 'pep8'


class Python3CompatibilityWarning(AbstractWarning):
    type = 'python3-compatibility'


class LineWarning(Warning):
    def __init__(self, message, lineno, file):
        Warning.__init__(self, message, file)
        self.lineno = lineno


@PEP8Warning.register
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


@PEP8Warning.register
class WrongNumberOfIndentationSpaces(TokenWarning):
    type = 'wrong-number-of-indentation-spaces'


class MixedTabsAndSpaces(TokenWarning):
    type = 'mixed-tabs-and-spaces'


class ASTWarning(Warning):
    def __init__(self, message, lineno, file):
        Warning.__init__(self, message, file)
        self.lineno = lineno


@PEP8Warning.register
class MultipleImports(ASTWarning):
    type = 'multiple-imports'


class StarImport(ASTWarning):
    type = 'star-import'


class IndiscriminateExcept(ASTWarning):
    type = 'indiscriminate-except'


class GlobalKeyword(ASTWarning):
    type = 'global-keyword'


@Python3CompatibilityWarning.register
class PrintStatement(ASTWarning):
    type = 'print-statement'


@Python3CompatibilityWarning.register
class DivStatement(ASTWarning):
    type = 'div-statement'
