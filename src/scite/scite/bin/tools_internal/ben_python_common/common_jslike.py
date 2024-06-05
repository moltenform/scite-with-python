# BenPythonCommon,
# 2020 Ben Fisher, released under the LGPLv3 license.

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

from .common_util import *

# array methods

def concat(ar1, ar2):
    # like extend, but operates on a copy
    ar = list(ar1)
    ar.extend(ar2)
    return ar

def every(lst, fn):
    # true if the condition holds for all items, will exit early
    return builtins.all(builtins.map(fn, lst))

def some(lst, fn):
    # true if fn called on any element returns true, exits early
    return builtins.any(builtins.map(fn, lst))

def filter(lst, fn):
    # return a list with items where the condition holds
    return [item for item in lst if fn(item)]

def find(lst, fn):
    # returns the value in a list where fn returns true, or None
    ind = findIndex(lst, fn)
    return lst[ind] if ind != -1 else None

def findIndex(lst, fn):
    # returns the position in a list where fn returns true, or None
    for i, val in enumerate(lst):
        if fn(val):
            return i
    return -1

def indexOf(lst, valToFind):
    # search for a value and return first position where seen, or -1
    for i, val in enumerate(lst):
        if val == valToFind:
            return i
    return -1

def lastIndexOf(lst, valToFind):
    # search for a value and return last position where seen, or -1
    i = len(lst) - 1
    while i >= 0:
        if lst[i] == valToFind:
            return i
        i -= 1
    return -1

def map(lst, fn):
    # return a list with fn called on each item
    return list(builtins.map(fn, lst))

def times(n, fn):
    # return a list with n items, values from calling fn
    return [fn() for _ in range(n)]


notProvided = object()

def reduce(lst, fn, initialVal=notProvided):
    # callback should have 2 parameters
    import functools
    if initialVal == notProvided:
        return functools.reduce(fn, lst)
    else:
        return functools.reduce(fn, lst, initialVal)

# string manipulation

def splice(s, insertionPoint, lenToDelete=0, newText=''):
    # like javascript's splice
    return s[0:insertionPoint] + newText + s[insertionPoint + lenToDelete:]

def spliceSpan(s, span, newText):
    # provide a span [startIndex, stopIndex] to be replaced with newText
    assertEq(2, len(span), 'expected [startIndex, stopIndex]')
    assertTrue(span[1] >= span[0])
    return splice(s, span[0], span[1] - span[0], newText)

# object/dict methods

def merged(d1, d2):
    # like update, but does not operate in-place
    d1copy = d1.copy()
    d1copy.update(d2)
    return d1copy

# type conversions

def floatOrNone(s):
    try:
        return float(s)
    except:
        return None

def intOrNone(s):
    try:
        return int(s)
    except:
        return None
