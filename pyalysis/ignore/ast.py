# coding: utf-8
"""
    pyalysis.ignore.ast
    ~~~~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""


class Node(object):
    """
    Represents a node in the ast.
    """
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
    """
    Represents an ignore file.

    :param filename: The name of the file being represented.
    :param filters: A list of :class:`Filter` instances.
    """
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
    """
    Represents a filter for some type of warning.

    :param name: The name of the type of warnings being filtered.
    :param expressions: A list of :class:`Expression` instances.
    """
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
    """
    Represents a name.
    """
    def __init__(self, name, start, end):
        Node.__init__(self, start, end)
        self.name = name

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return parent_equal and self.name == other.name


class Literal(Node):
    """
    Represents a literal.
    """
    def __init__(self, value, start, end):
        Node.__init__(self, start, end)
        self.value = value

    def __eq__(self, other):
        parent_equal = Node.__eq__(self, other)
        if parent_equal is NotImplemented:
            return NotImplemented
        return parent_equal and self.value == other.value


class String(Literal):
    """
    Represents a string.
    """


class Integer(Literal):
    """
    Represents an integer.
    """


class Expression(Node):
    """
    Represents an expression.
    """


class BinaryOperation(Expression):
    """
    Represents a binary operation.

    :param left: A :class:`Name` or :class:`Literal`.
    :param right: A :class:`Name` or :class:`Literal`.
    """
    def __init__(self, left, right, start, end):
        Node.__init__(self, start, end)
        self.left = left
        self.right = right

    @property
    def name(self):
        """
        Returns the side of the operation that is the :class:`Name` instance
        or `None`.
        """
        if isinstance(self.left, Name):
            return self.left
        elif isinstance(self.right, Name):
            return self.right

    @property
    def literal(self):
        """
        Returns the side of the operation that is the :class:`Literal` instance
        or `None`.
        """
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
    """
    Represents an equal ``=`` operation.
    """


class LessThan(BinaryOperation):
    """
    Represents a less than ``<`` operation.
    """


class GreaterThan(BinaryOperation):
    """
    Represents a greater than ``>`` operation.
    """


class LessOrEqualThan(BinaryOperation):
    """
    Represents a less or equal than ``<=`` operation.
    """


class GreaterOrEqualThan(BinaryOperation):
    """
    Represents a greater or equal than ``>=`` operation.
    """
