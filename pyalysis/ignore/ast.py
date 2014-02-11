# coding: utf-8
"""
    pyalysis.ignore.ast
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""


class Node(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.start == other.start and self.end == other.end
        return NotImplemented

    def __ne__(self, other):
        is_equal = self == other
        if is_equal is NotImplemented:
            return NotImplemented
        return not is_equal

    __hash__ = None


class IgnoreFile(Node):
    def __init__(self, filename, filters):
        self.filename = filename
        self.filters = filters

    @property
    def start(self):
        if self.filters:
            return self.filters[0].start

    @property
    def end(self):
        if self.filters:
            return self.filters[-1].end


class Filter(Node):
    def __init__(self, name, start, end):
        Node.__init__(self, start, end)
        self.name = name

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return parent_equal and self.name == other.name
