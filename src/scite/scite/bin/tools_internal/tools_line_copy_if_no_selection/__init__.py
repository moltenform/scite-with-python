

def hasSelection(pane):
    return not pane.GetSelectionEmpty()

def getCurrentPane():
    from scite_extend_ui import ScEditor, ScOutput
    if ScEditor.GetFocus():
        return ScEditor
    elif ScOutput.GetFocus():
        return ScOutput
    else:
        return None

def doesStringBeginAndEndWithNewlines(s):
    if not s:
        return False
    
    if len(s.replace('\r\n', '\n')) < 2:
        # just a matter of preference, but let's not accept a single newline.
        return False
    
    # considered rejecting if there are inner newlines,
    # but decided it's ok to have inner newlines, since it might be convenient,
    # even if the string didn't come from DoLineCutIfNoSelection.
    return s[0] in ('\r', '\n') and s[-1] in ('\r', '\n')

def selectEntireLineAndPrecedingNewline(pane):
    pane.Home()
    pane.CharLeft()
    pane.CharRightExtend()
    pane.LineEndExtend()
    pane.CharRightExtend()
    
def DoLineCutIfNoSelection():
    '''if there's no selection, cut the entire line'''
    pane = getCurrentPane()
    if pane and not hasSelection(pane):
        pane.BeginUndoAction()
        try:
            # let's get the entire line, with a starting and ending newline
            selectEntireLineAndPrecedingNewline(pane)
            pane.Cut()
            
            # re-add the newline that we just removed
            pane.PaneWrite(pane.Utils.GetEolCharacter())
        finally:
            pane.EndUndoAction()
            
    else:
        from scite_extend_ui import ScApp
        ScApp.CmdCut()

def DoLineCopyIfNoSelection():
    '''if there's no selection, copy the entire line'''
    pane = getCurrentPane()
    if pane and not hasSelection(pane):
        # let's get the entire line, with a starting and ending newline
        position = pane.GetCurrentPos()
        selectEntireLineAndPrecedingNewline(pane)
        pane.Copy()
        pane.SetEmptySelection(position)
    else:
        from scite_extend_ui import ScApp
        ScApp.CmdCopy()

def DoLinePasteIfHasLine():
    '''if there's no selection,
    and the clipboard contents start and end with newlines,
    then insert the text *above* the current line instead of inside the current line.'''
    pane = getCurrentPane()
    if pane and not hasSelection(pane):
        runCustomPaste(pane)
    else:
        from scite_extend_ui import ScApp
        ScApp.CmdPaste()


def runCustomPaste(pane):
    '''first, run paste. if the contents look normal, leave the text there and exit.
    or if contents start and end with newlines, move them above the current line.
    note: should only call this function if there is no selection.'''
    
    prevPos = pane.GetCurrentPos()
    pane.BeginUndoAction()
    try:
        # considered using ben_python_common.getClipboardText(), but when running
        # in the SciTE context and text was copied from same process, it failed to work.
        pane.Paste()
        resultingPos = pane.GetCurrentPos()
        if prevPos == resultingPos:
            # nothing was pasted, maybe the clipboard was empty
            return
        
        pastedText = pane.PaneGetText(prevPos, resultingPos)
        if doesStringBeginAndEndWithNewlines(pastedText):
            # let's remove the inserted text, move to the preceding line, and call paste again.
            pane.PaneRemoveText(prevPos, resultingPos)
            pane.Home()
            posBeforePasted = pane.GetCurrentPos()
            pane.Paste()
            
            # remove the initial newline
            if pastedText.startswith('\r\n'):
                countCharsToDelete = 2
            else:
                countCharsToDelete = 1
            
            pane.PaneRemoveText(posBeforePasted, posBeforePasted + countCharsToDelete)
            
            # move the caret to the end of the line
            pane.CharLeft()
        else:
            # leave the pasted text here, since the user wanted to paste anyways.
            pass
        
    finally:
        pane.EndUndoAction()

        
if __name__ == '__main__':
    from ben_python_common import assertEq
    
    assertEq(False, doesStringBeginAndEndWithNewlines(None))
    assertEq(False, doesStringBeginAndEndWithNewlines(''))
    assertEq(False, doesStringBeginAndEndWithNewlines('\n'))
    assertEq(False, doesStringBeginAndEndWithNewlines('\r\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\n\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines(u'\n\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\r\n\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\n\r\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\na\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\n a \n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\r\na\r\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\r\n a \r\n'))
    assertEq(True, doesStringBeginAndEndWithNewlines('\r\n a\r\na \r\n'))
    