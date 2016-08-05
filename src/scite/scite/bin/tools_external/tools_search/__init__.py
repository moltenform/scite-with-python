
# UI for searching filenames
# The actual work is done by search_filenames.py
# While __init__.py is run by SciTE's embedded Python, 
# search_filenames.py runs in a different context in an external Python process,
# so that searches can run smoothly in the background while the user does other work.

from scite_extend_ui import ScToolUIBase, ScApp, ScConst
from ben_python_common import RecentlyUsedList

sessionHistoryQueries = RecentlyUsedList(maxSize=50)
sessionHistoryDirs = RecentlyUsedList(maxSize=50)
childProcess = None

class SearchFilenames(ScToolUIBase):
    currentFocus = None
    def AddControls(self):
        self.searchTypes = {'Filename contains': 'contains',
            'Wildcard expansion': 'wildcard', 
            'Regular expression': 'regex'}
        
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
        
        queries = sessionHistoryQueries.getList() or [ScApp.GetFileName()]
        dirs = sessionHistoryDirs.getList() or [ScApp.GetFileDirectory()]
        self._refreshComboBoxHistory(queries, dirs)

    def OnSearch(self):
        type = self.searchTypes.get(self.Get(self.cmbType), 'other')
        startProcess(type, self.Get(self.cmbDir), self.Get(self.cmbQuery))
        sessionHistoryQueries.add(self.Get(self.cmbQuery))
        sessionHistoryDirs.add(self.Get(self.cmbDir))
        self._refreshComboBoxHistory(sessionHistoryQueries.getList(), sessionHistoryDirs.getList())
        
    def OnCancelSearch(self):
        cancelProcess()
    
    def _refreshComboBoxHistory(self, queries, dirs):
        self.SetList(self.cmbQuery, '\n'.join(queries))
        self.SetList(self.cmbDir, '\n'.join(dirs))
        self.Set(self.cmbQuery, queries[0])
        self.Set(self.cmbDir, dirs[0])

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

