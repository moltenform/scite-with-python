
import os
import sys
import subprocess

from code_search_definition_filters import getFilterObject, filterLine

def getSciteInternalSearchArgs(wholeWord, matchCase,
    includeHidden, includeBinary, filetypes, searchTerm):
    s = ''
    s += 'w' if wholeWord else '~'
    s += 'c' if matchCase else '~'
    s += 'd' if includeHidden else '~'
    s += 'b' if includeBinary else '~'
    return ['-grep', s, filetypes, searchTerm]

def runProcessAndFilterStdout(args, filterObj, action, extension, stringWindowId):
    recordedResults = []
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if line:
            if filterLine(recordedResults, line, filterObj):
                print(line.rstrip())
                sys.stdout.flush()
        else:
            break
            
    if len(recordedResults) == 1 and action != 'any_whole_word':
        # if there's one result, automatically open it
        sciteDir = os.path.split(args[0])[0]
        sendSciteCmdNavigateToFirstResult(sciteDir, stringWindowId, filterObj, recordedResults[0])

def sendSciteCmdNavigateToFirstResult(sciteDir, stringWindowId, filterObj, result):
    if not sys.platform.startswith('win') or not stringWindowId:
        return
    
    try:
        windowId = int(stringWindowId)
    except ValueError:
        return False
    
    sys.path.append(os.path.join(sciteDir, 'tools_external'))
    try:
        import send_scite
    except ImportError:
        print('Could not load send_scite.')
        return
    
    filepath, lineno, match = result
    if not os.path.isfile(filepath):
        return
    
    goto = str(lineno)
    columnPos = match.find(filterObj.searchTerm)
    if columnPos != -1:
        goto += ',' + str(columnPos)
    
    # we'd use CmdNextMsg, except it's too early to call that because our own script is still executing
    send_scite.sendSciteMessage(windowId, 'open:' + filepath)
    send_scite.sendSciteMessage(windowId, 'goto:' + goto)
    
def goSearch(pathScite, dir, searchTerm, stringWindowId, action, extension):
    filterObj, filetypes = getFilterObject(action, extension, searchTerm)
    if filterObj:
        args = getSciteInternalSearchArgs(wholeWord=True, matchCase=True,
            includeHidden=False, includeBinary=False, filetypes=filetypes, searchTerm=searchTerm)
        args.insert(0, pathScite)
            
        os.chdir(dir)
        runProcessAndFilterStdout(args, filterObj, action, extension, stringWindowId)

def applyDirDepth(dir, depth):
    for i in range(depth):
        dir = os.path.split(dir)[0]
    return dir

def go(filepath, searchTerm, dirDepthString, stringWindowId, action):
    import re
    if not filepath:
        print('File not found')
        return
    
    searchTerm = searchTerm.strip()
    if not searchTerm:
        print('No word selected')
        return
    
    if not re.match(r'^[a-zA-Z0-9_]+$', searchTerm):
        print('Search term should be consist of only alphanumeric characters.')
        return
    
    pathThisScript = os.path.realpath(__file__)
    pathScite = os.path.join(applyDirDepth(pathThisScript, 3), 'scite.exe')
    if not os.path.isfile(pathScite):
        print('Could not find scite.exe, expected at %s.' % pathScite)
        return
    
    if not dirDepthString:
        dirDepthString = '0'
    
    try:
        dirDepth = int(dirDepthString)
    except ValueError:
        print('directory depth must be an integer, check value of customcommand.code_search_c_declaration.directory_depth.')
        return
    
    if dirDepth > 0:
        print('Searching %d level(s) of parent directories.' % dirDepth)
    
    dir = os.path.split(filepath)[0]
    dir = applyDirDepth(dir, dirDepth)
    extension = os.path.splitext(filepath)[1].lower()
    goSearch(pathScite, dir, searchTerm, stringWindowId, action, extension)
    

def tests():
    from ben_python_common import assertEq
    assertEq(r'C:\d1\d2\d3', applyDirDepth(r'C:\d1\d2\d3', 0))
    assertEq(r'C:\d1\d2', applyDirDepth(r'C:\d1\d2\d3', 1))
    assertEq(r'C:\d1', applyDirDepth(r'C:\d1\d2\d3', 2))
    assertEq('C:\\', applyDirDepth(r'C:\d1\d2\d3', 3))
    assertEq('C:\\', applyDirDepth(r'C:\d1\d2\d3', 4))

if __name__ == '__main__':
    if len(sys.argv) == 6:
        _, filepath, searchTerm, dirDepth, stringWindowId, action = sys.argv
        go(filepath, searchTerm, dirDepth, stringWindowId, action)
    elif len(sys.argv) <= 1:
        tests()
    else:
        print('Received incorrect number of args.')
