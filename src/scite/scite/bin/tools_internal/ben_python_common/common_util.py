# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

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
        assertTrue(not isinstance(listStart, anystringtype))
        self._set = set(listStart)

    def __getattribute__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        elif name in self._set:
            return name
        else:
            raise AttributeError

    def __setattr__(self, name, value):
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

def toValidFilename(sOrig, dirsepOk=False, maxLen=None):
    s = sOrig
    if dirsepOk:
        # sometimes we want to leave directory-separator characters in the string.
        import os
        if os.path.sep == '/':
            s = s.replace(u'\\ ', u', ').replace(u'\\', u'-')
        else:
            s = s.replace(u'/ ', u', ').replace(u'/', u'-')
    else:
        s = s.replace(u'\\ ', u', ').replace(u'\\', u'-')
        s = s.replace(u'/ ', u', ').replace(u'/', u'-')

    result = s.replace(u'\u2019', u"'").replace(u'?', u'').replace(u'!', u'') \
        .replace(u': ', u', ').replace(u':', u'-') \
        .replace(u'| ', u', ').replace(u'|', u'-') \
        .replace(u'*', u'') \
        .replace(u'"', u"'").replace(u'<', u'[').replace(u'>', u']') \
        .replace(u'\r\n', u' ').replace(u'\r', u' ').replace(u'\n', u' ')

    if maxLen and len(result) > maxLen:
        import os as _os
        assertTrue(maxLen > 1)
        ext = _os.path.splitext(s)[1]
        beforeExt = s[0:-len(ext)]
        while len(result) > maxLen:
            result = beforeExt + ext
            beforeExt = beforeExt[0:-1]
        # if it ate into the directory, though, through an error
        assertTrue(_os.path.split(sOrig)[0] == _os.path.split(result)[0])

    return result

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

# see also: html.escape, html.unescape

def replaceMustExist(haystack, needle, replace):
    assertTrue(needle in haystack, "not found", needle)
    return haystack.replace(needle, replace)

def reSearchWholeWord(haystack, needle):
    import re
    reNeedle = '\\b' + re.escape(needle) + '\\b'
    return re.search(reNeedle, haystack)

def reReplaceWholeWord(haystack, sNeedle, replace):
    import re
    sNeedle = '\\b' + re.escape(sNeedle) + '\\b'
    return re.sub(sNeedle, replace, haystack)

def reReplace(haystack, reNeedle, replace):
    import re
    return re.sub(reNeedle, replace, haystack)


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

def strToList(s, replaceComments=True):
    lines = s.replace('\r\n', '\n').split('\n')
    if replaceComments:
        lines = [line for line in lines if not line.startswith('#')]
    return [line.strip() for line in lines if line.strip()]

def strToSet(s, replaceComments=True):
    lst = strToList(s, replaceComments=replaceComments)
    return set(lst)

def parseIntOrFallback(s, fallBack=None):
    try:
        return int(s)
    except:
        return fallBack

def addOrAppendToArrayInDict(d, key, val):
    got = d.get(key, None)
    if got:
        got.append(val)
    else:
        d[key] = [val]

def waitUntilTrue(iter, fnWaitUntil):
    if isinstance(iter, list):
        iter = (item for item in iter)

    hasSeen = False
    for value in iter:
        if not hasSeen and fnWaitUntil(value):
            hasSeen = True
        if hasSeen:
            yield value

def takeBatchOnArbitraryIterable(iterable, size):
    import itertools
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))

def takeBatch(itr, n):
    """ Yield successive n-sized chunks from l."""
    return list(takeBatchOnArbitraryIterable(itr, n))

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

# inspired by http://code.activestate.com/recipes/496879-memoize-decorator-function-with-cache-size-limit/
def BoundedMemoize(fn):
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
    if sys.version_info[0] <= 2:
        memoize_wrapper.func_name = fn.func_name
    else:
        memoize_wrapper.__name__ = fn.__name__
    return memoize_wrapper

# "millistime" is number of milliseconds past epoch (unix time * 1000)
def renderMillisTime(millisTime):
    t = millisTime / 1000.0
    import time
    return time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime(t))

def renderMillisTimeStandard(millisTime):
    t = millisTime / 1000.0
    import time
    return time.strftime("%Y-%m-%d %I:%M:%S", time.localtime(t))


class EnglishDateParserWrapper(object):
    def __init__(self, dateOrder='MDY'):
        # default to month-day-year
        # restrict to English, less possibility of accidentally parsing a non-date string
        import dateparser
        settings = {'STRICT_PARSING': True}
        if dateOrder:
            settings['DATE_ORDER'] = dateOrder
        self.p = dateparser.date.DateDataParser(languages=['en'], settings=settings)

    def parse(self, s):
        return self.p.get_date_data(s)['date_obj']

    def fromFullWithTimezone(self, s):
        # compensate for +0000
        # Wed Nov 07 04:01:10 +0000 2018
        pts = s.split(' ')
        newpts = []
        isTimeZone = ''
        for pt in pts:
            if pt.startswith('+'):
                assertEq('', isTimeZone)
                isTimeZone = ' ' + pt
            else:
                newpts.append(pt)
        return ' '.join(newpts) + isTimeZone

    def getDaysBefore(self, baseDate, n):
        import datetime
        assertTrue(isinstance(n, int))
        diff = datetime.timedelta(days=n)
        return baseDate - diff

    def getDaysBeforeInMilliseconds(self, sBaseDate, nDaysBefore):
        import datetime
        dObj = self.parse(sBaseDate)
        diff = datetime.timedelta(days=nDaysBefore)
        dBefore = dObj - diff
        return int(dBefore.timestamp() * 1000)

    def toUnixMilliseconds(self, s):
        assertTrue(isPy3OrNewer, 'requires python 3 or newer')
        dt = self.parse(s)
        assertTrue(dt, 'not parse dt', s)
        return int(dt.timestamp() * 1000)

def runAndCatchException(fn):
    try:
        fn()
    except:
        import sys
        return sys.exc_info()[1]
    return None

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

def assertWarn(condition, *messageArgs):
    from .common_ui import warn
    if not condition:
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        warn(msg)

def assertWarnEq(expected, received, *messageArgs):
    from .common_ui import warn
    if expected != received:
        import pprint
        msg = ' '.join(map(getPrintable, messageArgs)) if messageArgs else ''
        msg += '\nexpected:\n'
        msg += getPrintable(pprint.pformat(expected))
        msg += '\nbut got:\n'
        msg += getPrintable(pprint.pformat(received))
        warn(msg)

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

def getTraceback(e):
    assertTrue(isPy3OrNewer)
    import traceback
    lines = traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)

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
