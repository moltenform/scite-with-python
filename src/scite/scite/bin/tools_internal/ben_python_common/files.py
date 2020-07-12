# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

import sys
import os as _os
import shutil as _shutil
from .common_higher import *
from .common_util import *

rename = _os.rename
delete = _os.unlink
exists = _os.path.exists
join = _os.path.join
split = _os.path.split
splitext = _os.path.splitext
isdir = _os.path.isdir
isfile = _os.path.isfile
getsize = _os.path.getsize
rmdir = _os.rmdir
chdir = _os.chdir
sep = _os.path.sep
linesep = _os.linesep
abspath = _os.path.abspath
rmtree = _shutil.rmtree

# simple wrappers
def getparent(s):
    return _os.path.split(s)[0]
    
def getname(s):
    return _os.path.split(s)[1]
    
def modtime(s):
    return _os.stat(s).st_mtime
    
def createdtime(s):
    return _os.stat(s).st_ctime
    
def getext(s, removeDot=True):
    a, b = splitext(s)
    if removeDot and len(b) > 0 and b[0] == '.':
        return b[1:].lower()
    else:
        return b.lower()
    
def deletesure(s):
    if exists(s):
        delete(s)
    assert not exists(s)
    
def makedirs(s):
    try:
        _os.makedirs(s)
    except OSError:
        if isdir(s):
            return
        else:
            raise

def ensureEmptyDirectory(d):
    if isfile(d):
        raise IOError('file exists at this location ' + d)
    
    if isdir(d):
        # delete all existing files in the directory
        for s in _os.listdir(d):
            if _os.path.isdir(join(d, s)):
                _shutil.rmtree(join(d, s))
            else:
                _os.unlink(join(d, s))
        
        assertTrue(isemptydir(d))
    else:
        _os.makedirs(d)

def copy(srcfile, destfile, overwrite, traceToStdout=False):
    if not isfile(srcfile):
        raise IOError('source path does not exist or is not a file')

    if traceToStdout:
        trace('copy()', srcfile, destfile)

    if srcfile == destfile:
        pass
    elif sys.platform.startswith('win'):
        from ctypes import windll, c_wchar_p, c_int, GetLastError
        failIfExists = c_int(0) if overwrite else c_int(1)
        res = windll.kernel32.CopyFileW(c_wchar_p(srcfile), c_wchar_p(destfile), failIfExists)
        if not res:
            err = GetLastError()
            raise IOError('CopyFileW failed (maybe dest already exists?) err=%d' % err +
                getPrintable(srcfile + '->' + destfile))
    else:
        if overwrite:
            _shutil.copy(srcfile, destfile)
        else:
            copyFilePosixWithoutOverwrite(srcfile, destfile)

    assertTrue(exists(destfile))
        
def move(srcfile, destfile, overwrite, warn_between_drives=False,
        traceToStdout=False, allowDirs=False):
    if not exists(srcfile):
        raise IOError('source path does not exist')
    if not allowDirs and not isfile(srcfile):
        raise IOError('source path does not exist or is not a file')

    if traceToStdout:
        trace('move()', srcfile, destfile)

    if srcfile == destfile:
        pass
    elif sys.platform.startswith('win'):
        from ctypes import windll, c_wchar_p, c_int, GetLastError
        ERROR_NOT_SAME_DEVICE = 17
        flags = 0
        flags |= 1 if overwrite else 0
        flags |= 0 if warn_between_drives else 2
        res = windll.kernel32.MoveFileExW(c_wchar_p(srcfile), c_wchar_p(destfile), c_int(flags))
        if not res:
            err = GetLastError()
            if err == ERROR_NOT_SAME_DEVICE and warn_between_drives:
                rinput('Note: moving file from one drive to another. ' +
                    '%s %s Press Enter to continue.\r\n'%(srcfile, destfile))
                return move(srcfile, destfile, overwrite, warn_between_drives=False)
                
            raise IOError('MoveFileExW failed (maybe dest already exists?) err=%d' % err +
                getPrintable(srcfile + '->' + destfile))
        
    elif sys.platform.startswith('linux') and overwrite:
        _os.rename(srcfile, destfile)
    else:
        copy(srcfile, destfile, overwrite)
        _os.unlink(srcfile)
    
    assertTrue(exists(destfile))

def copyTrace(srcfile, destfile, overwrite):
    if not isfile(srcfile):
        raise IOError('source path does not exist or is not a file')

def copyFilePosixWithoutOverwrite(srcfile, destfile):
    # fails if destination already exist. O_EXCL prevents other files from writing to location.
    # raises OSError on failure.
    flags = _os.O_CREAT | _os.O_EXCL | _os.O_WRONLY
    file_handle = _os.open(destfile, flags)
    with _os.fdopen(file_handle, 'wb') as fdest:
        with open(srcfile, 'rb') as fsrc:
            while True:
                buffer = fsrc.read(64 * 1024)
                if not buffer:
                    break
                fdest.write(buffer)

# "millistime" is number of milliseconds past epoch (unix time * 1000)

def getModTimeNs(path, asMillisTime=False):
    t = _os.stat(path).st_mtime_ns
    if asMillisTime:
        t = int(t / 1.0e6)
    return t

def getCTimeNs(path, asMillisTime=False):
    t = _os.stat(path).st_ctime_ns
    if asMillisTime:
        t = int(t / 1.0e6)
    return t

def getATimeNs(path, asMillisTime=False):
    t = _os.stat(path).st_atime_ns
    if asMillisTime:
        t = int(t / 1.0e6)
    return t

def setModTimeNs(path, mtime, asMillisTime=False):
    if asMillisTime:
        mtime *= 1e6
    atime = getATimeNs(path)
    _os.utime(path, ns=(atime, mtime))

def setATimeNs(path, atime, asMillisTime=False):
    if asMillisTime:
        atime *= 1e6
    mtime = getModTimeNs(path)
    _os.utime(path, ns=(atime, mtime))

def getFileLastModifiedTime(filepath):
    return _os.path.getmtime(filepath)

def setFileLastModifiedTime(filepath, lmt):
    curtimes = _os.stat(filepath)
    newtimes = (curtimes.st_atime, lmt)
    with open(filepath, 'ab'):
        _os.utime(filepath, newtimes)

def _openSupportingUnicode(s, mode, unicodetype, encoding):
    if encoding:
        # python 3-style
        return lambda: open(s, mode, encoding=encoding)
    elif unicodetype:
        # python 2-style. see also: io.open
        import codecs
        return lambda: codecs.open(s, mode, encoding=unicodetype)
    else:
        return lambda: open(s, mode)

# unicodetype can be utf-8, utf-8-sig, etc.
def readall(s, mode='r', unicodetype=None, encoding=None):
    with _openSupportingUnicode(s, mode, unicodetype, encoding)() as f:
        return f.read()

# unicodetype can be utf-8, utf-8-sig, etc.
def writeall(s, txt, mode='w', unicodetype=None, encoding=None, skipIfSameContent=False, updateTimeIfSameContent=True):
    if skipIfSameContent and isfile(s):
        assertTrue(mode == 'w' or mode == 'wb')
        currentContent = readall(s, mode.replace('w', 'r'), unicodetype, encoding)
        if currentContent == txt:
            if updateTimeIfSameContent:
                setFileLastModifiedTime(s, getNowAsMillisTime() / 1000.0)
            return False

    with _openSupportingUnicode(s, mode, unicodetype, encoding)() as f:
        f.write(txt)
        return True


_enforceExplicitlyNamedParameters = object()
# use this to make the caller pass argument names,
# allowing foo(param=False) but preventing foo(False)

def _checkNamedParameters(obj):
    if obj is not _enforceExplicitlyNamedParameters:
        raise ValueError('please name parameters for this function or method')

# allowedexts in the form ['png', 'gif']
def listchildrenUnsorted(dir, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, allowedexts=None):
    _checkNamedParameters(_ind)
    for filename in _os.listdir(dir):
        if not allowedexts or getext(filename) in allowedexts:
            yield filename if filenamesOnly else (dir + _os.path.sep + filename, filename)


if sys.platform.startswith('win'):
    exeSuffix = '.exe'
    listchildren = listchildrenUnsorted
else:
    exeSuffix = ''

    def listchildren(*args, **kwargs):
        return sorted(listchildrenUnsorted(*args, **kwargs))

def listdirs(dir, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, allowedexts=None):
    _checkNamedParameters(_ind)
    for full, name in listchildren(dir, allowedexts=allowedexts):
        if _os.path.isdir(full):
            yield name if filenamesOnly else (full, name)

def listfiles(dir, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, allowedexts=None):
    _checkNamedParameters(_ind)
    for full, name in listchildren(dir, allowedexts=allowedexts):
        if not _os.path.isdir(full):
            yield name if filenamesOnly else (full, name)

def recursefiles(root, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, allowedexts=None,
        fnFilterDirs=None, includeFiles=True, includeDirs=False, topdown=True, followSymlinks=False):
    _checkNamedParameters(_ind)
    assert isdir(root)
    
    for (dirpath, dirnames, filenames) in _os.walk(root, topdown=topdown, followlinks=followSymlinks):
        if fnFilterDirs:
            newdirs = [dir for dir in dirnames if fnFilterDirs(join(dirpath, dir))]
            dirnames[:] = newdirs
        
        if includeFiles:
            for filename in (filenames if sys.platform.startswith('win') else sorted(filenames)):
                if not allowedexts or getext(filename) in allowedexts:
                    yield filename if filenamesOnly else (dirpath + _os.path.sep + filename, filename)
        
        if includeDirs:
            yield getname(dirpath) if filenamesOnly else (dirpath, getname(dirpath))
    
def recursedirs(root, _ind=_enforceExplicitlyNamedParameters, filenamesOnly=False, fnFilterDirs=None,
        topdown=True, followSymlinks=False):
    _checkNamedParameters(_ind)
    return recursefiles(root, filenamesOnly=filenamesOnly, fnFilterDirs=fnFilterDirs, includeFiles=False,
        includeDirs=True, topdown=topdown, followSymlinks=followSymlinks)

class FileInfoEntryWrapper(object):
    def __init__(self, obj):
        self.obj = obj
        self.path = obj.path
        
    def is_dir(self, *args):
        return self.obj.is_dir(*args)
        
    def is_file(self, *args):
        return self.obj.is_file(*args)
        
    def short(self):
        return _os.path.split(self.path)[1]
        
    def size(self):
        return self.obj.stat().st_size
        
    def mtime(self):
        return self.obj.stat().st_mtime
    
    def metadatachangetime(self):
        assertTrue(not sys.platform.startswith('win'))
        return self.obj.stat().st_ctime
    
    def createtime(self):
        assertTrue(sys.platform.startswith('win'))
        return self.obj.stat().st_ctime

def recursefileinfo(root, recurse=True, followSymlinks=False, filesOnly=True):
    assertTrue(isPy3OrNewer)
    
    # scandir's resources are released in destructor,
    # do not create circular references holding it
    for entry in _os.scandir(root):
        if entry.is_dir(follow_symlinks=followSymlinks):
            if not filesOnly:
                yield FileInfoEntryWrapper(entry)
            if recurse:
                for subentry in recursefileinfo(entry.path, recurse=recurse,
                        followSymlinks=followSymlinks, filesOnly=filesOnly):
                    yield subentry
        
        if entry.is_file():
            yield FileInfoEntryWrapper(entry)

def listfileinfo(root, followSymlinks=False, filesOnly=True):
    return recursefileinfo(root, recurse=False,
        followSymlinks=followSymlinks, filesOnly=filesOnly)

def isemptydir(dir):
    return len(_os.listdir(dir)) == 0
    
def fileContentsEqual(f1, f2):
    import filecmp
    return filecmp.cmp(f1, f2, shallow=False)

# processes
def openDirectoryInExplorer(dir):
    assert isdir(dir), 'not a dir? ' + dir
    if sys.platform.startswith('win'):
        assert '^' not in dir and '"' not in dir, 'dir cannot contain ^ or "'
        runWithoutWaitUnicode([u'cmd', u'/c', u'start', u'explorer.exe', dir])
    else:
        for candidate in ['xdg-open', 'nautilus']:
            path = findBinaryOnPath(candidate)
            if path:
                args = [path, dir]
                run(args, shell=False, createNoWindow=False, throwOnFailure=False, captureOutput=False, wait=False)
                return
        raise RuntimeError('unable to open directory.')

def openUrl(s, filter=True):
    import webbrowser
    if s.startswith('http://'):
        prefix = 'http://'
    elif s.startswith('https://'):
        prefix = 'https://'
    else:
        assertTrue(False, 'url did not start with http')
    
    if filter:
        s = s[len(prefix):]
        s = s.replace('%', '%25')
        s = s.replace('&', '%26')
        s = s.replace('|', '%7C')
        s = s.replace('\\', '%5C')
        s = s.replace('^', '%5E')
        s = s.replace('"', '%22')
        s = s.replace("'", '%27')
        s = s.replace('>', '%3E')
        s = s.replace('<', '%3C')
        s = s.replace(' ', '%20')
        s = prefix + s
    webbrowser.open(s, new=2)


exeExt = {'.action': 1, '.apk': 1, '.app': 1, '.bat': 1, '.bin': 1, '.cmd': 1, '.com': 1,
    '.command': 1, '.cpl': 1, '.csh': 1, '.exe': 1, '.gadget': 1, '.inf1': 1, '.ins': 1, '.inx': 1,
    '.ipa': 1, '.isu': 1, '.job': 1, '.jse': 1, '.ksh': 1, '.lnk': 1, '.msc': 1, '.msi': 1,
    '.msp': 1, '.mst': 1, '.osx': 1, '.out': 1, '.paf': 1, '.pif': 1, '.prg': 1, '.ps1': 1,
    '.reg': 1, '.rgs': 1, '.run': 1, '.scr': 1, '.sct': 1, '.shb': 1, '.shs': 1, '.u3p': 1,
    '.vb': 1, '.vbe': 1, '.vbs': 1, '.vbscript': 1, '.workflow': 1, '.ws': 1, '.wsf': 1, '.wsh': 1}

warnExt = {'.0xe': 1, '.73k': 1, '.89k': 1, '.a6p': 1, '.ac': 1, '.acc': 1, '.acr': 1, '.actm': 1,
    '.ahk': 1, '.air': 1, '.app': 1, '.arscript': 1, '.as': 1, '.asb': 1, '.awk': 1, '.azw2': 1,
    '.beam': 1, '.btm': 1, '.cel': 1, '.celx': 1, '.chm': 1, '.cof': 1, '.crt': 1, '.dek': 1,
    '.dld': 1, '.dmc': 1, '.docm': 1, '.dotm': 1, '.dxl': 1, '.ear': 1, '.ebm': 1, '.ebs': 1,
    '.ebs2': 1, '.ecf': 1, '.eham': 1, '.elf': 1, '.es': 1, '.ex4': 1, '.exopc': 1, '.ezs': 1,
    '.fas': 1, '.fky': 1, '.fpi': 1, '.frs': 1, '.fxp': 1, '.gs': 1, '.ham': 1, '.hms': 1,
    '.hpf': 1, '.hta': 1, '.iim': 1, '.ipf': 1, '.isp': 1, '.jar': 1, '.js': 1, '.jsx': 1,
    '.kix': 1, '.lo': 1, '.ls': 1, '.mam': 1, '.mcr': 1, '.mel': 1, '.mpx': 1, '.mrc': 1,
    '.ms': 1, '.ms': 1, '.mxe': 1, '.nexe': 1, '.obs': 1, '.ore': 1, '.otm': 1, '.pex': 1,
    '.plx': 1, '.potm': 1, '.ppam': 1, '.ppsm': 1, '.pptm': 1, '.prc': 1, '.pvd': 1, '.pwc': 1,
    '.pyc': 1, '.pyo': 1, '.qpx': 1, '.rbx': 1, '.rox': 1, '.rpj': 1, '.s2a': 1, '.sbs': 1,
    '.sca': 1, '.scar': 1, '.scb': 1, '.script': 1, '.smm': 1, '.spr': 1, '.tcp': 1, '.thm': 1,
    '.tlb': 1, '.tms': 1, '.udf': 1, '.upx': 1, '.url': 1, '.vlx': 1, '.vpm': 1, '.wcm': 1,
    '.widget': 1, '.wiz': 1, '.wpk': 1, '.wpm': 1, '.xap': 1, '.xbap': 1, '.xlam': 1, '.xlm': 1,
    '.xlsm': 1, '.xltm': 1, '.xqt': 1, '.xys': 1, '.zl9': 1}

# from Duplicati's default_compressed_extensions.txt
# GNU Lesser General Public License v2.1
alreadyCompressedExt = {'.7z': 1, '.alz': 1, '.bz': 1, '.bz2': 1, '.cab': 1, '.cbr': 1, '.cbz': 1,
    '.deb': 1, '.dl_': 1, '.dsft': 1, '.ex_': 1, '.gz': 1, '.jar': 1, '.lzma': 1, '.mpkg': 1,
    '.msi': 1, '.msp': 1, '.msu': 1, '.pet': 1, '.rar': 1, '.rpm': 1, '.sft': 1, '.sfx': 1,
    '.sit': 1, '.sitx': 1, '.sy_': 1, '.tgz': 1, '.war': 1, '.wim': 1, '.xar': 1, '.xz': 1,
    '.zip': 1, '.zipx': 1, '.3gp': 1, '.aa3': 1, '.aac': 1, '.aif': 1, '.ape': 1, '.file': 1,
    '.flac': 1, '.gsm': 1, '.iff': 1, '.m4a': 1, '.mp3': 1, '.mpa': 1, '.mpc': 1, '.ra': 1,
    '.ogg': 1, '.wma': 1, '.wv': 1, '.sfark': 1, '.sfpack': 1, '.3g2': 1, '.3gp': 1, '.asf': 1,
    '.asx': 1, '.avi': 1, '.bsf': 1, '.divx': 1, '.dv': 1, '.f4v': 1, '.flv': 1, '.hdmov': 1,
    '.m2p': 1, '.m4v': 1, '.mkv': 1, '.mov': 1, '.mp4': 1, '.mpg': 1, '.mts': 1, '.ogv': 1,
    '.rm': 1, '.swf': 1, '.trp': 1, '.ts': 1, '.vob': 1, '.webm': 1, '.wmv': 1, '.wtv': 1,
    '.m2ts': 1, '.emz': 1, '.gif': 1, '.j2c': 1, '.jpeg': 1, '.jpg': 1, '.pamp': 1, '.pdn': 1,
    '.png': 1, '.pspimage': 1, '.tif': 1, '.dng': 1, '.cr2': 1, '.webp': 1, '.nef': 1,
    '.arw': 1, '.heic': 1, '.eot': 1, '.woff': 1, '.bik': 1, '.mpq': 1, '.chm': 1, '.docx': 1,
    '.docm': 1, '.dotm': 1, '.dotx': 1, '.epub': 1, '.graffle': 1, '.hxs': 1, '.max': 1,
    '.mobi': 1, '.mshc': 1, '.odp': 1, '.ods': 1, '.odt': 1, '.otp': 1, '.ots': 1, '.ott': 1,
    '.pages': 1, '.pptx': 1, '.pptm': 1, '.stw': 1, '.trf': 1, '.webarchive': 1, '.xlsx': 1,
    '.xlsm': 1, '.xlsb': 1, '.xps': 1, '.d': 1, '.dess': 1, '.i': 1, '.idx': 1, '.nupkg': 1,
    '.pack': 1, '.swz': 1, '.aes': 1, '.axx': 1, '.gpg': 1, '.hc': 1, '.kdbx': 1, '.tc': 1,
    '.tpm': 1, '.fve': 1, '.apk': 1, '.eftx': 1, '.sdg': 1, '.thmx': 1, '.vsix': 1, '.vsv': 1,
    '.wmz': 1, '.xpi': 1}

mostCommonImageExt = {'.gif': 1, '.jpg': 1, '.jpeg': 1, '.png': 1, '.bmp': 1, '.tif': 1,
    '.webp': 1}

def extensionPossiblyExecutable(s):
    '''Returns 'exe' if it looks executable,
    Returns 'warn' if it is a document type that can include embedded scripts,
    Returns False otherwise'''
    ext = getext(s, False)
    if ext in exeExt:
        return 'exe'
    elif ext in warnExt:
        return 'warn'
    else:
        return False

def findBinaryOnPath(name):
    def existsAsExe(dir, name):
        f = join(dir, name)
        if _os.path.isfile(f):
            return f
        if sys.platform.startswith('win'):
            if _os.path.isfile(f + '.exe'):
                return f + '.exe'
            if _os.path.isfile(f + '.cmd'):
                return f + '.cmd'
            if _os.path.isfile(f + '.com'):
                return f + '.com'
            if _os.path.isfile(f + '.bat'):
                return f + '.bat'
        return None
    
    # handle "./binaryname"
    if _os.sep in name:
        return existsAsExe('.', name) if existsAsExe('.', name) else None

    # handle "binaryname"
    for path in _os.environ["PATH"].split(_os.pathsep):
        if path and existsAsExe(path, name):
            return existsAsExe(path, name)

    return None

def hasherFromString(s):
    import hashlib
    if s == 'sha1':
        return hashlib.sha1()
    elif s == 'sha224':
        return hashlib.sha224()
    elif s == 'sha256':
        return hashlib.sha256()
    elif s == 'sha384':
        return hashlib.sha384()
    elif s == 'sha512':
        return hashlib.sha512()
    elif s == 'blake2b':
        return hashlib.blake2b()
    elif s == 'blake2s':
        return hashlib.blake2s()
    elif s == 'md5':
        return hashlib.md5()
    elif s == 'sha3_224':
        return hashlib.sha3_224()
    elif s == 'sha3_256':
        return hashlib.sha3_256()
    elif s == 'sha3_384':
        return hashlib.sha3_384()
    elif s == 'sha3_512':
        return hashlib.sha3_512()
    elif s == 'shake_128':
        return hashlib.shake_128()
    elif s == 'shake_256':
        return hashlib.shake_256()
    else:
        raise ValueError('Unknown hash type ' + s)

def computeHash(path, hasher='sha1', buffersize=0x40000):
    if hasher == 'crc32':
        import zlib
        crc = zlib.crc32(bytes(), 0)
        with open(path, 'rb') as f:
            while True:
                # update the hash with the contents of the file
                buffer = f.read(buffersize)
                if not buffer:
                    break
                crc = zlib.crc32(buffer, crc)
        crc = crc & 0xffffffff
        return '%08x' % crc
    else:
        if isinstance(hasher, str):
            hasher = hasherFromString(hasher)

        with open(path, 'rb') as f:
            while True:
                # update the hash with the contents of the file
                buffer = f.read(buffersize)
                if not buffer:
                    break
                hasher.update(buffer)
        return hasher.hexdigest()

def addAllToZip(root, zipPath, method='deflate', alreadyCompressedAsStore=False,
        pathPrefix='', recurse=True, **kwargs):
    import zipfile
    methodDict = dict(store=zipfile.ZIP_STORED, deflate=zipfile.ZIP_DEFLATED)
    try:
        methodDict['lzma'] = zipfile.ZIP_LZMA
    except AttributeError:
        pass  # lzma isn't always available, e.g. python 2.7
    def getMethod(s):
        if alreadyCompressedAsStore and getext(s, False) in alreadyCompressedExt:
            return zipfile.ZIP_STORED
        elif isinstance(method, anystringtype):
            return methodDict[method]
        else:
            return method

    assertTrue(not root.endswith('/') and not root.endswith('\\'))
    with zipfile.ZipFile(zipPath, 'a') as zip:
        if isfile(root):
            thisMethod = getMethod(root)
            zip.write(root, pathPrefix + files.getname(root), compress_type=thisMethod)
        elif isdir(root):
            itr = recursefiles(root, **kwargs) if recurse else listfiles(root, **kwargs)
            for f, short in itr:
                assertTrue(f.startswith(root))
                shortname = f[len(root) + 1:]
                thisMethod = getMethod(f)
                assertTrue(shortname)
                zip.write(f, pathPrefix + shortname, compress_type=thisMethod)
        else:
            raise RuntimeError("not found: " + root)

def windowsUrlFileGet(path):
    assertEq('.url', _os.path.splitext(path)[1].lower())
    s = readall(path, mode='r')
    lines = s.split('\n')
    for line in lines:
        if line.startswith('URL='):
            return line[len('URL='):]
    raise RuntimeError('no url seen in ' + path)

def windowsUrlFileWrite(path, url):
    assertTrue(len(url) > 0)
    assertTrue(not exists(path), 'file already exists at', path)
    try:
        url.encode('ascii')
    except e:
        if isinstance(e, UnicodeEncodeError):
            raise RuntimeError('can\'t support a non-ascii url' + url + ' ' + path)
        else:
            raise

    s = '[InternetShortcut]\n'
    s += 'URL=%s\n' % url
    writeall(path, s)

def runRsync(srcDir, destDir, deleteExisting, excludeFiles=None,
        excludeDirs=None, throwOnFailure=True, checkExist=True):
    if not excludeFiles:
        excludeFiles = []
    if not excludeDirs:
        excludeDirs = []
    if checkExist:
        assertTrue(isdir(srcDir), "not a dir", srcDir)
        assertTrue(isdir(destDir), "not a dir", destDir)

    args = []
    if sys.platform.startswith('win'):
        # we could use /r:0 to eliminate retries, but an
        # apparent bug in robocopy gives a success exit code,
        # so it's better to leave the current repeat-million-times
        # because at least it doesn't silently fail
        # (example: open a file for write with the same name as incoming directory)
        args.append('robocopy')
        args.append(srcDir)
        args.append(destDir)
        if deleteExisting:
            args.append('/MIR')
        args.append('/E')  # copy all, including empty dirs
        for ex in excludeFiles:
            args.append('/XF')
            args.append(ex)
        for ex in excludeDirs:
            args.append('/XD')
            args.append(ex)
    else:
        args.append('rsync')
        args.append('-az')
        if not srcDir.endswith('/'):
            # so that rsync won't put files into a subdir
            srcDir += '/'
        args.append(srcDir)
        args.append(destDir)
        if deleteExisting:
            args.append('--delete-after')
        for ex in excludeFiles + excludeDirs:
            args.append('--exclude')
            args.append(ex)
    
    retcode, stdout, stderr = run(args, throwOnFailure=False)
    isOk, status = runRsyncErrMap(retcode)
    if throwOnFailure and not isOk:
        raise Exception("Could not copy. " + str(retcode) +
            str(stdout) + str(stderr) + str(status))
    return retcode, stdout, stderr, status

def runRsyncErrMap(code, platform=None):
    if not platform:
        platform = sys.platform

    if platform.startswith('win'):
        status = ''
        if code & 0x1:
            status += "One or more files were copied successfully (that is, new files have arrived).\n"
            code = code & ~0x1
        if code & 0x2:
            status += "Extra files or directories were detected.\n"
            code = code & ~0x2
        if code & 0x4:
            status += "Mismatched files or directories were detected.\n"
            code = code & ~0x4
        if code & 0x8:
            status += "Some files or directories could not be copied.\n"
        if code & 0x10:
            status += "Serious error.\n"
        isOk = code == 0
        return (isOk, status)
    else:
        mapCode = {}
        mapCode[0] = (True, '')
        mapCode[1] = (False, "Syntax or usage error")
        mapCode[2] = (False, "Protocol incompatibility")
        mapCode[3] = (False, "Errors selecting input/output files, dirs")
        mapCode[4] = (False, "Action not supported, maybe by the client and not server")
        mapCode[5] = (False, "Error starting client-server protocol")
        mapCode[6] = (False, "Daemon unable to append to log-file")
        mapCode[10] = (False, "Error in socket I/O")
        mapCode[11] = (False, "Error in file I/O")
        mapCode[12] = (False, "Error in rsync protocol data stream")
        mapCode[13] = (False, "Errors with program diagnostics")
        mapCode[14] = (False, "Error in IPC code")
        mapCode[20] = (False, "Received SIGUSR1 or SIGINT")
        mapCode[21] = (False, "Some error returned by waitpid()")
        mapCode[22] = (False, "Error allocating core memory buffers")
        mapCode[23] = (False, "Partial transfer due to error")
        mapCode[24] = (False, "Partial transfer due to vanished source files")
        mapCode[25] = (False, "The --max-delete limit stopped deletions")
        mapCode[30] = (False, "Timeout in data send/receive")
        mapCode[35] = (False, "Timeout waiting for daemon connection")
        return mapCode.get(code, (False, "Unknown"))

# returns tuple (returncode, stdout, stderr)
def run(listArgs, _ind=_enforceExplicitlyNamedParameters, shell=False, createNoWindow=True,
        throwOnFailure=RuntimeError, stripText=True, captureOutput=True, silenceOutput=False,
        wait=True):
    import subprocess
    _checkNamedParameters(_ind)
    kwargs = {}
    
    if sys.platform.startswith('win') and createNoWindow:
        kwargs['creationflags'] = 0x08000000
    
    if captureOutput and not wait:
        raise ValueError('captureOutput implies wait')
    
    if throwOnFailure and not wait:
        raise ValueError('throwing on failure implies wait')
    
    retcode = -1
    stdout = None
    stderr = None
    
    if captureOutput:
        sp = subprocess.Popen(listArgs, shell=shell,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        
        comm = sp.communicate()
        stdout = comm[0]
        stderr = comm[1]
        retcode = sp.returncode
        if stripText:
            stdout = stdout.rstrip()
            stderr = stderr.rstrip()

    else:
        if silenceOutput:
            stdoutArg = open(_os.devnull, 'wb')
            stderrArg = open(_os.devnull, 'wb')
        else:
            stdoutArg = None
            stderrArg = None
        
        if wait:
            retcode = subprocess.call(listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs)
        else:
            subprocess.Popen(listArgs, stdout=stdoutArg, stderr=stderrArg, shell=shell, **kwargs)
        
    if throwOnFailure and retcode != 0:
        if throwOnFailure is True:
            throwOnFailure = RuntimeError

        exceptionText = 'retcode is not 0 for process ' + \
            str(listArgs) + '\nretcode was ' + str(retcode) + \
            '\nstdout was ' + str(stdout) + \
            '\nstderr was ' + str(stderr)
        raise throwOnFailure(getPrintable(exceptionText))
    
    return retcode, stdout, stderr
    
def runWithoutWaitUnicode(listArgs):
    # in Windows in Python2, non-ascii characters cause subprocess.Popen to fail.
    # https://bugs.python.org/issue1759845
    
    import subprocess
    if isPy3OrNewer or not sys.platform.startswith('win') or all(isinstance(arg, str) for arg in listArgs):
        # no workaround needed in Python3
        p = subprocess.Popen(listArgs, shell=False)
        return p.pid
    else:
        import winprocess
        import types
        if isinstance(listArgs, types.StringTypes):
            combinedArgs = listArgs
        else:
            combinedArgs = subprocess.list2cmdline(listArgs)
            
        combinedArgs = unicode(combinedArgs)
        executable = None
        close_fds = False
        creationflags = 0
        env = None
        cwd = None
        startupinfo = winprocess.STARTUPINFO()
        handle, ht, pid, tid = winprocess.CreateProcess(executable, combinedArgs,
            None, None,
            int(not close_fds),
            creationflags,
            env,
            cwd,
            startupinfo)
        ht.Close()
        handle.Close()
        return pid

def runWithTimeout(args, _ind=_enforceExplicitlyNamedParameters, shell=False, createNoWindow=True,
                  throwOnFailure=True, captureOutput=True, timeout=None, addArgs=None):
    addArgs = addArgs if addArgs else {}
    # todo: consolidate with run()
    assertTrue(throwOnFailure is True or throwOnFailure is False or throwOnFailure is None,
        "we don't yet support custom exception types set here, you can use CalledProcessError")

    retcode = -1
    stdout = None
    stderr = None
    if sys.platform.startswith('win') and createNoWindow:
        addArgs['creationflags'] = 0x08000000

    import subprocess
    ret = subprocess.run(args, capture_output=captureOutput, shell=shell, timeout=timeout,
        check=throwOnFailure, **addArgs)

    retcode = ret.returncode
    if captureOutput:
        stdout = ret.stdout
        stderr = ret.stderr
    return retcode, stdout, stderr
