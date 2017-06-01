# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

import os
import pytest
from os.path import join
from collections import OrderedDict
from ..common_ui import *
from .test_files import fixture_dir as fixture_dir_
fixture_dir = fixture_dir_

class TestStringHelpers(object):
    # getPrintable
    def test_getPrintableNormalAscii(self):
        assert 'normal ascii' == getPrintable('normal ascii')

    def test_getPrintableNormalUnicode(self):
        assert 'normal unicode' == getPrintable(u'normal unicode')

    def test_getPrintableWithUniChars(self):
        assert 'k?u?o??n' == getPrintable(u'\u1E31\u1E77\u1E53\u006E')

    def test_getPrintableWithUniCompositeSequence(self):
        assert 'k?u?o??n' == getPrintable(u'\u006B\u0301\u0075\u032D\u006F\u0304\u0301\u006E')

    # replacewholeword
    def test_replacewholeword(self):
        assert 'w,n,w other,wantother,w.other' == re_replacewholeword('want,n,want other,wantother,want.other', 'want', 'w')

    def test_replacewholewordWithPunctation(self):
        assert 'w,n,w other,w??|tother,w.other' == re_replacewholeword('w??|t,n,w??|t other,w??|tother,w??|t.other', 'w??|t', 'w')

    def test_replacewholewordWithCasing(self):
        assert 'and A fad pineapple A da' == re_replacewholeword('and a fad pineapple a da', 'a', 'A')

    # truncateWithEllipsis
    def test_truncateWithEllipsisEmptyString(self):
        assert '' == truncateWithEllipsis('', 2)

    def test_truncateWithEllipsisStringLength1(self):
        assert 'a' == truncateWithEllipsis('a', 2)

    def test_truncateWithEllipsisStringLength2(self):
        assert 'ab' == truncateWithEllipsis('ab', 2)

    def test_truncateWithEllipsisStringLength3(self):
        assert 'ab' == truncateWithEllipsis('abc', 2)

    def test_truncateWithEllipsisStringLength4(self):
        assert 'ab' == truncateWithEllipsis('abcd', 2)

    def test_truncateWithEllipsisEmptyStringTo4(self):
        assert '' == truncateWithEllipsis('', 4)

    def test_truncateWithEllipsisStringTo4Length1(self):
        assert 'a' == truncateWithEllipsis('a', 4)

    def test_truncateWithEllipsisStringTo4Length2(self):
        assert 'ab' == truncateWithEllipsis('ab', 4)

    def test_truncateWithEllipsisStringTo4Length4(self):
        assert 'abcd' == truncateWithEllipsis('abcd', 4)

    def test_truncateWithEllipsisStringLength5TruncatedTo4(self):
        assert 'a...' == truncateWithEllipsis('abcde', 4)

    def test_truncateWithEllipsisStringLength6TruncatedTo4(self):
        assert 'a...' == truncateWithEllipsis('abcdef', 4)

    # formatSize
    def test_formatSizeGb(self):
        assert '3.00GB' == formatSize(3 * 1024 * 1024 * 1024)
        
    def test_formatSizeGbAndFewBytes(self):
        assert '3.00GB' == formatSize(3 * 1024 * 1024 * 1024 + 123)
    
    def test_formatSizeGbDecimal(self):
        assert '3.12GB' == formatSize(3 * 1024 * 1024 * 1024 + 123 * 1024 * 1024)
    
    def test_formatSizeGbDecimalRound(self):
        assert '3.17GB' == formatSize(3 * 1024 * 1024 * 1024 + 169 * 1024 * 1024)
    
    def test_formatSizeMb(self):
        assert '2.31MB' == formatSize(2 * 1024 * 1024 + 315 * 1024)
    
    def test_formatSizeKb(self):
        assert '1.77KB' == formatSize(1 * 1024 + 789)
    
    def test_formatSizeB(self):
        assert '1000b' == formatSize(1000)
    
    def test_formatSize1000B(self):
        assert '678b' == formatSize(678)
    
    def test_formatSizeZeroB(self):
        assert '0b' == formatSize(0)

    # getRandomString
    def test_getRandomString(self):
        s1 = getRandomString()
        s2 = getRandomString()
        assert all((c in '0123456789' for c in s1))
        assert all((c in '0123456789' for c in s2))
        assert s1 != s2
    
    # getClipboardText
    def test_getClipboardTextWithNoUnicode(self):
        prev = getClipboardText()
        try:
            setClipboardText('normal ascii')
            assert 'normal ascii' == getClipboardText()
        finally:
            setClipboardText(prev)
    
    def test_getClipboardTextWithUnicode(self):
        prev = getClipboardText()
        try:
            setClipboardText(u'\u1E31\u1E77\u1E53\u006E')
            assert u'\u1E31\u1E77\u1E53\u006E' == getClipboardText()
        finally:
            setClipboardText(prev)

class TestDataStructures(object):
    # takeBatch
    def test_takeBatchNonLazy(self):
        assert [[1, 2, 3], [4, 5, 6], [7]] == takeBatch([1, 2, 3, 4, 5, 6, 7], 3)
        assert [[1, 2, 3], [4, 5, 6]] == takeBatch([1, 2, 3, 4, 5, 6], 3)
        assert [[1, 2, 3], [4, 5]] == takeBatch([1, 2, 3, 4, 5], 3)
        assert [[1, 2], [3, 4], [5]] == takeBatch([1, 2, 3, 4, 5], 2)
    
    def test_takeBatchWithCallbackOddNumber(self):
        log = []
        def callback(batch, log=log):
            log.append(list(batch))
        with TakeBatch(2, callback) as obj:
            obj.append(1)
            obj.append(2)
            obj.append(3)
        assert [[1, 2], [3]] == log
    
    def test_takeBatchWithCallbackEvenNumber(self):
        log = []
        def callback(batch, log=log):
            log.append(list(batch))
        with TakeBatch(2, callback) as obj:
            obj.append(1)
            obj.append(2)
            obj.append(3)
            obj.append(4)
        assert [[1, 2], [3, 4]] == log
    
    def test_takeBatchWithCallbackSmallNumber(self):
        log = []
        def callback(batch, log=log):
            log.append(list(batch))
        with TakeBatch(3, callback) as obj:
            obj.append(1)
        assert [[1]] == log
    
    def test_takeBatchWithCallbackDoNotCallOnException(self):
        log = []
        def callback(batch, log=log):
            log.append(list(batch))
        
        # normally, leaving scope of TakeBatch makes final call, but don't if leaving because of exception
        with pytest.raises(IOError):
            with TakeBatch(2, callback) as obj:
                obj.append(1)
                obj.append(2)
                obj.append(3)
                raise IOError()
        assert [[1, 2]] == log
    
    def test_memoizeCountNumberOfCalls_RepeatedCall(self):
        if sys.version_info[0] <= 2:
            countCalls = Bucket(count=0)
            
            @BoundedMemoize
            def addTwoNumbers(a, b, countCalls=countCalls):
                countCalls.count += 1
                return a + b
            assert 20 == addTwoNumbers(10, 10)
            assert 20 == addTwoNumbers(10, 10)
            assert 40 == addTwoNumbers(20, 20)
            assert 2 == countCalls.count
    
    def test_memoizeCountNumberOfCalls_InterleavedCall(self):
        if sys.version_info[0] <= 2:
            countCalls = Bucket(count=0)
            
            @BoundedMemoize
            def addTwoNumbers(a, b, countCalls=countCalls):
                countCalls.count += 1
                return a + b
            assert 20 == addTwoNumbers(10, 10)
            assert 40 == addTwoNumbers(20, 20)
            assert 20 == addTwoNumbers(10, 10)
            assert 2 == countCalls.count
    
    def test_checkOrderedDictEqualitySame(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d1same = OrderedDict()
        d1same['a'] = 1
        d1same['b'] = 2
        assert d1 == d1
        assert d1 == d1same
        assert d1same == d1
    
    def test_checkOrderedDictEqualityDifferentOrder(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d2 = OrderedDict()
        d2['b'] = 2
        d2['a'] = 1
        assert d1 != d2
    
    def test_checkOrderedDictEqualityDifferentValues(self):
        d1 = OrderedDict()
        d1['a'] = 1
        d1['b'] = 2
        d2 = OrderedDict()
        d2['a'] = 1
        d2['b'] = 3
        assert d1 != d2
    
    def test_recentlyUsedList_MaxNotExceeded(self):
        mruTest = RecentlyUsedList(maxSize=5)
        mruTest.add('abc')
        mruTest.add('def')
        mruTest.add('ghi')
        assert ['ghi', 'def', 'abc'] == mruTest.getList()

    def test_recentlyUsedList_RedundantEntryMovedToTop(self):
        mruTest = RecentlyUsedList(maxSize=5)
        mruTest.add('aaa')
        mruTest.add('bbb')
        mruTest.add('ccc')
        mruTest.add('bbb')
        assert ['bbb', 'ccc', 'aaa'] == mruTest.getList()
    
    def test_recentlyUsedList_MaxSizePreventsGrowth(self):
        mruTest = RecentlyUsedList(maxSize=2)
        mruTest.add('aaa')
        mruTest.add('bbb')
        mruTest.add('ccc')
        assert ['ccc', 'bbb'] == mruTest.getList()
    
    def test_recentlyUsedList_MaxSizePreventsMoreGrowth(self):
        mruTest = RecentlyUsedList(maxSize=2)
        mruTest.add('aaa')
        mruTest.add('bbb')
        mruTest.add('ccc')
        mruTest.add('ddd')
        assert ['ddd', 'ccc'] == mruTest.getList()

class TestCommonUI(object):
    def test_checkIsDigit(self):
        # make sure isdigit behaves as expected
        assert not ''.isdigit()
        assert '0'.isdigit()
        assert '123'.isdigit()
        assert not '123 '.isdigit()
        assert not '123a'.isdigit()
        assert not 'a123'.isdigit()

    def test_findUnusedLetterMaintainsUsedLetterState(self):
        d = dict()
        assert 0 == findUnusedLetter(d, 'abc')
        assert 1 == findUnusedLetter(d, 'abc')
        assert 2 == findUnusedLetter(d, 'abc')
        assert None is findUnusedLetter(d, 'abc')
        assert None is findUnusedLetter(d, 'ABC')
        assert None is findUnusedLetter(d, 'a b c!@#')

    def test_softDeleteFileShouldMakeFileNotExist(self, fixture_dir):
        path = join(fixture_dir, 'testdelfile1.txt')
        files.writeall(path, 'contents')
        assert os.path.exists(path)
        newlocation = softDeleteFile(path)
        assert not os.path.exists(path)
        assert os.path.exists(newlocation)

    def test_softDeleteFileShouldRenameFirstCharOfFile(self, fixture_dir):
        path = join(fixture_dir, 'zzzz', 'testdelfile2.txt')
        files.makedirs(files.getparent(path))
        files.writeall(path, 'contents')
        newlocation = softDeleteFile(path)
        assert os.path.exists(newlocation)
        assert files.getname(newlocation).startswith('z')

class TestCustomAsserts(object):
    def raisevalueerr(self):
        raise ValueError('msg')
    
    # assertException
    def test_assertExceptionExpectsAnyException(self):
        assertException(self.raisevalueerr, None)
    
    def test_assertExceptionExpectsSpecificException(self):
        assertException(self.raisevalueerr, ValueError)
    
    def test_assertExceptionExpectsSpecificExceptionAndMessage(self):
        assertException(self.raisevalueerr, ValueError, 'msg')
    
    def test_assertExceptionFailsIfNoExceptionThrown(self):
        with pytest.raises(AssertionError) as exc:
            assertException(lambda: 1, None)
        exc.match('did not throw')
    
    def test_assertExceptionFailsIfWrongExceptionThrown(self):
        with pytest.raises(AssertionError) as exc:
            assertException(self.raisevalueerr, ValueError, 'notmsg')
        exc.match('exception string check failed')
    
    # assertTrue
    def test_assertTrueExpectsTrue(self):
        assertTrue(True)
        assertTrue(1)
        assertTrue('string')
    
    def test_assertTrueFailsIfFalse(self):
        with pytest.raises(AssertionError):
            assertTrue(False)
    
    def test_assertTrueFailsIfFalseWithMessage(self):
        with pytest.raises(AssertionError) as exc:
            assertTrue(False, 'custom msg')
        exc.match('custom msg')
    
    # assertEq
    def test_assertEq(self):
        assertEq(True, True)
        assertEq(1, 1)
        assertEq((1, 2, 3), (1, 2, 3))
    
    def test_assertEqFailsIfNotEqual(self):
        with pytest.raises(AssertionError):
            assertEq(1, 2, 'msg here')
    
    # test assertFloatEq
    def test_assertFloatEqEqual(self):
        assertFloatEq(0.0, 0)
        assertFloatEq(0.1234, 0.1234)
        assertFloatEq(-0.1234, -0.1234)
    
    def test_assertFloatEqEqualWithinPrecision(self):
        assertFloatEq(0.123456788, 0.123456789)
    
    def test_assertFloatNotEqualGreater(self):
        with pytest.raises(AssertionError):
            assertFloatEq(0.4, 0.1234)
    
    def test_assertFloatNotEqualSmaller(self):
        with pytest.raises(AssertionError):
            assertFloatEq(0.1234, 0.4)
    
    def test_assertFloatNotEqualBitGreater(self):
        with pytest.raises(AssertionError):
            assertFloatEq(-0.123457, -0.123456)
    
    def test_assertFloatNotEqualBitSmaller(self):
        with pytest.raises(AssertionError):
            assertFloatEq(-0.123457, -0.123458)
            
    def test_assertFloatNotEqualNegative(self):
        with pytest.raises(AssertionError):
            assertFloatEq(0.1234, -0.1234)
