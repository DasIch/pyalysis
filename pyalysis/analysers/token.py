# coding: utf-8
"""
    pyalysis.analysers.token
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
from __future__ import absolute_import
import token
import tokenize
from collections import namedtuple

from blinker import Signal

from pyalysis.warnings import (
    WrongNumberOfIndentationSpaces, MixedTabsAndSpaces
)
from pyalysis._compat import PY2, with_metaclass


Token = namedtuple('Token', ['type', 'lexeme', 'start', 'end', 'logical_line'])
Location = namedtuple('Location', ['line', 'column'])


class TokenAnalyserMeta(type):
    def __init__(self, name, bases, attributes):
        type.__init__(self, name, bases, attributes)
        for token_name in token.tok_name.values():
            setattr(self, 'on_' + token_name, Signal())


class TokenAnalyser(with_metaclass(TokenAnalyserMeta)):
    """
    Token-level analyser of Python source code.
    """

    on_analyse = Signal()

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
            warning_cls(message, self.module.name, tok.start, tok.end)
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
        self.on_analyse.send(self)
        for tok in self.generate_tokens():
            name = token.tok_name[tok.type]
            signal_name = 'on_' + name
            signal = getattr(self, signal_name)
            signal.send(self, tok=tok)
        return self.warnings


@TokenAnalyser.on_analyse.connect
def analyse_indentation(analyser):
    indentation_stack = []

    @analyser.on_INDENT.connect_via(analyser)
    def analyse_indent(analyser, tok):
        line_indentation = tok.lexeme.count(u'\t') * 8 + tok.lexeme.count(u' ')
        added_indentation = line_indentation - sum(indentation_stack)
        if added_indentation != 4:
            analyser.emit(
                WrongNumberOfIndentationSpaces,
                u'Indented by {0} spaces instead of 4 as demanded by PEP 8'
                        .format(added_indentation),
                tok
            )
        indentation_stack.append(added_indentation)

    @analyser.on_DEDENT.connect_via(analyser)
    def analyse_dedent(analyser, tok):
        # tok.lexeme on DEDENT tokens is always the empty string, therefore we
        # only know that we have to jump back to the previous indentation
        # level. This is why we maintain a stack with each element being the
        # added amount of indentation.
        indentation_stack.pop()


@TokenAnalyser.on_NEWLINE.connect
def analyse_newline(analyser, tok):
    indentation = tok.logical_line[:-len(tok.logical_line.lstrip())]
    if u' ' in indentation and u'\t' in indentation:
        analyser.emit(
            MixedTabsAndSpaces,
            u'Tabs and spaces are mixed. This is disallowed on Python 3 '
            u'and inconsistent. Use either tabs or spaces exclusively, '
            u'preferably spaces.',
            tok
        )
