# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import os, sys
import re
import fnmatch

def redirectStdoutToSciTE(scitewindow):
    # add tools_external to the path in order to import send_scite
    pathThisScript = os.path.realpath(__file__)
    pathParent1 = os.path.split(pathThisScript)[0]
    pathParent2 = os.path.split(pathParent1)[0]
    pathScite = os.path.split(pathParent2)[0]
    pathExternalTools = os.path.join(pathScite, 'tools_external')
    sys.path.append(pathExternalTools)
    try:
        import send_scite
    except ImportError:
        print('Could not load send_scite.')
        return
    
    import send_scite
    send_scite.SciTEUtils_RedirectStdout(scitewindow)

def checkArgs(dir, query):
    if not os.path.isdir(dir):
        print('Dir does not exist')
        return False
    
    if not query.strip():
        print('No query entered.')
        return False

    return True

def getReObj(type, query):
    if type == 'contains':
        regexString = re.escape(query)
    elif type == 'wildcard':
        # whole-string-match
        regexString = '^' + fnmatch.translate(query) + '$'
    elif type == 'regex':
        # whole-string-match
        regexString = '^' + query + '$'
    else:
        print('Unknown search type')
        return None
        
    # assuming ntfs or fat, but that's usually a good guess.
    caseSensitive = not sys.platform.startswith('win')
    try:
        return re.compile(regexString, 0 if caseSensitive else re.I)
    except re.error:
        print('Could not parse regular expression.')
        return None

def startSearch(dir, reObj):
    print('Searching...')
    for (path, dirs, files) in os.walk(dir):
        for filename in files:
            if reObj.search(filename):
                full = os.path.join(path, filename)
                print(full + ':1: ')
            
    print('Search complete.')

def go(type, dir, query, scitewindow):
    # first set up SendSciTE so we can communicate back to SciTE.
    if not scitewindow.isdigit() or int(scitewindow) == 0:
        print('scitewindow not valid.')
        sys.exit(1)

    assert sys.version_info[0] <= 2
    redirectStdoutToSciTE(int(scitewindow))
    query = unicode(query.decode('utf-8'))
    dir = unicode(dir.decode('utf-8'))
    if not checkArgs(dir, query):
        sys.exit(1)
    
    reObj = getReObj(type, query)
    if not reObj:
        sys.exit(1)
    
    startSearch(dir, reObj)
    
def tests():
    from code_search_definition_filters import assertEq
    reObj = getReObj('contains', 'abc')
    assertEq(True, not not reObj.search('abc'))
    assertEq(True, not not reObj.search('abc.txt'))
    assertEq(True, not not reObj.search('testabc.txt'))
    assertEq(False, not not reObj.search('ab'))
    assertEq(False, not not reObj.search('testabd.txt'))
    reObj = getReObj('wildcard', 'z*')
    assertEq(True, not not reObj.search('ziemassvetki'))
    assertEq(True, not not reObj.search('ziemassvetki.txt'))
    assertEq(False, not not reObj.search('not ziemassvetki.txt'))
    assertEq(False, not not reObj.search('not.txt'))
    reObj = getReObj('wildcard', '*')
    assertEq(True, not not reObj.search('anything.txt'))
    assertEq(True, not not reObj.search('a'))
    assertEq(True, not not reObj.search(''))
    reObj = getReObj('wildcard', '*.*')
    assertEq(False, not not reObj.search('noext'))
    assertEq(True, not not reObj.search('file.txt'))
    reObj = getReObj('wildcard', '*.txt')
    assertEq(True, not not reObj.search('file.txt'))
    assertEq(False, not not reObj.search('file.doc'))
    reObj = getReObj('wildcard', '*.tx*')
    assertEq(True, not not reObj.search('file.txa'))
    assertEq(True, not not reObj.search('file.txb'))
    assertEq(True, not not reObj.search('file.tx'))
    assertEq(False, not not reObj.search('file.doc'))
    assertEq(False, not not reObj.search('file'))
    reObj = getReObj('wildcard', 'abc')
    assertEq(True, not not reObj.search('abc'))
    assertEq(False, not not reObj.search('abcd'))
    assertEq(False, not not reObj.search('testabc.txt'))
    assertEq(False, not not reObj.search('test abc .txt'))
    reObj = getReObj('regex', 'abc')
    assertEq(True, not not reObj.search('abc'))
    assertEq(False, not not reObj.search('abcd'))
    assertEq(False, not not reObj.search('testabc.txt'))
    assertEq(False, not not reObj.search('test abc .txt'))
    reObj = getReObj('regex', 'abc*')
    assertEq(True, not not reObj.search('ab'))
    assertEq(True, not not reObj.search('abc'))
    assertEq(True, not not reObj.search('abccccc'))
    assertEq(False, not not reObj.search('abcd'))
    assertEq(False, not not reObj.search('testabc'))
    assertEq(False, not not reObj.search('testabcd'))

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        tests()
    elif len(sys.argv) == 5:
        _, type, dir, query, scitewindow = sys.argv
        go(type, dir, query, scitewindow)
    else:
        print('Received unsupported number of arguments.')
        sys.exit(1)
