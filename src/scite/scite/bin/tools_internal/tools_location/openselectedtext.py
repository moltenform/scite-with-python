
'''
base path is current file.
normalize / and \ for the os.
apply relative paths.
if a relative path and not found, keep going up directories until you find it.
if a relative path and not found, add all the extensions, starting with the one that you have

if a directory: files.openDirectoryInExplorer()


fall back to ScApp.CmdOpenSelected() which can handle links including:
    http: and https: urls
    file:///C:/filename.ext urls
    adding a open.suffix.
    line numbers
    ctags

'''

import os
import sys
from ben_python_common import files

# don't open files > 20mb
maxSize = 20 * 1024 * 1024

mapDirectoryToExtensionsToTry = {
    'ts': ['js'],
}

def isFilenameCharForSel(c, includeSpaces):
    # see SciTEBase::isfilenamecharforsel
    if len(c) != 1:
        return False
    else:
        delim = "\t\n\r\"$'*,;<>[]^`{|}" if includeSpaces else " \t\n\r\"$'*,;<>[]^`{|}"
        return c not in delim

def expandSelectionToEntireString(includeSpaces):
    from scite_extend_ui import ScApp
    pane = ScApp.GetActivePane()
    start = pane.GetSelectionStart()
    end = pane.GetSelectionEnd()
    
    if end - start > 1:
        # use an explicit selection
        return pane.PaneGetText(start, end)
    length = pane.GetLength()
    while start > 0 and isFilenameCharForSel(pane.PaneGetText(start - 1, start), includeSpaces):
        start -= 1
    while end < length and isFilenameCharForSel(pane.PaneGetText(end, end+1), includeSpaces):
        end += 1
    length = pane.GetLength()
    if start <= end and start >= 0 and end < length:
        return pane.PaneGetText(start, end)
    else:
        return ''

def existsAndIsSmallEnough(path):
    #~ print('|'+path+'|')
    return files.isfile(path) and files.getsize(path) < maxSize

def existsOrIsDir(path):
    # normalize path
    if sys.platform.startswith('win'):
        # support c backslash escapes
        path = path.replace('/', '\\').replace('\\\\', '\\')
    
    # remove trailing slash
    if path.endswith(files.sep):
        path = path[0:-1]
        
    if files.isdir(path):
        # go from import mydir to mydir/__init__.py
        if existsAndIsSmallEnough(files.join(path, '__init__.py')):
            return files.join(path, '__init__.py')
        index = [f for (f, short) in files.listfiles(path) if short.startswith('index') and existsAndIsSmallEnough(f)]
        if len(index):
            return index[0]
        # go from <a href="mydir/"> to mydir/index.html
        main = [f for (f, short) in files.listfiles(path) if short.startswith('main') and existsAndIsSmallEnough(f)]
        if len(main):
            return main[0]
        # otherwise, use the first file in the directory
        children = sorted([f for (f, short) in files.listfiles(path) if existsAndIsSmallEnough(f)])
        if len(children):
            return children[0]
    elif existsAndIsSmallEnough(path):
        return path

def tryInAncestors(currentParent, sBase):
    # try as-is
    if existsOrIsDir(sBase):
        return existsOrIsDir(sBase)
    # try relative path
    sTry = files.join(currentParent, sBase)
    if existsOrIsDir(sTry):
        return existsOrIsDir(sTry)
    # try relative path up once
    sTry = files.join(currentParent, '..', sBase)
    if existsOrIsDir(sTry):
        return existsOrIsDir(sTry)
    # try relative path up twice
    sTry = files.join(currentParent, '..', '..', sBase)
    if existsOrIsDir(sTry):
        return existsOrIsDir(sTry)
    # try relative path up three times
    sTry = files.join(currentParent, '..', '..', '..', sBase)
    if existsOrIsDir(sTry):
        return existsOrIsDir(sTry)

def findOpenTarget(curfile, s):
    if not s:
        return None
    currentParent = files.getparent(curfile)
    currentExt = files.getext(curfile)
    extensionsToTry = ['', currentExt]
    extensionsToTry.extend(mapDirectoryToExtensionsToTry.get(currentExt, []))
    # webpages/protocols are handled in CmdOpenSelected
    if s.startswith('http:') or s.startswith('https:') or s.startswith('ftp:') or s.startswith('ftps:') or s.startswith('file:'):
        return None

    # for each extension added:
    for addExt in extensionsToTry:
        if len(addExt):
            addExt = '.' + addExt
        for addOrReplace in (True, False):
            if addOrReplace:
                # try appending extension. try this first
                sBase = s + addExt
            else:
                # try replacing extension
                sBase = files.splitext(s)[0] + addExt
            
            #~ print('\n[[addExt=%s addOrReplace=%s sBase=%s]]'%(addExt, addOrReplace, sBase))
            sTry = tryInAncestors(currentParent, sBase)
            if sTry:
                return sTry
    
    if currentExt in ('py'):
        sTry = openSelectedForPython(curfile, s)
        if sTry:
            return sTry
    elif currentExt in ('c', 'cpp', 'cxx', 'h', 'hpp'):
        sTry = openSelectedForC(curfile, s)
        if sTry:
            return sTry
    elif currentExt in ('html', 'htm', 'css', 'php', 'shtml', 'js', 'ts'):
        sTry = openSelectedForWeb(curfile, s)
        if sTry:
            return sTry

def openSelectedForC(curfile, s):
    # sometimes headers are in a ../includes directory
    # this will check all uncle directories and child directories
    if s.endswith('.h') and not os.path.isabs(s):
        parent = files.getparent(files.getparent(curfile))
        for f, short in files.recursedirs(parent):
            sBase = files.join(f, s)
            if existsOrIsDir(sBase):
                return existsOrIsDir(sBase)
    
def openSelectedForWeb(curfile, s):
    # an absolute web path might point to something local, so let's omit a starting slash
    # treating /dir/ as /dir/index.html will be done by tryInAncestors, see existsOrIsDir
    currentParent = files.getparent(curfile)
    if s.startswith('/'):
        sBase = s[1:]
        sTry = tryInAncestors(currentParent, sBase)
        if sTry:
            return sTry

def openSelectedForPython(curfile, s):
    from scite_extend_ui import ScApp
    currentParent = files.getparent(curfile)
    if '/' in s or '.' in s or ' ' in s:
        return
    
    # maybe it's a directory module? that would already be checked by existsOrIsDir.
    # maybe it's in standard library or a site package
    py = ScApp.GetProperty("command.go.*.py") or ''
    if py.startswith('"'):
        py = py.split('"')[1]
    else:
        py = py.split(' ')[0]
    
    if os.path.isabs(py) and files.isdir(files.getparent(py)):
        sTry = files.join(files.getparent(py), 'Lib', s)
        if existsOrIsDir(sTry):
            return existsOrIsDir(sTry)
        if existsOrIsDir(sTry + '.py'):
            return existsOrIsDir(sTry + '.py')
        sTry = files.join(files.getparent(py), 'Lib', 'site-packages', s)
        if existsOrIsDir(sTry):
            return existsOrIsDir(sTry)
        if existsOrIsDir(sTry + '.py'):
            return existsOrIsDir(sTry + '.py')

def openSelectedText():
    from scite_extend_ui import ScApp
    
    # try including spaces
    curfile = ScApp.GetFilePath() or 'placeholder.' + ScApp.GetProperty("default.file.ext") or 'placeholder.txt'
    
    # paths should be relative to current file
    savedDir = os.getcwd()
    if ScApp.GetFilePath():
        os.chdir(files.getparent(ScApp.GetFilePath()))
    try:
        target = findOpenTarget(curfile, expandSelectionToEntireString(True))
        if target:
            ScApp.OpenFile(target)
        else:
            # try again, not including spaces
            target = findOpenTarget(curfile, expandSelectionToEntireString(False))
            if target:
                ScApp.OpenFile(target)
            else:
                # fall back to default open-selection
                ScApp.CmdOpenSelected()
    finally:
        os.chdir(savedDir)

