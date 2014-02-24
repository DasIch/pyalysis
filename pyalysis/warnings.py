# coding: utf-8
"""
    pyalysis.warnings
    ~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from abc import ABCMeta

from pyalysis.utils import classproperty, iter_subclasses
from pyalysis._compat import with_metaclass, text_type


class Warning(object):
    attributes = [
        ('message', text_type),
        ('file', str)
    ]

    def __init__(self, *args, **kwargs):
        for (name, _), arg in zip(self.attributes, args):
            setattr(self, name, arg)
        for name, arg in kwargs.items():
            if any(name in (name for (name, _) in self.attributes)):
                setattr(self, name, arg)
            else:
                raise TypeError(
                    '__init__() got an unexpected keyword argument {!r}'
                    .format(name)
                )


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
    attributes = Warning.attributes + [
        ('start', (int, int)),
        ('end', (int, int))
    ]


@PEP8Warning.register
class LineTooLong(LineWarning):
    type = 'line-too-long'


class TokenWarning(Warning):
    attributes = Warning.attributes + [
        ('lineno', int)
    ]

    def __init__(self, message, file, start, end):
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
    attributes = Warning.attributes + [
        ('lineno', int)
    ]


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


class CSTWarning(Warning):
    attributes = Warning.attributes + [
        ('lineno', int)
    ]


@PEP8Warning.register
class ExtraneousWhitespace(CSTWarning):
    type = 'extraneous-whitespace'


def _create_warnings_mapping():
    warnings = {}
    for warning_super_cls in [Warning, AbstractWarning]:
        for warning_cls in iter_subclasses(warning_super_cls):
            if hasattr(warning_cls, 'type'):
                warnings[warning_cls.type] = warning_cls
    return warnings


WARNINGS = _create_warnings_mapping()
