# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import sys
from scite_extend_ui import ScApp

# inspired by SciTE-Ru's command 130

def OpenInNewWindow(closeCurrent=True):
    from ben_python_common import files
    currentFile = ScApp.GetFilePath()
    
    if sys.platform.startswith('win'):
        scite = files.join(ScApp.GetSciteDirectory(), 'SciTE.exe')
    else:
        scite = '/usr/bin/SciTE_with_python'
        if not files.isfile(scite):
            scite = '/usr/local/bin/SciTE_with_python'
    
    if not files.isfile(scite):
        print('Could not find scite.')
        return
    else:
        args = [scite]
        args.append("-check.if.already.open=0")
        args.append("-save.session=0")
    
    # if there's an untitled document open, just start a new SciTE instance
    # otherwise, start a new SciTE instance and open the current file+line
    if currentFile and closeCurrent:
        ScApp.CmdClose()
        args.append(currentFile)
        args.append("-goto:%s,%s" %
            (ScApp.GetProperty('SelectionStartLine'), ScApp.GetProperty('SelectionStartColumn')))
            
    files.run(args, createNoWindow=False, captureoutput=False,
        wait=False, throwOnFailure=None)
        
def OpenNewDocInNewWindow():
    OpenInNewWindow(closeCurrent=False)
