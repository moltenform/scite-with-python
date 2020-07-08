
from scite_extend_ui import ScApp, ScEditor, ScConst

# if this is turned on, you'll be sent to the end or start of the file, which was less convenient to use.
okToBeTakenToEndOfFile = False

def GetPositionOfStartOfBlock(posToWorkWith):
    bitmask = ScConst.SC_FOLDLEVELNUMBERMASK
    previousLine = ScEditor.LineFromPosition(posToWorkWith)
    previousLevel = ScEditor.GetFoldLevel(previousLine) & bitmask
    line = previousLine
    
    # search for a line where the level is less than the current level.
    found = False
    while line > 0:
        if (ScEditor.GetFoldLevel(line) & bitmask) < previousLevel:
            found = True
            break
        line -= 1
    
    if not found and not okToBeTakenToEndOfFile:
        return None, None
    else:
        return line, ScEditor.PositionFromLine(line)

def GoUp(addToSelection):
    previousSelStart = ScEditor.GetSelectionStart()
    previousSelEnd = ScEditor.GetSelectionEnd()
    line, newpos = GetPositionOfStartOfBlock(previousSelStart)
    if line is None:
        return
    
    ScEditor.GotoPos(newpos)
    if addToSelection:
        ScEditor.SetSelectionStart(ScEditor.PositionFromLine(line))
        ScEditor.SetSelectionEnd(previousSelEnd)
    else:
        ScEditor.LineEnd()

def GoDown(addToSelection):
    bitmask = ScConst.SC_FOLDLEVELNUMBERMASK
    lastLineInDocument = ScEditor.LineFromPosition(ScEditor.GetTextLength())
    previousSelStart = ScEditor.GetSelectionStart()
    previousSelEnd = ScEditor.GetSelectionEnd()
    
    # why move the caret down a line? for the case where the current line is "while(condition) {"
    # it's convenient to act as if the caret were inside the body of this block, even though
    # technically it is outside.
    # this doesn't work as well for blocks that are only two lines long, preventing
    # Ctrl+Shift+J, Ctrl+Shift+K from selecting the entire block as expected, but the tool works well enough for now.
    ScEditor.LineDown()
    
    startScopeLine, startScopePos = GetPositionOfStartOfBlock(ScEditor.GetSelectionStart())
    if startScopeLine is None:
        ScEditor.SetSelectionStart(previousSelStart)
        ScEditor.SetSelectionEnd(previousSelEnd)
        return
    
    # fold levels are apparently not determined until user views that text.
    # call EnsureChildrenVisible, in order to both compute fold levels for the rest of the scope and expand everything.
    ScEditor.SetCurrentPos(startScopePos)
    ScApp.CmdExpandEnsureChildrenVisible()
    
    startScopeLevel = ScEditor.GetFoldLevel(startScopeLine) & bitmask
    line = startScopeLine + 1
    found = False
    while line < lastLineInDocument:
        if (ScEditor.GetFoldLevel(line + 1) & bitmask) <= startScopeLevel:
            found = True
            break
        line += 1
    
    if not found and not okToBeTakenToEndOfFile:
        ScEditor.SetSelectionStart(previousSelStart)
        ScEditor.SetSelectionEnd(previousSelEnd)
        return
    
    ScEditor.GotoPos(ScEditor.PositionFromLine(line))
    ScEditor.LineEnd()
    if addToSelection:
        endPos = ScEditor.GetSelectionEnd()
        ScEditor.SetSelectionStart(previousSelStart)
        ScEditor.SetSelectionEnd(endPos)


