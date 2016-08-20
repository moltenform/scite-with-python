# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

def GetNumberOfLinesInSelection():
    from scite_extend_ui import ScEditor
    startLine = ScEditor.LineFromPosition(ScEditor.GetSelectionStart())
    endLine = ScEditor.LineFromPosition(ScEditor.GetSelectionEnd())
    return 1 + (endLine - startLine)

def MoveLinesUp():
    from scite_extend_ui import ScEditor
    if ScEditor.GetSelections() <= 1:
        numberOfLines = GetNumberOfLinesInSelection()
        if numberOfLines <= 1:
            ScEditor.LineTranspose()
            ScEditor.LineUp()
        else:
            ScEditor.BeginUndoAction()
            try:
                moveManyLinesUp(numberOfLines)
            finally:
                ScEditor.EndUndoAction()
    else:
        print('this tool does not support multiple selections')

def MoveLinesDown():
    from scite_extend_ui import ScEditor
    if ScEditor.GetSelections() <= 1:
        numberOfLines = GetNumberOfLinesInSelection()
        if numberOfLines <= 1:
            ScEditor.LineDown()
            ScEditor.LineTranspose()
            ScEditor.LineDown()
            ScEditor.LineUp()
        else:
            ScEditor.BeginUndoAction()
            try:
                moveManyLinesDown(numberOfLines)
            finally:
                ScEditor.EndUndoAction()
    else:
        print('this tool does not support multiple selections')

def moveManyLinesUp(numberOfLines):
    from scite_extend_ui import ScEditor
    if ScEditor.LineFromPosition(ScEditor.GetSelectionStart()) == 0:
        return
    
    # go to first line
    pos = ScEditor.GetSelectionStart()
    ScEditor.SetSelectionEnd(pos)
    
    # move all lines up one
    ScEditor.Home()
    for i in range(numberOfLines):
        ScEditor.LineTranspose()
        ScEditor.LineDown()
    
    # restore selection
    ScEditor.LineUp()
    ScEditor.CharLeft()
    for i in range(numberOfLines - 1):
        ScEditor.LineUpExtend()
    ScEditor.HomeExtend()

def moveManyLinesDown(numberOfLines):
    from scite_extend_ui import ScEditor
    lastLineInDocument = ScEditor.LineFromPosition(ScEditor.GetTextLength())
    if ScEditor.LineFromPosition(ScEditor.GetSelectionEnd()) >= lastLineInDocument - 1:
        return
    
    # go to last line
    pos = ScEditor.GetSelectionEnd()
    ScEditor.SetSelectionStart(pos)
    
    # move all lines down one
    ScEditor.LineDown()
    for i in range(numberOfLines):
        ScEditor.LineTranspose()
        ScEditor.LineUp()
    
    # select all the lines
    ScEditor.LineDown()
    ScEditor.Home()
    for i in range(numberOfLines):
        ScEditor.LineDownExtend()
    ScEditor.CharLeftExtend()

# sample text for manual testing:

# 1
# 2
# 3
# 4
# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# 1
# 2
# 3
# 4

# 1
# 2
# 3
# 4
# Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# 1
# 2
# 3
# 4

# 1
# 2
# 3
# 4
# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33
# 1
# 2
# 3
# 4

# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# Test44Test44Test44Test44
# Test1
# Test2
# Test3
# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# Test44Test44Test44Test44

# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# Test44Test44Test44Test44
# T1
# Test2
# Test3
# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# Test44Test44Test44Test44

# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# Test44Test44Test44Test44
# Test1
# Test2
# T3
# Test11Test11Test11Test11
# Test22Test22Test22Test22
# Test33Test33Test33Test33
# Test44Test44Test44Test44
