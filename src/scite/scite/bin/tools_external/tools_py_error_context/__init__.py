# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

def WritePrintStatement(word):
    from scite_extend_ui import ScEditor
    whatToWrite = "print '''%s''', %s"%(word, word)
    
    ScEditor.BeginUndoAction()
    try:
        ScEditor.LineEnd()
        ScEditor.NewLine()
        ScEditor.PaneWrite(whatToWrite)
    finally:
        ScEditor.EndUndoAction()

def AddPrintStatement():
    from scite_extend_ui import ScApp, ScEditor
    if ScEditor.GetFocus() and ScEditor.GetSelections() <= 1:
        sel = ScEditor.GetSelectedText()
        if sel and sel.strip():
            if '\n' in sel or '\r' in sel:
                print('Select within one line.')
            else:
                WritePrintStatement(sel)
        else:
            word = ScApp.GetProperty('CurrentWord')
            if word and word.strip():
                WritePrintStatement(word)
