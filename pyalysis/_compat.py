# coding: utf-8
"""
    pyalysis._compat
    ~~~~~~~~~~~~~~~~

    :copyright: 2014 by Daniel Neuhäuser and Contributors
"""
import sys
import codecs
try:
    import __pypy__
    PYPY = True
except ImportError:
    PYPY = False


PY2 = sys.version_info[0] == 2


if PY2:
    text_type = unicode

    def implements_iterator(cls):
        cls.next = cls.__next__
        del cls.__next__
        return cls

    stdout = codecs.lookup(
        sys.stdout.encoding or 'utf-8'
    ).streamwriter(sys.stdout)

else:
    text_type = str

    def implements_iterator(cls):
        return cls

    stdout = sys.stdout


# copied from Flask: flask/_compat.py
#                    copyright 2014 by Armin Ronacher
#                    licensed under BSD
#
def with_metaclass(meta, *bases):
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass. Because of internal type checks
    # we also need to make sure that we downgrade the custom metaclass
    # for one level to something closer to type (that's why __call__ and
    # __init__ comes back from type etc.).
    #
    # This has the advantage over six.with_metaclass in that it does not
    # introduce dummy classes into the final MRO.
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})
