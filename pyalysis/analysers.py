# coding: utf-8
"""
    pyalysis.analysers
    ~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import token
import tokenize
import ast
import codecs
from collections import namedtuple

from pyalysis.warnings import (
    LineTooLong, WrongNumberOfIndentationSpaces, MixedTabsAndSpaces,
    MultipleImports, StarImport, IndiscriminateExcept, GlobalKeyword,
    PrintStatement
)
from pyalysis.utils import detect_encoding
from pyalysis._compat import PY2


class LineAnalyser(object):
    """
    Line-level analyser of Python source code.
    """
    def __init__(self, module):
        self.module = module

        self.encoding = detect_encoding(module)
        self.warnings = []

    def emit(self, warning_cls, message, lineno):
        self.warnings.append(warning_cls(message, lineno, self.module.name))

    def analyse(self):
        reader = codecs.lookup(self.encoding).streamreader(self.module)
        for i, line in enumerate(reader, 1):
            self.analyse_line(i, line)
        return self.warnings

    def analyse_line(self, lineno, line):
        if len(line.rstrip()) > 79:
            self.emit(
                LineTooLong,
                u'Line is longer than 79 characters. '
                u'You should keep it below that',
                lineno
            )


Token = namedtuple('Token', ['type', 'lexeme', 'start', 'end', 'logical_line'])
Location = namedtuple('Location', ['line', 'column'])


class TokenAnalyser(object):
    """
    Token-level analyser of Python source code.
    """
    def __init__(self, module):
        self.module = module

        self.warnings = []
        self.indentation_stack = []

    def emit(self, warning_cls, message, tok):
        """
        Creates an instance of `warning_cls` using the given `message` and the
        information in `tok`.
        """
        self.warnings.append(
            warning_cls(message, tok.start, tok.end, self.module.name)
        )

    def generate_tokens(self):
        """
        Generates tokens similar to :func:`tokenize.generate_tokens` but uses
        namedtuples, see :class:`Token` and :class:`Location`.
        """
        # tokenize.generate_tokens in Python 3.x does not work with bytes so we
        # have to use tokenize.tokenize instead which works exactly like
        # tokenize.generate_tokens does.
        if PY2:
            generate_tokens = tokenize.generate_tokens
        else:
            generate_tokens = tokenize.tokenize
        for tok in generate_tokens(self.module.readline):
            type, lexeme, start, end, logical_line = tok
            start = Location(*start)
            end = Location(*end)
            tok = Token(type, lexeme, start, end, logical_line)
            yield tok

    def analyse(self):
        """
        Analyses the module passed to the instance and returns a list of
        :class:`pyalysis.warnings.TokenWarning` instances.
        """
        for tok in self.generate_tokens():
            name = token.tok_name[tok.type]
            method_name = 'analyse_' + name
            method = getattr(self, method_name, None)
            if method is not None:
                method(tok)
        return self.warnings

    def analyse_INDENT(self, tok):
        line_indentation = tok.lexeme.count(u'\t') * 8 + tok.lexeme.count(u' ')
        added_indentation = line_indentation - sum(self.indentation_stack)
        if added_indentation != 4:
            self.emit(
                WrongNumberOfIndentationSpaces,
                u'Indented by {0} spaces instead of 4 as demanded by PEP 8' \
                        .format(added_indentation),
                tok
            )
        self.indentation_stack.append(added_indentation)

    def analyse_DEDENT(self, tok):
        # tok.lexeme on DEDENT tokens is always the empty string, therefore we
        # only know that we have to jump back to the previous indentation
        # level. This is why we maintain a stack with each element being the
        # added amount of indentation.
        self.indentation_stack.pop()

    def analyse_NEWLINE(self, tok):
        indentation = tok.logical_line[:-len(tok.logical_line.lstrip())]
        if u' ' in indentation and u'\t' in indentation:
            self.emit(
                MixedTabsAndSpaces,
                u'Tabs and spaces are mixed. This is disallowed on Python 3 '
                u'and inconsistent. Use either tabs or spaces exclusively, '
                u'preferably spaces.',
                tok
            )


class ASTAnalyser(object):
    """
    AST-level analyser of Python source code.
    """
    def __init__(self, module):
        self.module = module

        self.ast = ast.parse(module.read(), module.name)
        self.warnings = []

    def emit(self, warning_cls, message, node):
        """
        Creates an instance of `warning_cls` using the given `message` and the
        information in `node` and appends it to :attr:`warnings`.
        """
        self.warnings.append(
            warning_cls(message, node.lineno, self.module.name)
        )

    def analyse(self):
        """
        Analyses the module passed to the instance and returns a list of
        :class:`pyalysis.warnings.ASTWarning` instances.
        """
        self.analyse_node(self.ast)
        return self.warnings

    def analyse_node(self, node):
        for child in ast.iter_child_nodes(node):
            self.analyse_node(child)
        name = node.__class__.__name__
        method_name = 'analyse_node_' + name
        method = getattr(self, method_name, None)
        if method is not None:
            method(node)

    def analyse_node_Import(self, node):
        if len(node.names) > 1:
            self.emit(
                MultipleImports,
                u'Multiple imports on one line. Should be on separate ones.',
                node
            )

    def analyse_node_ImportFrom(self, node):
        if len(node.names) == 1 and node.names[0].name == u'*':
            self.emit(
                StarImport,
                u'from ... import * should be avoided.',
                node
            )

    def analyse_node_Try(self, node):
        if len(node.handlers) == 1 and node.handlers[0].type is None:
            self.emit(
                IndiscriminateExcept,
                u'Never use except without a specific exception.',
                node.handlers[0]
            )
    if PY2:
        analyse_node_TryExcept = analyse_node_Try
        analyse_node_TryExcept.__name__ = 'analyse_node_TryExcept'

    def analyse_node_Global(self, node):
        self.emit(
            GlobalKeyword,
            u'The global keyword should be avoided.',
            node
        )

    def analyse_node_Print(self, node):
        self.emit(
            PrintStatement,
            u'The print statement has been removed in Python 3. Import '
            u'print() with from __future__ import print_function instead.',
            node
        )
