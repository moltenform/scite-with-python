
from ben_python_common import files, assertEq

# Sometimes you'll have two copies of a codebase in separate directories.
# The "switch_to_corresponding_dir" plugin lets you quickly switch from one directory's version of a file to another.
# for example, there are two files, c:\example\working\foo\bar\code.cpp and c:\example\master\foo\bar\code.cpp.
# if you set up a mapping c:\example\working|c:\example\master in the list defined by
#                           customcommand.switch_to_corresponding_dir.directorymappings,
# you can open the file c:\example\working\foo\bar\code.cpp
# run the "switch_to_corresponding_dir" plugin,
# and then the plugin opens the corresponding file, c:\example\master\foo\bar\code.cpp.

def getCandidates(currentFile, mappings):
    '''get a list of mapped files, if there are any found'''
    candidates = []
    currentFileLower = currentFile.lower()
    for srcdir, destdir in mappings:
        if currentFileLower.startswith(srcdir.lower() + files.sep):
            filejustpath = currentFile[len(srcdir):]
            destfile = destdir + filejustpath
            candidates.append(destfile)
    
    return candidates

def getMappingsFromString(s):
    '''mappings are stored in a list of (srcdir, destdir), preserves order unlike dict.'''
    result = []
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    s = s.replace('||', '\n')
    lines = s.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            first, second = line.split('|')
            result.append((first, second))
    return result

def getTargetFile(propMappings, currentFile):
    '''returns the first candidate that exists'''
    mappings = getMappingsFromString(propMappings)
    missings = ['']
    for candidate in getCandidates(currentFile, mappings):
        if files.isfile(candidate):
            return candidate
        else:
            missings.append('file missing at ' + candidate)
    print('no corresponding file found.' + '\n'.join(missings))

def SwitchToCorrespondingDir():
    '''look up the current file, tell SciTE to open the next file'''
    from scite_extend_ui import ScApp
    currentFile = ScApp.GetFilePath()
    propKey = 'customcommand.switch_to_corresponding_dir.directorymappings'
    propMappings = ScApp.GetProperty(propKey)
    if not currentFile:
        print('It doesn\'t appear that a file is open.')
    elif not propMappings or '|' not in propMappings:
        print('It doesn\'t appear that anything has been set in ' + propKey)
        print('Edit %s to see an example and provide a definition.' %
            files.join(ScApp.GetSciteDirectory(),
            'tools_internal/tools_switch_to_header/register.properties'))
    else:
        target = getTargetFile(propMappings, currentFile)
        if target:
            ScApp.OpenFile(target)

if __name__ == '__main__':
    exampleOneEntry = r'c:\example\working|c:\example\master'
    assertEq([(r'c:\example\working', r'c:\example\master')],
        getMappingsFromString(exampleOneEntry))
    
    exampleNewlinesAndSpace = r'''
||c:\example\working|c:\example\master
  ||c:\other_example\working|c:\other_example\master
'''
    assertEq([(r'c:\example\working', r'c:\example\master'),
        (r'c:\other_example\working', r'c:\other_example\master')],
        getMappingsFromString(exampleNewlinesAndSpace))
    
    exampleNoNewlines = r'||c:\example\working|c:\example\master' + \
        r'||c:\other_example\working|c:\other_example\master'
    assertEq([(r'c:\example\working', r'c:\example\master'),
        (r'c:\other_example\working', r'c:\other_example\master')],
        getMappingsFromString(exampleNoNewlines))
    
    map = getMappingsFromString(exampleOneEntry)
    assertEq([], getCandidates(r'c:\example', map))
    assertEq([], getCandidates(r'c:\example\working', map))
    assertEq([], getCandidates(r'c:\example\master\a.cpp', map))
    assertEq([], getCandidates(r'c:\example\working_not_a_match', map))
    assertEq([], getCandidates(r'c:\example\working_not_a_match\a.cpp', map))
    
    assertEq([r'c:\example\master\a.cpp'],
        getCandidates(r'c:\example\working\a.cpp', map))
    assertEq([r'c:\example\master\d\d\d\a.cpp'],
        getCandidates(r'c:\example\working\d\d\d\a.cpp', map))
    assertEq([r'c:\example\master' + '\\'],
        getCandidates(r'c:\example\working' + '\\', map))
    
    # test casing
    assertEq([r'c:\example\master\aFILE.cpp'],
        getCandidates(r'c:\exAMPle\working\aFILE.cpp', map))
    
    # test multiple matches
    mpMany = r'c:\e\ww|c:\e\mm||c:\e\w|c:\e\m1||c:\e\w|c:\e\m2||c:\e\w|c:\e\m3'
    assertEq([r'c:\e\m1\a.cpp', r'c:\e\m2\a.cpp', r'c:\e\m3\a.cpp'],
        getCandidates(r'c:\e\w\a.cpp', getMappingsFromString(mpMany)))
