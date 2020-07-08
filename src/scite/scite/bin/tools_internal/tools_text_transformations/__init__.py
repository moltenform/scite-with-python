# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from changecasing import DoChangeCasing
from changelines import DoChangeLines
from movelines import MoveLinesUp, MoveLinesDown

def modifyTextInScite(fn):
    from scite_extend_ui import ScEditor
    selected = ScEditor.GetSelectedText()
    if not selected:
        print('Nothing is selected.')
        return
    
    replaced = fn(selected)
    if replaced is None:
        return
        
    ScEditor.BeginUndoAction()
    try:
        # Using Write() would work, but it would lose the selection
        # Using InsertText() on the other hand, selects the text afterwards, which looks nice
        ScEditor.Clear()
        p = ScEditor.GetCurrentPos()
        ScEditor.InsertText(p, replaced)
        # This method scrolls the view to make caret visible
        ScEditor.SetSel(p, p + len(replaced))
    finally:
        ScEditor.EndUndoAction()

def modifyTextSupportsMultiSelection(fn, resetSelection):
    from scite_extend_ui import ScEditor
    sels = ScEditor.GetMultiSelect()
    if not sels:
        print('Nothing is selected.')
        return
    
    firstChar = sels[0][0]
    ScEditor.BeginUndoAction()
    try:
        for b in sels:
            txt = ScEditor.PaneGetText(b[0], b[1])
            newtxt = fn(txt)
            ScEditor.PaneRemoveText(b[0], b[1])
            ScEditor.PaneInsertText(newtxt, b[0])
        if resetSelection:
            ScEditor.SetSel(firstChar, firstChar)
    finally:
        ScEditor.EndUndoAction()

