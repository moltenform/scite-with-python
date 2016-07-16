
from scite_extend_ui import *

def ChangeCasing():
    import changecasing
    return changecasing.DoChangeCasing()

def ChangeOrder():
    import changeorder
    return changeorder.DoChangeOrder()

def SplitJoin():
    import splitjoin
    return splitjoin.DoSplitJoin()
    
def InsertSequentialNumbers():
    import insertsequentialnumbers
    return insertsequentialnumbers.DoInsertSequentialNumbers()

def modifyTextInScite(fn):
    selected = ScEditor.GetSelText()
    if not selected:
        print('Nothing is selected.')
        return
    
    replaced = fn(selected)
    if replaced is None:
        return
        
    ScEditor.CmdBeginUndoAction()
    try:
        # Using Write() would work, but it would lose the selection
        # Using InsertText() on the other hand, selects the text afterwards, which looks nice
        ScEditor.CmdClear()
        ScEditor.InsertText(replaced, ScEditor.GetCurrentPos())
        ScEditor.SetAnchor(ScEditor.GetCurrentPos() + len(replaced))
    finally:
        ScEditor.CmdEndUndoAction()

