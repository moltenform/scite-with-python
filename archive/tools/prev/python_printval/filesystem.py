
import os,shutil
rename = os.rename
delete = os.unlink
exists = os.path.exists
join = os.path.join
split = os.path.split
isdir = os.path.isdir
is_dir = os.path.isdir
copy = shutil.copy
getsize = os.path.getsize
copytree = shutil.copytree
move = shutil.move
rmtree = shutil.rmtree
abspath = shutil.abspath


def blistfiles(s, pattern='*.*'):
    import fnmatch
    ls = os.listdir(s)
    for item in ls:
        if fnmatch.fnmatch(item, pattern):
            yield (join(s,item), item)

def blistfilesrecurse(s, fnAllowDir=None):
    for (dirpath, dirnames, filenames) in os.walk(s):
        if fnAllowDir:
            newdirs = []
            for dir in dirnames:
                if fnAllowDir(join(dirpath,dir), dir):
                    newdirs.append(dir)
            dirnames[:] = newdirs
        
        for file in filenames:
            yield (join(dirpath, file), file)

def blistdirsrecurse(s, fnAllowDir=None):
    for (dirpath, dirnames, filenames) in os.walk(s):
        if fnAllowDir:
            newdirs = []
            for dir in dirnames:
                if fnAllowDir(join(dirpath,dir), dir):
                    newdirs.append(dir)
            dirnames[:] = newdirs
        yield (dirpath, os.path.split(dirpath)[1])

def readfile(s, mode='r'):
    f=open(s,mode)
    txt = f.read()
    f.close()
    return txt
def writefile(s, txt, mode='w'):
    f=open(s,mode)
    f.write(txt)
    f.close()
    
    
def file_modtime(s): return os.stat(s).ST_MTIME
def file_acctime(s): return os.stat(s).ST_ATIME
def file_ctime(s): return os.stat(s).ST_CTIME

def runGetStdout(listArgs, shell=False):
    sp = subprocess.Popen(listArgs, shell, stdout=subprocess.PIPE)
    text = sp.communicate()[0]
    return text.rstrip(), sp.returncode

def runGetRetcode(listArgs, shell=False):
    sp = subprocess.Popen(listArgs, shell)
    sp.wait()
    return sp.returncode

def replacewholeword(starget, sin, srep):
    import re
    sin = '\\b'+re.escape(sin)+'\\b'
    return re.sub(sin, srep, starget)

def re_replace(starget, sre, srep):
    import re
    return re.sub(sre, srep, starget)


def getClipboardText():
    from Tkinter import Tk
    r = Tk()
    r.withdraw()
    s = r.clipboard_get()
    r.destroy()
    return s

def setClipboardText(s):
    from Tkinter import Tk
    text = str(s)
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.destroy()

if __name__=='__main__':
    for f in blistfiles('.'):
        print(f)
    print('--')
    for f in blistfiles('.','*.pyc'):
        print(f)
    print('--')
    for f in blistfilesrecurse('.'):
        print(f)
    print('--')
    for f in blistdirsrecurse('.'):
        print(f)
    assert replacewholeword('and a fad pineapple a da', 'a', 'A')=='and A fad pineapple A da'
    assert re_replace('and a fad pineapple a da', '[abcdef]a', 'GA')=='and a GAd pinGApple a GA'
    setClipboardText('pineapple')
    assert getClipboardText()=='pineapple'