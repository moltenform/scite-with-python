
import sys
from common_util import *
from common_ui import *

def common_util_tests():
    # test assertException
    def raisevalueerr():
        raise ValueError('msg')
    assertException(lambda: raisevalueerr(), None)
    assertException(lambda: raisevalueerr(), ValueError)
    assertException(lambda: raisevalueerr(), ValueError, 'msg')
    assertException(lambda: assertException(lambda: 1, None), AssertionError, 'did not throw')
    assertException(lambda: assertException(lambda: raisevalueerr(), TypeError), AssertionError, 'exception type check failed')
    assertException(lambda: assertException(lambda: raisevalueerr(), ValueError, 'notmsg'), AssertionError, 'exception string check failed')
    
    # test assertTrue
    assertTrue(True)
    assertException(lambda: assertTrue(False, 'msg here'), AssertionError, 'msg here')
    
    # test assertEq
    assertEq(1, 1)
    assertException(lambda: assertEq(1, 2, 'msg here'), AssertionError, 'msg here')
    
    # test assertFloatEq
    assertFloatEq(0.1234, 0.1234)
    assertFloatEq(0.123456788, 0.123456789)
    assertException(lambda: assertFloatEq(0.4, 0.1234), AssertionError)
    assertException(lambda: assertFloatEq(0.1234, 0.4), AssertionError)
    assertException(lambda: assertFloatEq(-0.123457, -0.123456), AssertionError)
    assertException(lambda: assertFloatEq(-0.123456, -0.123457), AssertionError)
    
    # test Bucket
    b = Bucket()
    b.elem1 = '1'
    b.elem2 = '2'
    assertEq('elem1=1\n\n\nelem2=2', b.__repr__())
    
    # test getPrintable
    assertEq('normal ascii', getPrintable('normal ascii'))
    assertEq('normal unicode', getPrintable(u'normal unicode'))
    assertEq('k?u?o??n', getPrintable(u'\u1E31\u1E77\u1E53\u006E'))  # mixed non-ascii and ascii
    assertEq('k?u?o??n', getPrintable(u'\u006B\u0301\u0075\u032D\u006F\u0304\u0301\u006E'))  # mixed composite sequence and ascii
    
    # test getRandomString
    s1 = getRandomString()
    s2 = getRandomString()
    assertTrue(all((c in '0123456789' for c in s1)))
    assertTrue(all((c in '0123456789' for c in s2)))
    assertTrue(s1 != s2)
    
    # test re_replacewholeword
    assertEq('w,n,w other,wantother,w.other', re_replacewholeword('want,n,want other,wantother,want.other', 'want', 'w'))
    assertEq('w,n,w other,w??|tother,w.other', re_replacewholeword('w??|t,n,w??|t other,w??|tother,w??|t.other', 'w??|t', 'w'))
    assertEq('and A fad pineapple A da', re_replacewholeword('and a fad pineapple a da', 'a', 'A'))
    assertEq('and a GAd pinGApple a GA', re_replace('and a fad pineapple a da', '[abcdef]a', 'GA'))
    
    # test getClipboardText
    prev = getClipboardText()
    try:
        setClipboardText('normal ascii')
        assertEq('normal ascii', getClipboardText())
        setClipboardText(u'\u1E31\u1E77\u1E53\u006E')
        assertEq(u'\u1E31\u1E77\u1E53\u006E', getClipboardText())
    finally:
        setClipboardText(prev)
    
    # takeBatch and takeBatchOnArbitraryIterable have the same implementation
    assertEq([[1, 2, 3], [4, 5, 6], [7]], takeBatch([1, 2, 3, 4, 5, 6, 7], 3))
    assertEq([[1, 2, 3], [4, 5, 6]], takeBatch([1, 2, 3, 4, 5, 6], 3))
    assertEq([[1, 2, 3], [4, 5]], takeBatch([1, 2, 3, 4, 5], 3))
    assertEq([[1, 2], [3, 4], [5]], takeBatch([1, 2, 3, 4, 5], 2))
    
    # test TakeBatch class
    callbackLog = []

    def callback(batch, callbackLog=callbackLog):
        callbackLog.append(batch)
        
    tb1 = TakeBatch(2, callback)
    tb1.append(1)
    assertEq([], callbackLog)
    tb1.append(2)
    assertEq([[1, 2]], callbackLog)
    tb1.append(3)
    assertEq([[1, 2]], callbackLog)
    tb1.append(4)
    assertEq([[1, 2], [3, 4]], callbackLog)
    
    # TakeBatch should call, if going out of scope normally
    callbackLog[:] = []
    with TakeBatch(2, callback) as tb2:
        tb2.append(1)
        tb2.append(2)
        tb2.append(3)
    assertEq([[1, 2], [3]], callbackLog)
    
    # TakeBatch should not call, if going out of scope due to exception
    callbackLog[:] = []
    sawException = False
    try:
        with TakeBatch(2, callback) as tb3:
            tb3.append(1)
            tb3.append(2)
            tb3.append(3)
            raise TypeError()
    except TypeError:
        sawException = True
    assertEq(True, sawException)
    assertEq([[1, 2]], callbackLog)
    
    # test OrderedDict equality checks
    from collections import OrderedDict
    assertEq(OrderedDict(a=1, b=2), OrderedDict(b=2, a=1))
    assertTrue(OrderedDict(a=1, b=2) != OrderedDict(a=1, b=3))
    
    # test BoundedMemoize
    countCalls = Bucket(count=0)

    @BoundedMemoize
    def addTwoNumbers(a, b, countCalls=countCalls):
        countCalls.count += 1
        return a + b
    assertEq(2, addTwoNumbers(1, 1))
    assertEq(1, countCalls.count)
    assertEq(2, addTwoNumbers(1, 1))
    assertEq(1, countCalls.count)
    assertEq(4, addTwoNumbers(2, 2))
    assertEq(2, countCalls.count)
    
    # test RecentlyUsedList
    mruTest = RecentlyUsedList(maxSize=5)
    mruTest.add('abc')
    mruTest.add('def')
    mruTest.add('ghi')
    assertEqArray('ghi|def|abc', mruTest.getList())
    
    # redundant entries should not be added, but still moved to top
    mruTest.add('abc')
    assertEqArray('abc|ghi|def', mruTest.getList())
    mruTest.add('def')
    assertEqArray('def|abc|ghi', mruTest.getList())
    mruTest.add('ghi')
    assertEqArray('ghi|def|abc', mruTest.getList())
    
    # size should be capped
    mruTest.add('1')
    assertEqArray('1|ghi|def|abc', mruTest.getList())
    mruTest.add('2')
    assertEqArray('2|1|ghi|def|abc', mruTest.getList())
    mruTest.add('3')
    assertEqArray('3|2|1|ghi|def', mruTest.getList())
    mruTest.add('4')
    assertEqArray('4|3|2|1|ghi', mruTest.getList())
    
def files_tests():
    from files import (readall, writeall, exists, copy, move, sep, run, isemptydir, listchildren, makedir,
        getname, listfiles, recursedirs, recursefiles, delete, runWithoutWaitUnicode)
    import tempfile
    import os
    import shutil
    tmpdir = tempfile.gettempdir() + sep + 'pytest'
    tmpdirsl = tmpdir + sep
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)

    def cleardirectoryfiles(d):
        shutil.rmtree(d)
        os.mkdir(d)
        assertTrue(isemptydir(d))
    
    # test copy_overwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: copy(tmpdirsl + 'src.txt', tmpdirsl + 'srccopy.txt', True), IOError)
    
    # test copy_overwrite, simple copy
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    copy(tmpdirsl + 'src.txt', tmpdirsl + 'srccopy.txt', True)
    assertEq('src', readall(tmpdirsl + 'srccopy.txt'))
    assertTrue(exists(tmpdirsl + 'src.txt'))
    
    # test copy_overwrite, overwrite
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    assertEq('src', readall(tmpdirsl + 'src.txt'))
    writeall(tmpdirsl + 'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl + 'dest.txt'))
    copy(tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt', True)
    assertEq('src', readall(tmpdirsl + 'dest.txt'))
    assertTrue(exists(tmpdirsl + 'src.txt'))
    
    # test copy_nooverwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: copy(tmpdirsl + 'src.txt', tmpdirsl + 'srccopy.txt', False), IOError)
    
    # test copy_nooverwrite, simple copy
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    copy(tmpdirsl + 'src.txt', tmpdirsl + 'srccopy.txt', False)
    assertEq('src', readall(tmpdirsl + 'srccopy.txt'))
    
    # test copy_nooverwrite, simple overwrite should fail
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    assertEq('src', readall(tmpdirsl + 'src.txt'))
    writeall(tmpdirsl + 'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl + 'dest.txt'))
    if sys.platform == 'win32':
        assertException(lambda: copy(tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt', False), IOError, 'CopyFileW failed')
    else:
        assertException(lambda: copy(tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt', False), OSError, 'File exists')
    assertEq('dest', readall(tmpdirsl + 'dest.txt'))
    
    # test move_overwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: move(tmpdirsl + 'src.txt', tmpdirsl + 'srcmove.txt', True), IOError)
    assertTrue(not exists(tmpdirsl + 'src.txt'))
    
    # test move_overwrite, simple move
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    move(tmpdirsl + 'src.txt', tmpdirsl + 'srcmove.txt', True)
    assertEq('src', readall(tmpdirsl + 'srcmove.txt'))
    assertTrue(not exists(tmpdirsl + 'src.txt'))
    
    # test move_overwrite, overwrite
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    assertEq('src', readall(tmpdirsl + 'src.txt'))
    writeall(tmpdirsl + 'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl + 'dest.txt'))
    move(tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt', True)
    assertEq('src', readall(tmpdirsl + 'dest.txt'))
    assertTrue(not exists(tmpdirsl + 'src.txt'))
    
    # test move_nooverwrite, source not exist
    cleardirectoryfiles(tmpdir)
    assertException(lambda: move(tmpdirsl + 'src.txt', tmpdirsl + 'srcmove.txt', False), IOError)
    assertTrue(not exists(tmpdirsl + 'src.txt'))
    
    # test move_nooverwrite, simple move
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    move(tmpdirsl + 'src.txt', tmpdirsl + 'srcmove.txt', False)
    assertEq('src', readall(tmpdirsl + 'srcmove.txt'))
    assertTrue(not exists(tmpdirsl + 'src.txt'))
    
    # test move_nooverwrite, simple overwrite should fail
    cleardirectoryfiles(tmpdir)
    writeall(tmpdirsl + 'src.txt', 'src')
    assertEq('src', readall(tmpdirsl + 'src.txt'))
    writeall(tmpdirsl + 'dest.txt', 'dest')
    assertEq('dest', readall(tmpdirsl + 'dest.txt'))
    if sys.platform == 'win32':
        assertException(lambda: move(tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt', False), IOError, 'MoveFileExW failed')
    else:
        assertException(lambda: move(tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt', False), OSError, 'File exists')
    assertEq('dest', readall(tmpdirsl + 'dest.txt'))
    assertTrue(exists(tmpdirsl + 'src.txt'))
    
    # test _checkNamedParameters
    assertException(lambda: list(listchildren(tmpdir, True)), ValueError, 'please name parameters')
    
    # tmpdir has files, dirs
    # tmpdir/s1 has no files, dirs
    # tmpdir/s1/ss1 has files, no dirs
    # tmpdir/s1/ss2 has no files, dirs
    cleardirectoryfiles(tmpdir)
    dirstomake = [tmpdir, tmpdirsl + 's1', tmpdirsl + 's1' + sep + 'ss1', tmpdirsl + 's1' + sep + 'ss2', tmpdirsl + 's2']
    filestomake = [tmpdirsl + 'P1.PNG', tmpdirsl + 'a1.txt', tmpdirsl + 'a2png',
        tmpdirsl + 's1' + sep + 'ss1' + sep + 'file.txt', tmpdirsl + 's2' + sep + 'other.txt']
    for dir in dirstomake:
        if dir != tmpdir:
            makedir(dir)
    for file in filestomake:
        writeall(file, 'content')
    
    # test listchildren
    expected = ['P1.PNG', 'a1.txt', 'a2png', 's1', 's2']
    assertEq([(tmpdirsl + s, s) for s in expected], sorted(list(listchildren(tmpdir))))
    assertEq(expected, sorted(list(listchildren(tmpdir, filenamesOnly=True))))
    assertEq(['P1.PNG', 'a1.txt'], sorted(list(listchildren(tmpdir, filenamesOnly=True, allowedexts=['png', 'txt']))))
    
    # test listfiles
    expected = ['P1.PNG', 'a1.txt', 'a2png']
    assertEq([(tmpdirsl + s, s) for s in expected], sorted(list(listfiles(tmpdir))))
    assertEq(expected, sorted(list(listfiles(tmpdir, filenamesOnly=True))))
    assertEq(['P1.PNG', 'a1.txt'], sorted(list(listfiles(tmpdir, filenamesOnly=True, allowedexts=['png', 'txt']))))
    
    # test recursefiles
    assertEq([(s, getname(s)) for s in filestomake],
        sorted(list(recursefiles(tmpdir))))
    assertEq([getname(s) for s in filestomake],
        sorted(list(recursefiles(tmpdir, filenamesOnly=True))))
    assertEq(['a1.txt', 'file.txt', 'other.txt'],
        sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt']))))
    assertEq(['a1.txt', 'file.txt', 'other.txt'],
        sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda d: True))))
    assertEq(['a1.txt'],
        sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda d: False))))
    assertEq(['a1.txt', 'other.txt'],
        sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda dir: getname(dir) != 's1'))))
    assertEq(['a1.txt', 'file.txt'],
        sorted(list(recursefiles(tmpdir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda dir: getname(dir) != 's2'))))
    
    # test recursedirs
    assertEq(sorted([(s, getname(s)) for s in dirstomake]), sorted(list(recursedirs(tmpdir))))
    assertEq(sorted([getname(s) for s in dirstomake]), sorted(list(recursedirs(tmpdir, filenamesOnly=True))))
    assertEq(['pytest', 's2'], sorted(list(recursedirs(tmpdir, filenamesOnly=True, fnFilterDirs=lambda dir: getname(dir) != 's1'))))
    
    # test run process, simple batch script
    if sys.platform == 'win32':
        cleardirectoryfiles(tmpdir)
        writeall(tmpdirsl + 'src.txt', 'src')
        writeall(tmpdirsl + 'script.bat', 'copy "%ssrc.txt" "%sdest.txt"'%(tmpdirsl, tmpdirsl))
        assertTrue(not exists(tmpdirsl + 'dest.txt'))
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat'])
        assertEq(0, returncode)
        assertTrue(exists(tmpdirsl + 'dest.txt'))
        
        # specify no capture and run again
        delete(tmpdirsl + 'dest.txt')
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat'], captureoutput=False)
        assertEq(0, returncode)
        assertTrue(exists(tmpdirsl + 'dest.txt'))
        
        # run process with unicode characters
        delete(tmpdirsl + 'dest.txt')
        unicodepath = tmpdirsl + u'scr#1pt#2.bat'.replace('#1', u'\u012B').replace('#2', u'\u013C')
        writeall(unicodepath, 'copy "%ssrc.txt" "%sdest.txt"'%(tmpdirsl, tmpdirsl))
        try:
            import time
            runWithoutWaitUnicode([unicodepath])
            time.sleep(0.5)
            assertTrue(exists(tmpdirsl + 'dest.txt'))
        finally:
            delete(unicodepath)
        
        # test run process, batch script returns failure
        cleardirectoryfiles(tmpdir)
        writeall(tmpdirsl + 'script.bat', '\nexit /b 123')
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat'], throwOnFailure=False)
        assertEq(123, returncode)
        # specify no capture and run again
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat'], throwOnFailure=False, captureoutput=False)
        assertEq(123, returncode)
        # except exception
        assertException(lambda: run([tmpdirsl + 'script.bat']), RuntimeError, 'retcode is not 0')
        # specify no capture, except exception
        assertException(lambda: run([tmpdirsl + 'script.bat'], captureoutput=False), RuntimeError, 'retcode is not 0')
        
        # test run process, get stdout
        writeall(tmpdirsl + 'script.bat', '\n@echo off\necho testecho')
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat'])
        assertEq(0, returncode)
        assertEq('testecho', stdout)
        assertEq('', stderr)
        
        # test run process, get stderr
        writeall(tmpdirsl + 'script.bat', '\n@echo off\necho testechoerr 1>&2')
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat'])
        assertEq(0, returncode)
        assertEq('', stdout)
        assertEq('testechoerr', stderr)
        
        # test run process, get both. (this deadlocks if done naively, but it looks like subprocess correctly uses 2 threads.)
        writeall(tmpdirsl + 'script.bat', '\n@echo off\necho testecho\necho testechoerr 1>&2')
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat'])
        assertEq(0, returncode)
        assertEq('testecho', stdout)
        assertEq('testechoerr', stderr)
        
        # test run process, send argument without spaces
        writeall(tmpdirsl + 'script.bat', '\n@echo off\necho %1')
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat', 'testarg'])
        assertEq(0, returncode)
        assertEq('testarg', stdout)
        
        # test run process, send argument with spaces (subprocess will quote the args)
        writeall(tmpdirsl + 'script.bat', '\n@echo off\necho %1')
        returncode, stdout, stderr = run([tmpdirsl + 'script.bat', 'test arg'])
        assertEq(0, returncode)
        assertEq('"test arg"', stdout)
        
        # test run process, run without shell
        cleardirectoryfiles(tmpdir)
        writeall(tmpdirsl + 'src.txt', 'src')
        # won't work without the shell:
        assertException(lambda: run(['copy', tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt']), OSError)
        assertTrue(not exists(tmpdirsl + 'dest.txt'))
        # will work with the shell
        returncode, stdout, stderr = run(['copy', tmpdirsl + 'src.txt', tmpdirsl + 'dest.txt'], shell=True)
        assertEq(0, returncode)
        assertTrue(exists(tmpdirsl + 'dest.txt'))

def common_ui_tests():
    # test softDeleteFile
    import tempfile
    tmpdir = tempfile.gettempdir() + files.sep + 'pytest'
    if not files.exists(tmpdir):
        files.mkdir(tmpdir)
    movedname = None
    srcfile = tmpdir + files.sep + 'tmp.txt'
    files.writeall(srcfile, 'test')
    try:
        assertTrue(files.exists(srcfile))
        movedname = softDeleteFile(srcfile)
        assertTrue(not files.exists(srcfile))
        assertTrue(files.exists(movedname))
        assertTrue(movedname != srcfile)
        assertTrue(files.split(movedname)[1] != files.split(srcfile)[1])
    finally:
        if files.exists(srcfile):
            files.delete(srcfile)
        if movedname and files.exists(movedname):
            files.delete(movedname)
    
    # test isdigit
    assertTrue(not ''.isdigit())
    assertTrue('0'.isdigit())
    assertTrue('123'.isdigit())
    assertTrue(not '123 '.isdigit())
    assertTrue(not '123a'.isdigit())
    assertTrue(not 'a123'.isdigit())
    
    # test _findUnusedLetter
    d = dict()
    assertEq(0, findUnusedLetter(d, 'abc'))
    assertEq(1, findUnusedLetter(d, 'abc'))
    assertEq(2, findUnusedLetter(d, 'abc'))
    assertEq(None, findUnusedLetter(d, 'abc'))
    assertEq(None, findUnusedLetter(d, 'ABC'))
    assertEq(None, findUnusedLetter(d, 'a b c!@#'))
    

if __name__ == '__main__':
    common_util_tests()
    files_tests()
    common_ui_tests()
