
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
        ScEditor.InsertText(ScEditor.GetCurrentPos(), replaced)
        ScEditor.SetAnchor(ScEditor.GetCurrentPos() + len(replaced))
    finally:
        ScEditor.EndUndoAction()

