# coding: utf-8
"""
    pyalysis.analysers.cst
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import codecs
from lib2to3 import pygram, pytree
from lib2to3.refactor import _detect_future_features
from lib2to3.pgen2.driver import Driver
from lib2to3.pgen2.token import tok_name as TOKEN_NAMES

from blinker import Signal

from pyalysis.warnings import ExtraneousWhitespace
from pyalysis.utils import detect_encoding
from pyalysis._compat import with_metaclass


SYMBOL_NAMES = {
    value: name for name, value in pygram.python_symbols.__dict__.items()
    if type(value) == int
}

NODE_NAMES = {}
NODE_NAMES.update(TOKEN_NAMES)
NODE_NAMES.update(SYMBOL_NAMES)


class _Namespace(object):
    pass


nodes = _Namespace()
nodes.__dict__.update({name: value for value, name in NODE_NAMES.items()})


def parse(file):
    encoding = detect_encoding(file)
    file = codecs.lookup(encoding).streamreader(file)
    source = file.read()
    source += u'\n' # necessary to fix weird parsing error
    features = _detect_future_features(source)
    if u'print_function' in features:
        grammar = pygram.python_grammar_no_print_statement
    else:
        grammar = pygram.python_grammar
    driver = Driver(grammar, convert=pytree.convert)
    return driver.parse_string(source)


class CSTAnalyserMeta(type):
    def __init__(self, name, bases, attributes):
        type.__init__(self, name, bases, attributes)
        for name in NODE_NAMES.values():
            setattr(self, 'on_' + name, Signal())


class CSTAnalyser(with_metaclass(CSTAnalyserMeta)):
    """
    CST-level analyser of Python source code.
    """
    on_analyse = Signal()

    def __init__(self, module):
        self.module = module

        self.cst = parse(module)
        self.warnings = []

    def emit(self, warning_cls, message, node):
        self.warnings.append(
            warning_cls(message, self.module.name, node.get_lineno())
        )

    def analyse(self):
        self.warnings = []
        for node in self.cst.post_order():
            type_name = NODE_NAMES[node.type]
            signal_name = 'on_' + type_name
            signal = getattr(self, signal_name)
            signal.send(self, node=node)
        return self.warnings


@CSTAnalyser.on_atom.connect
def check_extraneous_whitespace_inside_list(analyser, node):
    is_empty_list = (
        len(node.children) == 2 and
        node.children[0].type == nodes.LSQB and
        node.children[1].type == nodes.RSQB
    )
    is_nonempty_list = (
        len(node.children) == 3 and
        node.children[0].type == nodes.LSQB and
        node.children[2].type == nodes.RSQB
    )
    if is_empty_list:
        if node.children[1].prefix and u'\n' not in node.children[1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace in empty list.',
                node
            )
    if is_nonempty_list:
        if node.children[1].prefix and u'\n' not in node.children[1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at the beginning of a list.',
                node
            )
        if node.children[-1].prefix and u'\n' not in node.children[-1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at the end of a list.',
                node
            )
        if node.children[1].type == nodes.listmaker:
            for node in node.children[1].children:
                if node.type == nodes.COMMA and node.prefix:
                    analyser.emit(
                        ExtraneousWhitespace,
                        u'Extraneous whitespace before comma in list.',
                        node
                    )


@CSTAnalyser.on_power.connect
def check_extraneous_whitespace_slicing_or_indexing(analyser, node):
    is_slicing_or_indexing = (
        len(node.children) == 2 and
        node.children[1].type == nodes.trailer and
        node.children[1].children[0].type == nodes.LSQB and
        node.children[1].children[-1].type == nodes.RSQB
    )
    if is_slicing_or_indexing:
        slicing_or_indexing = node.children[1]
        if slicing_or_indexing.children[1].type == nodes.subscript:
            if slicing_or_indexing.children[1].prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    u'Extraneous whitespace at the beginning of slicing.',
                    node
                )
            if slicing_or_indexing.children[-1].prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    u'Extraneous whitespace at the end of slicing.',
                    node
                )
        else:
            if slicing_or_indexing.prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    u'Extraneous whitespace before slicing or indexing.',
                    node
                )
            if slicing_or_indexing.children[1].prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    (
                        u'Extraneous whitespace at the beginning of slicing '
                        u'or indexing.'
                    ),
                    node
                )
            if slicing_or_indexing.children[-1].prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    (
                        u'Extraneous whitespace at the end of slicing or '
                        u'indexing.'
                    ),
                    node
                )


@CSTAnalyser.on_atom.connect
def check_extraneous_whitespace_inside_dict(analyser, node):
    is_empty_dict = (
        len(node.children) == 2 and
        node.children[0].type == nodes.LBRACE and
        node.children[1].type == nodes.RBRACE
    )
    is_nonempty_dict = (
        len(node.children) == 3 and
        node.children[0].type == nodes.LBRACE and
        node.children[1].type == nodes.dictsetmaker and
        node.children[2].type == nodes.RBRACE and
        any(n.type == nodes.COLON for n in node.children[1].children)
    )
    if is_empty_dict:
        if node.children[1].prefix and u'\n' not in node.children[1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace in empty dict.',
                node
            )
    if is_nonempty_dict:
        if node.children[1].prefix and u'\n' not in node.children[1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at beginning of dict.',
                node
            )
        if node.children[-1].prefix and u'\n' not in node.children[-1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at end of dict.',
                node
            )
        for child in node.children[1].children:
            if child.type == nodes.COLON and child.prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    u'Extraneous whitespace before colon in dict.',
                    node
                )


@CSTAnalyser.on_atom.connect
def check_extraneous_whitespace_inside_set(analyser, node):
    is_single_element_set = (
        len(node.children) == 3 and
        node.children[0].type == nodes.LBRACE and
        node.children[1].type != nodes.dictsetmaker and
        node.children[2].type == nodes.RBRACE
    )
    is_multiple_element_set = (
        len(node.children) == 3 and
        node.children[0].type == nodes.LBRACE and
        node.children[1].type == nodes.dictsetmaker and
        node.children[2].type == nodes.RBRACE and
        any(n.type == nodes.COMMA for n in node.children[1].children)
    )
    if is_single_element_set or is_multiple_element_set:
        if node.children[1].prefix and u'\n' not in node.children[1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at beginning of set.',
                node
            )
        if node.children[-1].prefix and u'\n' not in node.children[-1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at end of set.',
                node
            )
        for child in node.children[1].children:
            if child.type == nodes.COMMA and child.prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    u'Extraneous whitespace before comma in set.',
                    node
                )


@CSTAnalyser.on_atom.connect
def check_extraneous_whitespace_inside_tuple(analyser, node):
    is_tuple = (
        len(node.children) == 3 and
        node.children[0].type == nodes.LPAR and
        node.children[1].type == nodes.testlist_gexp and
        node.children[2].type == nodes.RPAR
    )
    if is_tuple:
        if node.children[1].prefix and u'\n' not in node.children[1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at beginning of tuple.',
                node
            )
        if node.children[-1].prefix and u'\n' not in node.children[-1].prefix:
            analyser.emit(
                ExtraneousWhitespace,
                u'Extraneous whitespace at end of tuple.',
                node
            )
        for child in node.children[1].children:
            if child.type == nodes.COMMA and child.prefix:
                analyser.emit(
                    ExtraneousWhitespace,
                    u'Extraneous whitespace before comma in tuple.',
                    node
                )
