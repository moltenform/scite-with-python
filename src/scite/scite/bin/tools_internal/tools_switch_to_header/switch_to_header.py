
from ben_python_common import files, assertEq

def getCandidates(currentFile):
    sameLevel, filename = files.split(currentFile)
    beforeExt, ext = files.splitext(filename)
    upOneLevel, _ = files.split(sameLevel)
    upTwoLevels, _ = files.split(upOneLevel)
    ext = ext.lower()
    cppLikeExtensions = ['.cpp', '.cxx', '.c']
    if ext in ['.h']:
        # try parent directories and also ..\src directories, for all cppLikeExtensions
        result = []
        for ext in cppLikeExtensions:
            result.extend([files.join(sameLevel, beforeExt + ext),
                files.join(upOneLevel, beforeExt + ext),
                files.join(upTwoLevels, beforeExt + ext),
                files.join(files.join(upOneLevel, 'src'), beforeExt + ext),
                files.join(files.join(upTwoLevels, 'src'), beforeExt + ext)])
        return result
    elif ext in cppLikeExtensions:
        # try parent directories and also ..\include directories
        return [files.join(sameLevel, beforeExt + '.h'),
            files.join(upOneLevel, beforeExt + '.h'),
            files.join(upTwoLevels, beforeExt + '.h'),
            files.join(files.join(upOneLevel, 'include'), beforeExt + '.h'),
            files.join(files.join(upTwoLevels, 'include'), beforeExt + '.h')]
    elif ext in ['.py']:
        return [files.join(sameLevel, '__init__.py'),
            files.join(upOneLevel, '__init__.py')]
    elif ext in ['.htm', '.html']:
        return [files.join(sameLevel, 'index.htm'),
            files.join(sameLevel, 'index.html')]
    else:
        return []

def getTargetFile(currentFile):
    for candidate in getCandidates(currentFile):
        if files.isfile(candidate):
            return candidate
    print('No header file found.')

def SwitchToHeader():
    from scite_extend_ui import ScApp
    currentFile = ScApp.GetFilePath()
    if not currentFile:
        print('It doesn\'t appear that a file is open.')
    else:
        target = getTargetFile(currentFile)
        if target:
            ScApp.OpenFile(target)

if __name__ == '__main__':
    # use '/' as the path character
    def normalizeSep(s):
        return s.replace(files.sep, '/')
    
    # unit tests
    assertEq(['/path/to/a/doc.h',
        '/path/to/doc.h',
        '/path/doc.h',
        '/path/to/include/doc.h',
        '/path/include/doc.h'],
        [normalizeSep(s) for s in getCandidates('/path/to/a/doc.cpp')])
    
    assertEq(['/path/doc.h',
        '/doc.h',
        '/doc.h',
        '/include/doc.h',
        '/include/doc.h'],
        [normalizeSep(s) for s in getCandidates('/path/doc.cpp')])

    assertEq(['/path/to/a/doc.cpp',
        '/path/to/doc.cpp',
        '/path/doc.cpp',
        '/path/to/src/doc.cpp',
        '/path/src/doc.cpp',
        '/path/to/a/doc.cxx',
        '/path/to/doc.cxx',
        '/path/doc.cxx',
        '/path/to/src/doc.cxx',
        '/path/src/doc.cxx',
        '/path/to/a/doc.c',
        '/path/to/doc.c',
        '/path/doc.c',
        '/path/to/src/doc.c',
        '/path/src/doc.c'],
        [normalizeSep(s) for s in getCandidates('/path/to/a/doc.h')])

