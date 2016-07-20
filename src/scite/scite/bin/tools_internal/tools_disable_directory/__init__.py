
# sometimes you might want to remind yourself that certain files shouldn't be edited lightly.
# set customcommand.disable_directory.disabled_directories in properties.
# when SciTE edits any files in these directories the background will be RED,
# a good reminder to think twice :)

def OnOpen(filename):
    onBufferShown()

def OnSwitchFile(filename):
    onBufferShown()

def getListFromPropertiesString(s):
    result = []
    s = s.replace('\r\n','\n').replace('\r', '\n')
    s = s.replace('|', '\n')
    lines = s.split('\n')
    return [line.strip() for line in lines if line.strip()]

def shouldWarn(currentFile, listDirs):
    from os.path import sep
    currentFileLower = currentFile.lower()
    for dir in listDirs:
        if currentFileLower.startswith(dir.lower() + sep):
            return True
    return False

def makeEverythingRed():
    # fortunately, it wears off as soon as the buffer is switched :)
    from scite_extend_ui import ScEditor, ScConst
    red = ScConst.MakeColor(255, 100, 100)
    for styleNumber in range(16):
        ScEditor.SetStyleBack(styleNumber, red)

def onBufferShown():
    from scite_extend_ui import ScApp
    currentFile = ScApp.GetFilePath()
    propKey = 'customcommand.disable_directory.disabled_directories'
    propMappings = ScApp.GetProperty(propKey)
    if not currentFile:
        return
    elif not propMappings:
        return
    else:
        listDirs = getListFromPropertiesString(propMappings)
        if shouldWarn(currentFile, listDirs):
            makeEverythingRed()
    
if __name__ == '__main__':
    from ben_python_common import assertEq
    input = r'c:\example\warn1'
    assertEq([r'c:\example\warn1'],
        getListFromPropertiesString(input))
    
    input = r'c:\example\warn1|c:\example\warn2'
    assertEq([r'c:\example\warn1', r'c:\example\warn2'],
        getListFromPropertiesString(input))
    
    input = r'c:\example\warn1  |  c:\example\warn2  || ||c:\example\warn3'.replace('||', '\n')
    assertEq([r'c:\example\warn1', r'c:\example\warn2', r'c:\example\warn3'],
        getListFromPropertiesString(input))
        
    listDirs = getListFromPropertiesString(r'c:\example\warn1|c:\example\warn2')
    assertEq(False, shouldWarn(r'', listDirs))
    assertEq(False, shouldWarn(r'c:\example', listDirs))
    assertEq(False, shouldWarn(r'c:\example\warn1', listDirs))
    assertEq(False, shouldWarn(r'c:\example\warn1_not_match', listDirs))
    
    assertEq(True, shouldWarn(r'c:\example\warn1\a.txt', listDirs))
    assertEq(True, shouldWarn(r'c:\example\warn1\d\d\d\a.txt', listDirs))
    assertEq(True, shouldWarn(r'c:\exAMPle\warn1\aCAPITAL.txt', listDirs))
    assertEq(True, shouldWarn(r'c:\example\warn2\a.txt', listDirs))
    
    