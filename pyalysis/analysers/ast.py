# coding: utf-8
"""
    pyalysis.analysers.ast
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import absolute_import
import ast

from pyalysis.warnings import (
    MultipleImports, StarImport, IndiscriminateExcept, GlobalKeyword,
    PrintStatement, DivStatement
)
from pyalysis._compat import PY2


class ASTAnalyser(object):
    """
    AST-level analyser of Python source code.
    """
    def __init__(self, module):
        self.module = module

        self.ast = ast.parse(module.read(), module.name)
        self.warnings = []

        self.div_is_floor_on_int = PY2

    def emit(self, warning_cls, message, node):
        """
        Creates an instance of `warning_cls` using the given `message` and the
        information in `node` and appends it to :attr:`warnings`.
        """
        self.warnings.append(
            warning_cls(message, self.module.name, node.lineno)
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
        if node.module == u'__future__':
            if any(alias.name == u'division' for alias in node.names):
                self.div_is_floor_on_int = False

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

    def analyse_node_BinOp(self, node):
        if isinstance(node.op, ast.Div) and self.div_is_floor_on_int:
            self.emit(
                DivStatement,
                u'Don\'t use / without from __future__ import division. Use '
                u'//, if you really want floor division.',
                node
            )
