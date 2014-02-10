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
from collections import namedtuple

from pyalysis.warnings import (
    WrongNumberOfIndentationSpaces, MixedTabsAndSpaces, MultipleImports
)
from pyalysis._compat import PY2


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
                u'Indented by {0} spaces instead of 4 as demanded by PEP 8'.format(added_indentation),
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
