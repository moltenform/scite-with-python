
# sometimes you might want to remind yourself that certain files shouldn't be edited lightly.
# set customcommand.disable_directory.disabled_directories in properties.
# when SciTE edits any files in these directories the background will be RED,
# a good reminder to think twice :)

class ShowWarnings(object):
    currentFilename = None
    mapFilenameToWarningStatus = None
    directoriesToWarn = None
    
    def __init__(self):
        from scite_extend_ui import ScApp
        self.mapFilenameToWarningStatus = dict()
        propKey = 'customcommand.disable_directory.disabled_directories'
        propMappings = ScApp.GetProperty(propKey)
        self.directoriesToWarn = getListFromPropertiesString(propMappings)
        
    def updateCurrentFilename(self):
        from scite_extend_ui import ScApp
        self.currentFileName = ScApp.GetFilePath()
    
    def showWarningIfNeeded(self):
        # first check the cache, for better performance
        needWarning = self.mapFilenameToWarningStatus.get(self.currentFileName, None)
        if needWarning is None:
            needWarning = shouldWarn(self.currentFileName, self.directoriesToWarn)
            self.mapFilenameToWarningStatus[self.currentFileName] = needWarning
            
        if needWarning:
            makeEverythingRed()
    
    def onClose(self):
        # remove from the cache, just to prevent the cache from growing indefinitely
        from scite_extend_ui import ScApp
        name = ScApp.GetFilePath()
        if name in self.mapFilenameToWarningStatus:
            del self.mapFilenameToWarningStatus[name]

# why do we need to track OnKey?
# we could do everything in OnOpen and OnFileChange, but the issue is that
# the OnOpen callback occurs too early, any coloring changes we make are
# reset immediately afterwards. So switching to a file would correctly set the colors,
# but the first time opening a file, the colors would not be seen.
# we'll use OnKey instead, even though it's not ideal.

def OnKey(key, shift, ctrl, alt):
    showWarnings.showWarningIfNeeded()
    
def OnFileChange():
    showWarnings.updateCurrentFilename()
    showWarnings.showWarningIfNeeded()

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
    from scite_extend_ui import ScEditor, ScConst
    # fortunately, it wears off as soon as the buffer is switched :)
    red = ScConst.MakeColor(255, 100, 100)
    for styleNumber in range(16):
        ScEditor.SetStyleBack(styleNumber, red)

showWarnings = ShowWarnings()

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
    
    