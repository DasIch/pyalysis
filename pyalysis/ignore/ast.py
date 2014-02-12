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

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return (
            parent_equal and
            self.filename == other.filename and
            self.filters == other.filters
        )


class Filter(Node):
    def __init__(self, name, expressions, start, end):
        Node.__init__(self, start, end)
        self.name = name
        self.expressions = expressions

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return (
            parent_equal and
            self.name == other.name and
            self.expressions == other.expressions
        )


class Name(Node):
    def __init__(self, name, start, end):
        Node.__init__(self, start, end)
        self.name = name

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return parent_equal and self.name == other.name


class Literal(Node):
    def __init__(self, value, start, end):
        Node.__init__(self, start, end)
        self.value = value

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return parent_equal and self.value == other.value


class String(Literal):
    pass


class Integer(Literal):
    pass


class BinaryOperation(Node):
    def __init__(self, left, right, start, end):
        Node.__init__(self, start, end)
        self.left = left
        self.right = right

    @property
    def name(self):
        if isinstance(self.left, Name):
            return self.left
        elif isinstance(self.right, Name):
            return self.right

    @property
    def literal(self):
        if isinstance(self.left, Name) and isinstance(self.right, Name):
            return None
        if isinstance(self.left, Name):
            return self.right
        return self.left

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return (
            parent_equal and
            self.left == other.left and
            self.right == other.right
        )


class Equal(BinaryOperation):
    pass


class LessThan(BinaryOperation):
    pass


class GreaterThan(BinaryOperation):
    pass


class LessOrEqualThan(BinaryOperation):
    pass
