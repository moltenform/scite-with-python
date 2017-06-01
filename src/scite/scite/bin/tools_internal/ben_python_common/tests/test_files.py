# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

import pytest
import tempfile
import os
from os.path import join
from ..common_util import isPy3OrNewer
from ..files import (readall, writeall, copy, move, sep, run, isemptydir, listchildren,
    getname, getparent, listfiles, recursedirs, recursefiles, listfileinfo, recursefileinfo,
    computeHash, runWithoutWaitUnicode, ensure_empty_directory, ustr, makedirs, isfile)
    
class TestComputeHash(object):
    def test_computeHashDefaultHash(self, fixture_dir):
        writeall(join(fixture_dir, 'a.txt'), 'contents')
        assert '4a756ca07e9487f482465a99e8286abc86ba4dc7' == computeHash(join(fixture_dir, 'a.txt'))
    
    def test_computeHashMd5(self, fixture_dir):
        import hashlib
        hasher = hashlib.md5()
        writeall(join(fixture_dir, 'a.txt'), 'contents')
        assert '98bf7d8c15784f0a3d63204441e1e2aa' == computeHash(join(fixture_dir, 'a.txt'), hasher)
    
    def test_computeHashCrc(self, fixture_dir):
        writeall(join(fixture_dir, 'a.txt'), 'contents')
        assert 'b4fa1177' == computeHash(join(fixture_dir, 'a.txt'), 'crc32')

class TestDirectoryList(object):
    def test_listChildren(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png', 's1', 's2']
        expectedTuples = [(join(fixture_fulldir, s), s) for s in expected]
        assert expectedTuples == sorted(list(listchildren(fixture_fulldir)))
    
    def test_listChildrenFilenamesOnly(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png', 's1', 's2']
        assert expected == sorted(list(listchildren(fixture_fulldir, filenamesOnly=True)))
    
    def test_listChildrenCertainExtensions(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt']
        assert expected == sorted(list(listchildren(fixture_fulldir, filenamesOnly=True, allowedexts=['png', 'txt'])))

    def test_listFiles(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png']
        expectedTuples = [(join(fixture_fulldir, s), s) for s in expected]
        assert expectedTuples == sorted(list(listfiles(fixture_fulldir)))
    
    def test_listFilesFilenamesOnly(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png']
        assert expected == sorted(list(listfiles(fixture_fulldir, filenamesOnly=True)))

    def test_listFilesCertainExtensions(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt']
        assert expected == sorted(list(listfiles(fixture_fulldir, filenamesOnly=True, allowedexts=['png', 'txt'])))

    def test_recurseFiles(self, fixture_fulldir):
        expected = ['/P1.PNG', '/a1.txt', '/a2png', '/s1/ss1/file.txt', '/s2/other.txt']
        expectedTuples = [(fixture_fulldir + s.replace('/', sep), getname(s)) for s in expected]
        assert expectedTuples == sorted(list(recursefiles(fixture_fulldir)))
    
    def test_recurseFilesFilenamesOnly(self, fixture_fulldir):
        expected = ['P1.PNG', 'a1.txt', 'a2png', 'file.txt', 'other.txt']
        assert expected == sorted(list(recursefiles(fixture_fulldir, filenamesOnly=True)))
    
    def test_recurseFilesCertainExtensions(self, fixture_fulldir):
        expected = ['a1.txt', 'file.txt', 'other.txt']
        assert expected == sorted(list(recursefiles(fixture_fulldir, filenamesOnly=True, allowedexts=['txt'])))
        
    def test_recurseFilesAcceptAllSubDirs(self, fixture_fulldir):
        expected = ['a1.txt', 'file.txt', 'other.txt']
        assert expected == sorted(list(
            recursefiles(fixture_fulldir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda d: True)))
    
    def test_recurseFilesAcceptNoSubDirs(self, fixture_fulldir):
        expected = ['a1.txt']
        assert expected == sorted(list(
            recursefiles(fixture_fulldir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=lambda d: False)))
    
    def test_recurseFilesExcludeOneSubdir(self, fixture_fulldir):
        expected = ['a1.txt', 'other.txt']
        def filter(d):
            return getname(d) != 's1'
        assert expected == sorted(list(recursefiles(fixture_fulldir, filenamesOnly=True, allowedexts=['txt'], fnFilterDirs=filter)))
    
    def test_recurseDirs(self, fixture_fulldir):
        expected = ['/full', '/full/s1', '/full/s1/ss1', '/full/s1/ss2', '/full/s2']
        expectedTuples = [(getparent(fixture_fulldir) + s.replace('/', sep), getname(s)) for s in expected]
        assert expectedTuples == sorted(list(recursedirs(fixture_fulldir)))
    
    def test_recurseDirsNamesOnly(self, fixture_fulldir):
        expected = ['full', 's1', 's2', 'ss1', 'ss2']
        assert expected == sorted(list(recursedirs(fixture_fulldir, filenamesOnly=True)))
    
    def test_recurseDirsExcludeOneSubdir(self, fixture_fulldir):
        expected = ['full', 's2']
        def filter(d):
            return getname(d) != 's1'
        assert expected == sorted(list(recursedirs(fixture_fulldir, filenamesOnly=True, fnFilterDirs=filter)))
    
    def test_listFileInfo(self, fixture_fulldir):
        if isPy3OrNewer:
            expected = [('full', 'P1.PNG', 8), ('full', 'a1.txt', 8), ('full', 'a2png', 8)]
            got = [(getname(getparent(o.path)), o.short(), o.size()) for o in listfileinfo(fixture_fulldir)]
            assert expected == sorted(got)
    
    def test_listFileInfoIncludeDirs(self, fixture_fulldir):
        if isPy3OrNewer:
            expected = [('full', 'P1.PNG', 8), ('full', 'a1.txt', 8), ('full', 'a2png', 8),
                ('full', 's1', 0), ('full', 's2', 0)]
            got = [(getname(getparent(o.path)), o.short(), o.size())
                for o in listfileinfo(fixture_fulldir, filesOnly=False)]
            assert expected == sorted(got)
            
    def test_recurseFileInfo(self, fixture_fulldir):
        if isPy3OrNewer:
            expected = [('full', 'P1.PNG', 8), ('full', 'a1.txt', 8), ('full', 'a2png', 8),
                ('s2', 'other.txt', 8), ('ss1', 'file.txt', 8)]
            got = [(getname(getparent(o.path)), o.short(), o.size())
                for o in recursefileinfo(fixture_fulldir)]
            assert expected == sorted(got)
    
    def test_recurseFileInfoIncludeDirs(self, fixture_fulldir):
        if isPy3OrNewer:
            expected = [('full', 'P1.PNG', 8), ('full', 'a1.txt', 8), ('full', 'a2png', 8),
                ('full', 's1', 0), ('full', 's2', 0), ('s1', 'ss1', 0), ('s1', 'ss2', 0),
                ('s2', 'other.txt', 8), ('ss1', 'file.txt', 8)]
            got = [(getname(getparent(o.path)), o.short(), o.size())
                for o in recursefileinfo(fixture_fulldir, filesOnly=False)]
            assert expected == sorted(got)
    
    def test_checkNamedParameters(self, fixture_dir):
        with pytest.raises(ValueError) as exc:
            list(listchildren(fixture_dir, True))
        exc.match('please name parameters')
        
class TestCopyingFiles(object):
    def test_copyOverwrite_srcNotExist(self, fixture_dir):
        with pytest.raises(IOError):
            copy(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), True)
    
    def test_copyOverwrite_srcExists(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'contents')
        copy(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), True)
        assert 'contents' == readall(join(fixture_dir, u'1\u1101.txt'))
        assert 'contents' == readall(join(fixture_dir, u'2\u1101.txt'))
    
    def test_copyOverwrite_srcOverwrites(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'new')
        writeall(join(fixture_dir, u'2\u1101.txt'), 'old')
        copy(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), True)
        assert 'new' == readall(join(fixture_dir, u'1\u1101.txt'))
        assert 'new' == readall(join(fixture_dir, u'2\u1101.txt'))
    
    def test_copyNoOverwrite_srcNotExist(self, fixture_dir):
        with pytest.raises(IOError):
            copy(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), False)
    
    def test_copyNoOverwrite_srcExists(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'contents')
        copy(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), False)
        assert 'contents' == readall(join(fixture_dir, u'1\u1101.txt'))
        assert 'contents' == readall(join(fixture_dir, u'2\u1101.txt'))
    
    def test_copyNoOverwrite_shouldNotOverwrite(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'new')
        writeall(join(fixture_dir, u'2\u1101.txt'), 'old')
        with pytest.raises((IOError, OSError)):
            copy(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), False)
        assert 'new' == readall(join(fixture_dir, u'1\u1101.txt'))
        assert 'old' == readall(join(fixture_dir, u'2\u1101.txt'))

class TestMovingFiles(object):
    def test_moveOverwrite_srcNotExist(self, fixture_dir):
        with pytest.raises(IOError):
            move(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), True)
    
    def test_moveOverwrite_srcExists(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'contents')
        move(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), True)
        assert not isfile(join(fixture_dir, u'1\u1101.txt'))
        assert 'contents' == readall(join(fixture_dir, u'2\u1101.txt'))
    
    def test_moveOverwrite_srcOverwrites(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'new')
        writeall(join(fixture_dir, u'2\u1101.txt'), 'old')
        move(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), True)
        assert not isfile(join(fixture_dir, u'1\u1101.txt'))
        assert 'new' == readall(join(fixture_dir, u'2\u1101.txt'))
    
    def test_moveNoOverwrite_srcNotExist(self, fixture_dir):
        with pytest.raises(IOError):
            move(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), False)
    
    def test_moveNoOverwrite_srcExists(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'contents')
        move(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), False)
        assert not isfile(join(fixture_dir, u'1\u1101.txt'))
        assert 'contents' == readall(join(fixture_dir, u'2\u1101.txt'))
    
    def test_moveNoOverwrite_shouldNotOverwrite(self, fixture_dir):
        writeall(join(fixture_dir, u'1\u1101.txt'), 'new')
        writeall(join(fixture_dir, u'2\u1101.txt'), 'old')
        with pytest.raises((IOError, OSError)):
            move(join(fixture_dir, u'1\u1101.txt'), join(fixture_dir, u'2\u1101.txt'), False)
        assert 'new' == readall(join(fixture_dir, u'1\u1101.txt'))
        assert 'old' == readall(join(fixture_dir, u'2\u1101.txt'))

class TestMakeDirectories(object):
    def test_makeDirectoriesAlreadyExists(self, fixture_dir):
        makedirs(fixture_dir)
        assert isemptydir(fixture_dir)
    
    def test_makeDirectoriesOneLevel(self, fixture_dir):
        makedirs(fixture_dir + sep + 'a')
        assert isemptydir(fixture_dir + sep + 'a')
    
    def test_makeDirectoriesTwoLevels(self, fixture_dir):
        makedirs(fixture_dir + sep + 'a' + sep + 'a')
        assert isemptydir(fixture_dir + sep + 'a' + sep + 'a')

@pytest.mark.skipif('not sys.platform.startswith("win")')
class TestRunProcess(object):
    def test_runShellScript(self, fixture_dir):
        writeall(join(fixture_dir, 'src.txt'), 'contents')
        writeall(join(fixture_dir, 's.bat'), 'copy src.txt dest.txt')
        returncode, stdout, stderr = run([join(fixture_dir, 's.bat')])
        assert returncode == 0 and isfile(join(fixture_dir, 'dest.txt'))
    
    def test_runShellScriptWithoutCapture(self, fixture_dir):
        writeall(join(fixture_dir, 'src.txt'), 'contents')
        writeall(join(fixture_dir, 's.bat'), 'copy src.txt dest.txt')
        returncode, stdout, stderr = run([join(fixture_dir, 's.bat')], captureoutput=False)
        assert returncode == 0 and isfile(join(fixture_dir, 'dest.txt'))

    def test_runShellScriptWithUnicodeChars(self, fixture_dir):
        import time
        writeall(join(fixture_dir, 'src.txt'), 'contents')
        writeall(join(fixture_dir, u's\u1101.bat'), 'copy src.txt dest.txt')
        runWithoutWaitUnicode([join(fixture_dir, u's\u1101.bat')])
        time.sleep(0.5)
        assert isfile(join(fixture_dir, 'dest.txt'))
    
    def test_runGetExitCode(self, fixture_dir):
        writeall(join(fixture_dir, 's.bat'), '\nexit /b 123')
        returncode, stdout, stderr = run([join(fixture_dir, 's.bat')], throwOnFailure=False)
        assert 123 == returncode
    
    def test_runGetExitCodeWithoutCapture(self, fixture_dir):
        writeall(join(fixture_dir, 's.bat'), '\nexit /b 123')
        returncode, stdout, stderr = run([join(fixture_dir, 's.bat')], throwOnFailure=False, captureoutput=False)
        assert 123 == returncode
    
    def test_runNonZeroExitShouldThrow(self, fixture_dir):
        writeall(join(fixture_dir, 's.bat'), '\nexit /b 123')
        with pytest.raises(RuntimeError):
            run([join(fixture_dir, 's.bat')])
    
    def test_runNonZeroExitShouldThrowWithoutCapture(self, fixture_dir):
        writeall(join(fixture_dir, 's.bat'), '\nexit /b 123')
        with pytest.raises(RuntimeError):
            run([join(fixture_dir, 's.bat')], captureoutput=False)
    
    def test_runSendArgument(self, fixture_dir):
        writeall(join(fixture_dir, 's.bat'), '\n@echo off\necho %1')
        returncode, stdout, stderr = run([join(fixture_dir, 's.bat'), 'testarg'])
        assert returncode == 0 and stdout == b'testarg'
    
    def test_runSendArgumentContainingSpaces(self, fixture_dir):
        writeall(join(fixture_dir, 's.bat'), '\n@echo off\necho %1')
        returncode, stdout, stderr = run([join(fixture_dir, 's.bat'), 'test arg'])
        assert returncode == 0 and stdout == b'"test arg"'
    
    def test_runGetOutput(self, fixture_dir):
        # the subprocess module uses threads to capture both stderr and stdout without deadlock
        writeall(join(fixture_dir, 's.bat'), '@echo off\necho testecho\necho testechoerr 1>&2')
        returncode, stdout, stderr = run([join(fixture_dir, 's.bat')])
        assert returncode == 0
        assert stdout == b'testecho'
        assert stderr == b'testechoerr'
    
@pytest.fixture()
def fixture_dir():
    basedir = join(tempfile.gettempdir(), 'ben_python_common_test', 'empty')
    basedir = ustr(basedir)
    ensure_empty_directory(basedir)
    os.chdir(basedir)
    yield basedir
    ensure_empty_directory(basedir)

@pytest.fixture(scope='module')
def fixture_fulldir():
    basedir = join(tempfile.gettempdir(), 'ben_python_common_test', 'full')
    basedir = ustr(basedir)
    ensure_empty_directory(basedir)
    
    # create every combination:
    # full						contains files and dirs
    # full/s1					contains dirs but no files
    # full/s1/ss1 			contains files but no dirs
    # full/s1/ss2 			contains no files or dirs
    dirsToCreate = ['s1', 's2', 's1/ss1', 's1/ss2']
    for dir in dirsToCreate:
        os.makedirs(join(basedir, dir).replace('/', sep))
    
    filesToCreate = ['P1.PNG', 'a1.txt', 'a2png', 's1/ss1/file.txt', 's2/other.txt']
    for file in filesToCreate:
        writeall(join(basedir, file).replace('/', sep), 'contents')
    
    yield basedir
    ensure_empty_directory(basedir)
