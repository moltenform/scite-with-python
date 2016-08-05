
import sys
from scite_extend_ui import ScApp

# inspired by SciTE-Ru's command 130

def OpenInNewWindow():
    from ben_python_common import files
    currentFile = ScApp.GetFilePath()
    if currentFile:
        ScApp.CmdClose()
        
        scite = 'scite.exe' if sys.platform.startswith('win') else 'scite'
        scite = files.join(ScApp.GetSciteDirectory(), scite)
        if not files.isfile(scite):
            print('Could not find scite.')
        else:
            args = [scite]
            args.append("-check.if.already.open=0")
            args.append("-save.session=0")
            args.append(currentFile)
            args.append("-goto:%s,%s" % 
                (ScApp.GetProperty('SelectionStartLine'), ScApp.GetProperty('SelectionStartColumn')))
            files.run(args, createNoWindow=False, captureoutput=False,
                    wait=False, throwOnFailure=None)
    else:
        print('Cannot OpenInNewWindow an unsaved document.')
