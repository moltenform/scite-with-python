# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

import sys

class Bucket(object):
    "simple named-tuple; o.field looks nicer than o['field']. "
    def __init__(self, **kwargs):
        for key in kwargs:
            object.__setattr__(self, key, kwargs[key])

    def __repr__(self):
        return '\n\n\n'.join(('%s=%s'%(ustr(key), ustr(self.__dict__[key])) for key in sorted(self.__dict__)))
            
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
    if not isPy3OrNewer:
        if not isinstance(s, unicode):
            return str(s)

        import unicodedata
        s = unicodedata.normalize('NFKD', s)
        if okToIgnore:
            return s.encode('ascii', 'ignore')
        else:
            return s.encode('ascii', 'replace')
    else:
        if isinstance(s, bytes):
            return s.decode('ascii')
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
        .replace(u'"', u"'").replace(u'<', u'[').replace(u'>', u']') \
        .replace(u'\r\n', u' ').replace(u'\r', u' ').replace(u'\n', u' ')
        
def getRandomString(max=100 * 1000):
    import random
    return '%s' % random.randrange(max)

def genGuid(asBase64=False):
    import uuid
    u = uuid.uuid4()
    if asBase64:
        import base64
        b = base64.urlsafe_b64encode(u.bytes_le)
        return b.decode('utf8')
    else:
        return str(u)

# "millistime" is number of milliseconds past epoch (unix time * 1000)
def renderMillisTime(millisTime):
    t = millisTime / 1000.0
    import time
    return time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(t))

def getNowAsMillisTime():
    import time
    t = time.time()
    return int(t * 1000)

def splice(s, insertionpoint, lenToDelete, newtext):
    return s[0:insertionpoint] + newtext + s[insertionpoint + lenToDelete:]

def spliceSpan(s, span, newtext):
    assertTrue(span[1] >= span[0])
    assertEq(len(span), 2)
    return splice(s, span[0], span[1] - span[0], newtext)

def stripHtmlTags(s, removeRepeatedWhitespace=True):
    import re
    # a (?:) is a non-capturing group
    reTags = re.compile(r'<[^>]+(?:>|$)', re.DOTALL)
    s = reTags.sub(' ', s)
    if removeRepeatedWhitespace:
        regNoDblSpace = re.compile(r'\s+')
        s = regNoDblSpace.sub(' ', s)
        s = s.strip()

    # malformed tags like "<a<" with no close, replace with ?
    s = s.replace('<', '?').replace('>', '?')
    return s


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

def truncateWithEllipsis(s, maxLength):
    if len(s) <= maxLength:
        return s
    else:
        ellipsis = '...'
        if maxLength < len(ellipsis):
            return s[0:maxLength]
        else:
            return s[0:maxLength - len(ellipsis)] + ellipsis

def formatSize(n):
    if n >= 1024 * 1024 * 1024:
        return '%.2fGB' % (n / (1024.0 * 1024.0 * 1024.0))
    elif n >= 1024 * 1024:
        return '%.2fMB' % (n / (1024.0 * 1024.0))
    elif n >= 1024:
        return '%.2fKB' % (n / (1024.0))
    else:
        return '%db' % n

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
            if len(self.batch):
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
        except ValueError:
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

class ParsePlus(object):
    '''
    ParsePlus, by Ben Fisher 2019
    
    Adds the following features to the "parse" module:
        {s:NoNewlines} field type
        {s:NoSpaces} works like {s:S}
        remember that "{s} and {s}" matches "a and a" but not "a and b",
            use "{s1} and {s2}" or "{} and {}" if the contents can differ
        escapeSequences such as backslash-escapes (see examples in tests)
        replaceFieldWithText (see examples in tests)
        getTotalSpan
    '''
    def __init__(self, pattern, extra_types=None, escapeSequences=None,
            case_sensitive=True):
        try:
            import parse
        except:
            raise ImportError('needs "parse", https://pypi.org/project/parse/')
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.extra_types = extra_types if extra_types else {}
        self.escapeSequences = escapeSequences if escapeSequences else []
        if 'NoNewlines' in pattern:
            @parse.with_pattern(r'[^\r\n]+')
            def parse_NoNewlines(s):
                return str(s)
            self.extra_types['NoNewlines'] = parse_NoNewlines
        if 'NoSpaces' in pattern:
            @parse.with_pattern(r'[^\r\n\t ]+')
            def parse_NoSpaces(s):
                return str(s)
            self.extra_types['NoSpaces'] = parse_NoSpaces

    def _createEscapeSequencesMap(self, s):
        self._escapeSequencesMap = {}
        if len(self.escapeSequences) > 5:
            raise ValueError('we support a max of 5 escape sequences')
    
        sTransformed = s
        for i, seq in enumerate(self.escapeSequences):
            assertTrue(len(seq) > 1, "an escape-sequence only makes sense if " +
                "it is at least two characters")
            
            # use rarely-occurring ascii chars like
            # \x01 (start of heading)
            rareChar = chr(i + 1)
            # raise error if there's any occurance of rareChar, not repl,
            # otherwise we would have incorrect expansions
            if rareChar in s:
                raise RuntimeError("we don't yet support escape sequences " +
                "if the input string contains rare ascii characters. the " +
                "input string contains " + rareChar + ' (ascii ' +
                str(ord(rareChar)) + ')')
            # replacement string is the same length, so offsets aren't affected
            repl = rareChar * len(seq)
            self._escapeSequencesMap[repl] = seq
            sTransformed = sTransformed.replace(seq, repl)
            
        assertEq(len(s), len(sTransformed), 'internal error: len(s) changed.')
        return sTransformed

    def _unreplaceEscapeSequences(self, s):
        for key in self._escapeSequencesMap:
            s = s.replace(key, self._escapeSequencesMap[key])
        return s

    def _resultToMyResult(self, parseResult, s):
        if not parseResult:
            return parseResult
        ret = Bucket()
        lenS = len(s)
        for name in parseResult.named:
            val = self._unreplaceEscapeSequences(parseResult.named[name])
            setattr(ret, name, val)
        ret.spans = parseResult.spans
        ret.getTotalSpan = lambda: self._getTotalSpan(parseResult, lenS)
        return ret

    def _getTotalSpan(self, parseResult, lenS):
        if '{{' in self.pattern or '}}' in self.pattern:
            raise RuntimeError("for simplicity, we don't yet support getTotalSpan " +
                "if the pattern contains {{ or }}")
        locationOfFirstOpen = self.pattern.find('{')
        locationOfLastClose = self.pattern.rfind('}')
        if locationOfFirstOpen == -1 or locationOfLastClose == -1:
            # pattern contained no fields?
            return None
        
        if not len(parseResult.spans):
            # pattern contained no fields?
            return None
        smallestSpanStart = float('inf')
        largestSpanEnd = -1
        for key in parseResult.spans:
            lower, upper = parseResult.spans[key]
            smallestSpanStart = min(smallestSpanStart, lower)
            largestSpanEnd = max(largestSpanEnd, upper)
        
        # ex.: for the pattern aaa{field}bbb, widen by len('aaa') and len('bbb')
        smallestSpanStart -= locationOfFirstOpen
        largestSpanEnd += len(self.pattern) - (locationOfLastClose + len('}'))
        
        # sanity check that the bounds make sense
        assertTrue(0 <= smallestSpanStart <= lenS,
            'internal error: span outside bounds')
        assertTrue(0 <= largestSpanEnd <= lenS,
            'internal error: span outside bounds')
        assertTrue(largestSpanEnd >= smallestSpanStart,
            'internal error: invalid span')
        return (smallestSpanStart, largestSpanEnd)
    
    def match(self, s):
        # entire string must match
        import parse
        sTransformed = self._createEscapeSequencesMap(s)
        parseResult = parse.parse(self.pattern, sTransformed,
            extra_types=self.extra_types, case_sensitive=self.case_sensitive)
        return self._resultToMyResult(parseResult, s)

    def search(self, s):
        import parse
        sTransformed = self._createEscapeSequencesMap(s)
        parseResult = parse.search(self.pattern, sTransformed,
            extra_types=self.extra_types, case_sensitive=self.case_sensitive)
        return self._resultToMyResult(parseResult, s)

    def findall(self, s):
        import parse
        sTransformed = self._createEscapeSequencesMap(s)
        parseResults = parse.findall(self.pattern, sTransformed,
            extra_types=self.extra_types, case_sensitive=self.case_sensitive)
        for parseResult in parseResults:
            yield self._resultToMyResult(parseResult, s)

    def replaceFieldWithText(self, s, key, newValue,
            appendIfNotFound=None, allowOnlyOnce=False):
        # example: <title>{title}</title>
        results = list(self.findall(s))
        if allowOnlyOnce and len(results) > 1:
            raise RuntimeError('we were told to allow pattern only once.')
        if len(results):
            span = results[0].spans[key]
            return spliceSpan(s, span, newValue)
        else:
            if appendIfNotFound is None:
                raise RuntimeError("pattern not found.")
            else:
                return s + appendIfNotFound
    
    def replaceFieldWithTextIntoFile(self, path, key, newValue,
            appendIfNotFound=None, allowOnlyOnce=False, encoding=None):
        from .files import readall, writeall
        s = readall(path, encoding=encoding)

        newS = self.replaceFieldWithText(s, key, newValue,
            appendIfNotFound=appendIfNotFound,
            allowOnlyOnce=allowOnlyOnce)
        
        writeall(path, newS, 'w', encoding=encoding)

def DBG(obj=None):
    import pprint
    if obj is None:
        import inspect
        fback = inspect.currentframe().f_back
        framelocals = fback.f_locals
        newDict = {}
        for key in framelocals:
            if not callable(framelocals[key]) and not \
                    inspect.isclass(framelocals[key]) and not \
                    inspect.ismodule(framelocals[key]):
                newDict[key] = framelocals[key]
        pprint.pprint(newDict)
    else:
        pprint.pprint(obj)

def runAndCatchException(fn):
    try:
        fn()
    except:
        import sys
        return sys.exc_info()[1]
    return None

def downloadUrl(url, toFile=None, timeout=30, asText=False):
    import requests
    resp = requests.get(url, timeout=timeout)
    if toFile:
        with open(toFile, 'wb') as fout:
            fout.write(resp.content)
    if asText:
        return resp.text
    else:
        return resp.content

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


# Python 2/3 compat, inspired by mutagen/_compat.py

if sys.version_info[0] <= 2:
    from StringIO import StringIO
    BytesIO = StringIO
    from cStringIO import StringIO as cBytesIO
    from itertools import izip  # noqa: F401
    
    def endswith(a, b):
        return a.endswith(b)
    
    def startswith(a, b):
        return a.startswith(b)
    
    def iterbytes(b):
        return iter(b)
    
    def bytes_to_string(b):
        return b
    
    def asbytes(s):
        return s
    
    rinput = raw_input
    ustr = unicode
    uchr = unichr
    anystringtype = basestring
    bytetype = str
    xrange = xrange
    isPy3OrNewer = False
else:
    from io import StringIO
    StringIO = StringIO
    from io import BytesIO
    cBytesIO = BytesIO
    
    def endswith(a, b):
        # use with either str or bytes
        if isinstance(a, str):
            if not isinstance(b, str):
                b = b.decode("ascii")
        else:
            if not isinstance(b, bytes):
                b = b.encode("ascii")
        return a.endswith(b)
    
    def startswith(a, b):
        # use with either str or bytes
        if isinstance(a, str):
            if not isinstance(b, str):
                b = b.decode("ascii")
        else:
            if not isinstance(b, bytes):
                b = b.encode("ascii")
        return a.startswith(b)
    
    def iterbytes(b):
        return (bytes([v]) for v in b)
    
    def bytes_to_string(b):
        return b.decode('utf-8')
    
    def asbytes(s, encoding='ascii'):
        return bytes(s, encoding)
    
    rinput = input
    ustr = str
    uchr = chr
    anystringtype = str
    bytetype = bytes
    xrange = range
    isPy3OrNewer = True
