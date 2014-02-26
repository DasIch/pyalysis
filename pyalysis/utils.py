# coding: utf-8
"""
    pyalysis.utils
    ~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
    :license: BSD, see LICENSE.rst for details
"""
import math
import re
import codecs
import tokenize
from collections import namedtuple
from weakref import WeakKeyDictionary
from contextlib import contextmanager

from pyalysis._compat import PY2


# as defined in PEP 263
_magic_encoding_comment = re.compile("coding[:=]\s*([-\w.]+)")


if PY2:
    def detect_encoding(file):
        encoding = 'utf-8'
        bom_found = False
        possible_bom = file.read(len(codecs.BOM_UTF8))
        if possible_bom == codecs.BOM_UTF8:
            encoding = 'utf-8-sig'
            bom_found = True
        file.seek(0)
        first = file.readline()
        match = _magic_encoding_comment.search(first)
        if match is None:
            second = file.readline()
            match = _magic_encoding_comment.search(second)
            if match is not None:
                encoding = match.group(1)
        else:
            encoding = match.group(1)
        if bom_found:
            if encoding == 'utf-8' or encoding == 'utf-8-sig':
                encoding = 'utf-8-sig'
            else:
                raise SyntaxError(
                    'Found utf8 BOM in conflict with encoding declaration'
                )
        file.seek(0)
        return encoding
else:
    def detect_encoding(file):
        try:
            encoding = tokenize.detect_encoding(file.readline)[0]
        finally:
            file.seek(0)
        return encoding

detect_encoding.__doc__ = """
Returns the encoding of a Python module given as a file-like object in binary
mode.

If a utf-8 BOM (byte-order mark) is found along with an encoding declaration
that defines an encoding other than utf-8, a :exc:`SyntaxError` is raised.
"""


class classproperty(object):
    """
    Like :func:`property` but acts as a class instead of an instance attribute.
    """
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        return self.fget(owner)


def iter_subclasses(cls):
    """
    Returns all subclasses of `cls` in postorder.
    """
    for subclass in cls.__subclasses__():
        for subsubclass in iter_subclasses(subclass):
            yield subsubclass
    yield cls


def count_digits(n):
    """
    Returns the number of digits in the given integer `n`.
    """
    return int(math.floor(math.log10(n))) + 1


Location = namedtuple('Location', ['line', 'column'])


class PerClassAttribute(object):
    """
    A descriptor for per-class class attributes. The descriptor will create a
    new attribute by calling `attribute_factory` for each class on which it is
    accessed.

    As with normal class attributes, class attributes defined with this
    descriptor can be overridden in instances.

    This descriptor is useful, if you want to define a class attribute you do
    not want subclasses to identically inherit::

        class SuperClass(object):
            foo = PerClassAttribute(object)

        class Child(SuperClass):
            pass

        assert SuperClass.foo is not Child.foo
    """
    def __init__(self, attribute_factory):
        self.attribute_factory = attribute_factory

        self.class2attribute = WeakKeyDictionary()
        self.instance2attribute = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance in self.instance2attribute:
            return self.instance2attribute[instance]
        if owner not in self.class2attribute:
            self.class2attribute[owner] = self.attribute_factory()
        return self.class2attribute[owner]

    def __set__(self, instance, attribute):
        self.instance2attribute[instance] = attribute

    def __delete__(self, instance):
        del self.instance2attribute[instance]


@contextmanager
def retain_file_position(file, position=0):
    """
    A contextmanager to temporarily seek the given `file` to `position`.
    """
    old_position = file.tell()
    file.seek(position)
    try:
        yield
    finally:
        file.seek(old_position)
