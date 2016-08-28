# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

class Bucket(object):
    "simple named-tuple; o.field looks nicer than o['field']. "
    def __init__(self, **kwargs):
        for key in kwargs:
            object.__setattr__(self, key, kwargs[key])

    def __repr__(self):
        return '\n\n\n'.join(('%s=%s'%(unicodestringtype(key), unicodestringtype(self.__dict__[key])) for key in sorted(self.__dict__)))
            
class SimpleEnum(object):
    "simple enum; prevents modification after creation."
    _set = None

    def __init__(self, listStart):
        self._set = set(listStart)

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        elif name in self._set:
            return name
        else:
            raise AttributeError

    def __setattribute__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            raise RuntimeError

    def __delattr__(self, name):
        raise RuntimeError
    
def getPrintable(s, okToIgnore=False):
    if sys.version_info[0] <= 2:
        if not isinstance(s, unicode):
            return str(s)

        import unicodedata
        s = unicodedata.normalize('NFKD', s)
        if okToIgnore:
            return s.encode('ascii', 'ignore')
        else:
            return s.encode('ascii', 'replace')
    else:
        if not isinstance(s, str):
            return str(s)

        import unicodedata
        s = unicodedata.normalize('NFKD', s)
        if okToIgnore:
            return s.encode('ascii', 'ignore').decode('ascii')
        else:
            return s.encode('ascii', 'replace').decode('ascii')
        
def trace(*args):
    print(' '.join(map(getPrintable, args)))
        
def safefilename(s):
    return s.replace(u'\u2019', u"'").replace(u'?', u'').replace(u'!', u'') \
        .replace(u'\\ ', u', ').replace(u'\\', u'-') \
        .replace(u'/ ', u', ').replace(u'/', u'-') \
        .replace(u': ', u', ').replace(u':', u'-') \
        .replace(u'| ', u', ').replace(u'|', u'-') \
        .replace(u'*', u'') \
        .replace(u'"', u"'").replace(u'<', u'[').replace(u'>', u']')
        
def getRandomString():
    import random
    return '%s' % random.randrange(99999)
        
def warnWithOptionToContinue(s):
    import common_ui
    trace('WARNING ' + s)
    if not common_ui.getInputBool('continue?'):
        raise RuntimeError()

'''
re.search(pattern, string, flags=0)
    look for at most one match starting anywhere
re.match(pattern, string, flags=0)
    look for match starting only at beginning of string
re.findall(pattern, string, flags=0)
    returns list of strings
re.finditer(pattern, string, flags=0)
    returns iterator of match objects
    
re.IGNORECASE, re.MULTILINE, re.DOTALL
'''

def re_replacewholeword(starget, sin, srep):
    import re
    sin = '\\b' + re.escape(sin) + '\\b'
    return re.sub(sin, srep, starget)

def re_replace(starget, sre, srep):
    import re
    return re.sub(sre, srep, starget)

def getClipboardTextTk():
    from Tkinter import Tk
    try:
        r = Tk()
        r.withdraw()
        s = r.clipboard_get()
    except BaseException as e:
        if 'selection doesn\'t exist' in str(e):
            s = ''
        else:
            raise
    finally:
        r.destroy()
    return s

def setClipboardTextTk(s):
    from Tkinter import Tk
    text = unicode(s)
    try:
        r = Tk()
        r.withdraw()
        r.clipboard_clear()
        r.clipboard_append(text)
    finally:
        r.destroy()

def getClipboardTextPyperclip():
    import pyperclip
    return pyperclip.paste()

def setClipboardTextPyperclip(s):
    import pyperclip
    pyperclip.copy(s)
    
def getClipboardText():
    try:
        return getClipboardTextPyperclip()
    except ImportError:
        return getClipboardTextTk()
    
def setClipboardText(s):
    try:
        setClipboardTextPyperclip(s)
    except ImportError:
        setClipboardTextTk(s)

def takeBatchOnArbitraryIterable(iterable, size):
    import itertools
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))

def takeBatch(l, n):
    """ Yield successive n-sized chunks from l."""
    return list(takeBatchOnArbitraryIterable(l, n))
    
class TakeBatch(object):
    def __init__(self, batchSize, callback):
        self.batch = []
        self.batchSize = batchSize
        self.callback = callback

    def append(self, item):
        self.batch.append(item)
        if len(self.batch) >= self.batchSize:
            self.callback(self.batch)
            self.batch = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # if exiting normally (not by exception), run the callback
        if not exc_type:
            self.callback(self.batch)

class RecentlyUsedList(object):
    '''Keep a list of items without storing duplicates'''
    def __init__(self, maxSize=None, startList=None):
        self.list = startList or []
        self.maxSize = maxSize
    
    def getList(self):
        return self.list
        
    def indexOf(self, s):
        try:
            return self.list.index(s)
        except:
            return -1
    
    def add(self, s):
        # if it's also elsewhere in the list, remove that one
        index = self.indexOf(s)
        if index != -1:
            self.list.pop(index)
        
        # insert new entry at the top
        self.list.insert(0, s)

        # if we've reached the limit, cut out the extra ones
        if self.maxSize:
            while len(self.list) > self.maxSize:
                self.list.pop()

def startThread(fn, args=None):
    import threading
    if args is None:
        args = tuple()
    t = threading.Thread(target=fn, args=args)
    t.start()
    
# inspired by http://code.activestate.com/recipes/496879-memoize-decorator-function-with-cache-size-limit/
def BoundedMemoize(fn):
    if sys.version_info[0] > 2:
        raise NotImplementedError('not supported in python 3+')
    
    from collections import OrderedDict
    cache = OrderedDict()

    def memoize_wrapper(*args, **kwargs):
        try:
            import cPickle as pickle
        except ImportError:
            import pickle
        key = pickle.dumps((args, kwargs))
        try:
            return cache[key]
        except KeyError:
            result = fn(*args, **kwargs)
            cache[key] = result
            if len(cache) > memoize_wrapper._limit:
                cache.popitem(False)  # the false means remove as FIFO
            return result

    memoize_wrapper._limit = 20
    memoize_wrapper._cache = cache
    memoize_wrapper.func_name = fn.func_name
    return memoize_wrapper
    
def DBG(obj=None):
    import pprint
    if obj is None:
        import inspect
        fback = inspect.currentframe().f_back
        framelocals = fback.f_locals
        newDict = {}
        for key in framelocals:
            if not callable(framelocals[key]) and not inspect.isclass(framelocals[key]) and not inspect.ismodule(framelocals[key]):
                newDict[key] = framelocals[key]
        pprint.pprint(newDict)
    else:
        pprint.pprint(obj)
            
def assertTrue(condition, *messageArgs):
    if not condition:
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        raise AssertionError(msg)
    
def assertEq(expected, received, *messageArgs):
    if expected != received:
        import pprint
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        msg += '\nassertion failed, expected:\n'
        msg += getPrintable(pprint.pformat(expected))
        msg += '\nbut got:\n'
        msg += getPrintable(pprint.pformat(received))
        raise AssertionError(msg)

def assertFloatEq(expected, received, *messageArgs):
    import math
    precision = 0.000001
    difference = math.fabs(expected - received)
    if difference > precision:
        messageArgs = list(messageArgs) or []
        messageArgs.append('expected %f, got %f, difference of %f' % (
            expected, received, difference))
        assertTrue(False, *messageArgs)

def assertEqArray(expected, received):
    if isinstance(expected, anystringtype):
        expected = expected.split('|')

    assertEq(len(expected), len(received))
    for i in range(len(expected)):
        assertEq(repr(expected[i]), repr(received[i]))

def assertException(fn, excType, excTypeExpectedString=None, msg='', regexp=False):
    import pprint
    import sys
    e = None
    try:
        fn()
    except:
        e = sys.exc_info()[1]
    
    assertTrue(e is not None, 'did not throw ' + msg)
    if excType:
        assertTrue(isinstance(e, excType), 'exception type check failed ' + msg +
            ' \ngot \n' + pprint.pformat(e) + '\n not \n' + pprint.pformat(excType))
    if excTypeExpectedString:
        if regexp:
            import re
            passed = re.search(excTypeExpectedString, str(e))
        else:
            passed = excTypeExpectedString in str(e)
        assertTrue(passed, 'exception string check failed ' + msg +
            '\ngot exception string:\n' + str(e))

import sys
if sys.version_info[0] <= 2:
    unicodestringtype = unicode
    anystringtype = basestring
else:
    unicodestringtype = str
    anystringtype = str

