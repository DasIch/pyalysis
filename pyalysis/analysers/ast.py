# coding: utf-8
"""
    pyalysis.analysers.ast
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import absolute_import
import ast
import inspect

from blinker import Signal

from pyalysis.warnings import (
    MultipleImports, StarImport, IndiscriminateExcept, GlobalKeyword,
    PrintStatement, DivStatement
)
from pyalysis.analysers.base import AnalyserBase
from pyalysis.utils import Location
from pyalysis._compat import PY2, with_metaclass


class ASTAnalyserMeta(type):
    def __init__(self, name, bases, attributes):
        type.__init__(self, name, bases, attributes)
        for name in dir(ast):
            attribute = getattr(ast, name)
            if inspect.isclass(attribute) and issubclass(attribute, ast.AST):
                setattr(self, 'on_' + name, Signal())


class ASTAnalyser(with_metaclass(ASTAnalyserMeta, AnalyserBase)):
    """
    AST-level analyser of Python source code.
    """
    def __init__(self, module):
        AnalyserBase.__init__(self, module)

        self.ast = ast.parse(module.read(), module.name)

    def emit(self, warning_cls, message, node):
        """
        Creates an instance of `warning_cls` using the given `message` and the
        information in `node` and appends it to :attr:`warnings`.
        """
        start_lineno, end_lineno = self.get_logical_line_range(node.lineno)
        start = Location(start_lineno, 0)
        end = Location(end_lineno, len(self.physical_lines[end_lineno - 1]))
        AnalyserBase.emit(self, warning_cls, message, start, end)

    def analyse(self):
        """
        Analyses the module passed to the instance and returns a list of
        :class:`pyalysis.warnings.ASTWarning` instances.
        """
        self.on_analyse.send(self)
        self.analyse_node(self.ast)
        return self.warnings

    def analyse_node(self, node):
        for child in ast.iter_child_nodes(node):
            self.analyse_node(child)
        name = node.__class__.__name__
        signal_name = 'on_' + name
        signal = getattr(self, signal_name)
        signal.send(self, node=node)


@ASTAnalyser.on_Import.connect
def check_multi_import(analyser, node):
    if len(node.names) > 1:
        analyser.emit(
            MultipleImports,
            u'Multiple imports on one line. Should be on separate ones.',
            node
        )


@ASTAnalyser.on_ImportFrom.connect
def check_star_import(analyser, node):
    if len(node.names) == 1 and node.names[0].name == u'*':
        analyser.emit(
            StarImport,
            u'from ... import * should be avoided.',
            node
        )


@ASTAnalyser.on_Global.connect
def check_global(analyser, node):
    analyser.emit(
        GlobalKeyword,
        u'The global keyword should be avoided.',
        node
    )


if PY2:
    @ASTAnalyser.on_Print.connect
    def check_print(analyser, node):
        analyser.emit(
            PrintStatement,
            u'The print statement has been removed in Python 3. Import '
            u'print() with from __future__ import print_function instead.',
            node
        )


def check_indiscriminate_except(analyser, node):
    if len(node.handlers) == 1 and node.handlers[0].type is None:
        analyser.emit(
            IndiscriminateExcept,
            u'Never use except without a specific exception.',
            node.handlers[0]
        )
if PY2:
    ASTAnalyser.on_TryExcept.connect(check_indiscriminate_except)
else:
    ASTAnalyser.on_Try.connect(check_indiscriminate_except)


@ASTAnalyser.on_analyse.connect
def check_ambiguous(analyser):
    # PY2 hack: should use nonlocal
    div_is_ambiguous = [PY2]

    @ASTAnalyser.on_ImportFrom.connect_via(analyser)
    def check_for_division_import(analyser, node):
        if node.module == u'__future__':
            if any(alias.name == u'division' for alias in node.names):
                div_is_ambiguous[0] = False

    @ASTAnalyser.on_BinOp.connect_via(analyser)
    def check_binop(analyser, node):
        if isinstance(node.op, ast.Div) and div_is_ambiguous[0]:
            analyser.emit(
                DivStatement,
                u'Don\'t use / without from __future__ import division. Use '
                u'//, if you really want floor division.',
                node
            )
