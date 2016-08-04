
# UI for searching filenames
# the actual work is done by search_filenames.py

from scite_extend_ui import ScToolUIBase, ScApp, ScConst

sessionHistoryQueries = []
sessionHistoryDirs = []
childProcess = None

class SearchFilenames(ScToolUIBase):
    currentFocus = None
    def AddControls(self):
        self.searchTypes = {'Filename contains':'contains',
            'Wildcard expansion': 'wildcard', 
            'Regular expression':'regex'}
        
        self.AddLabel('Search for files named:')
        self.cmbQuery = self.AddCombo()
        self.AddRow()
        self.AddLabel('In directory:')
        self.cmbDir = self.AddCombo()
        self.AddRow()
        self.AddLabel('Search by:')
        self.cmbType = self.AddCombo()
        self.AddButton('Start Search', callback=self.OnSearch, default=True)
        self.AddButton('Cancel Search', callback=self.OnCancelSearch)
        self.AddButton('Close', closes=True)
        
    def OnOpen(self):
        self.SetList(self.cmbType, '\n'.join(key for key in self.searchTypes))
        self.Set(self.cmbType, 'Wildcard expansion')
        
        queries = '\n'.join(sessionHistoryQueries) + '\n' + ScApp.GetFileName()
        dirs = '\n'.join(sessionHistoryDirs) + '\n' + ScApp.GetFileDirectory()
        self.SetList(self.cmbQuery, queries)
        self.SetList(self.cmbDir, dirs)
        self.Set(self.cmbQuery, ScApp.GetFileName())
        self.Set(self.cmbDir, ScApp.GetFileDirectory())
        
    def OnSearch(self):
        # if user clicks Search, self.currentFocus is set to None. if they press Enter, self.currentFocus is current control.
        # we want Enter to start a search if either user clicked Search or "query" is the current control.
        userClickedButtonRatherThanPressingEnter = self.currentFocus is None
        if self.currentFocus == self.cmbQuery or userClickedButtonRatherThanPressingEnter:
            type = self.searchTypes.get(self.Get(self.cmbType), 'other')
            startProcess(type, self.Get(self.cmbDir), self.Get(self.cmbQuery))
        
    def OnCancelSearch(self):
        cancelProcess()
    
    def OnEvent(self, control, eventType):
        if eventType == ScConst.eventTypeFocusOut:
            self.currentFocus = None
        elif eventType == ScConst.eventTypeFocusIn:
            self.currentFocus = control

def startProcess(type, dir, query):
    import os, subprocess
    global childProcess
    if childProcess and childProcess.poll() is None:
        print('Please cancel existing search before starting new search.')
        return
    
    python = ScApp.GetProperty('customcommand.externalpython')
    if not os.path.isfile(python):
        print('''Could not find Python 2 installation, please open the file \n%s\n
and set the property \ncustomcommand.externalpythondir\n to the directory where Python 2 is installed.''' % 
        os.path.join(ScApp.GetSciteDirectory(), 'properties', 'python.properties'))
        return
    
    scriptLocation = os.path.join(ScApp.GetSciteDirectory(), 'tools_external', 'tools_search', 'search_filenames.py')
    if not os.path.isfile(scriptLocation):
        print('Could not find script at %s.' % scriptLocation)
        return
    
    args = [python, scriptLocation, type, dir, query, str(ScApp.GetProperty('SciTEWindowID'))]
    childProcess = subprocess.Popen(args, shell=False)

def cancelProcess():
    global childProcess
    if childProcess and childProcess.poll() is None:
        try:
            childProcess.kill()
            childProcess.wait()
            childProcess = None
        except OSError, e:
            print('Canceling search, ' + str(e))
        print('Canceled search.')
    else:
        print('Search not running.')

def DoSearchFilenames():
    toolstripui = SearchFilenames()
    toolstripui.Show()


