# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from scite_extend_ui import *
from ben_python_common import assertEq, assertException, assertTrue
import os
import sys

# to run python extension tests,
# add the following lines to global properties or user properties and press Ctrl+Shift+F1.
# *customcommandsregister.begin_tests=begin_tests|
# customcommand.begin_tests.name=Begin tests...
# customcommand.begin_tests.shortcut=Ctrl+Shift+F1
# customcommand.begin_tests.action.py=import scite_extend_tests; scite_extend_tests.First()
# customcommand.begin_tests.path=.
# *customcommandsregister.begin_tests_next=begin_tests_next|
# customcommand.begin_tests_next.name=Begin tests next
# customcommand.begin_tests_next.shortcut=Ctrl+Shift+F2
# customcommand.begin_tests_next.action.py=import scite_extend_tests; scite_extend_tests.Next()
# customcommand.begin_tests_next.path=.

# After pressing Ctrl+Shift+F1, instructions will be shown in the output pane to describe what to do.

# For python 2 compatibility
def printfn(s):
    print(s)

# run provided methods and IDM commands
testForAppFunctions = [
    ('Edit the CurrentBindingsGtk.html file', lambda: ScApp.OpenFile(os.path.join(ScApp.GetSciteDirectory(), 'doc', 'CurrentBindingsGtk.html'))),
    ('Make selection lowercase', lambda: ScApp.CmdLowerCase()),
    ('Duplicate current line', lambda: ScApp.CmdDuplicate()),
    ('Select all', lambda: ScApp.CmdSelectAll()),
]

# test all permutations of data types
testForEditorPaneFunctions = [
    # void|void|void|Home
    ('Go to start of line (return None)', lambda: printfn(ScEditor.Home())),
    # void|void|void|LineDuplicate
    ('Duplicate current selection (return None)', lambda: printfn(ScEditor.LineDuplicate())),
    # bool|void|void|CanUndo
    ('Can undo? (return bool)', lambda: printfn(ScEditor.CanUndo())),
    # int|int|int|MarkerAdd
    ('add marker on the 4th line (return markerid)', lambda: printfn(ScEditor.MarkerAdd(3, 1))),
    # int|int|stringresult|GetLine
    ('get text on line 4 (return text, length)', lambda: printfn(ScEditor.GetLine(3))),
    # int|int|string|SearchNext
    ('find next occurence of "a", same case', lambda: printfn(ScEditor.SearchNext(ScConst.SCFIND_MATCHCASE, 'a'))),
    # int|int|string|SearchNext
    ('find next occurence of "a", any case', lambda: printfn(ScEditor.SearchNext(0, 'a'))),
    # int|int|void|LineLength
    ('how many chars on 4th line including newlines?', lambda: printfn(ScEditor.LineLength(3))),
    # int|length|stringresult|GetCurLine
    ('returns (text of current line, index of caret on line)', lambda: printfn(ScEditor.GetCurLine())),
    # int|position|bool|WordEndPosition
    ('length of current word?', lambda: printfn(ScEditor.WordEndPosition(ScEditor.GetCurrentPos(), True) - ScEditor.WordStartPosition(ScEditor.GetCurrentPos(), True))),
    # int|position|void|LineFromPosition
    ('which line am I currently on?', lambda: printfn(ScEditor.LineFromPosition(1 + ScEditor.GetCurrentPos()))),
    # position|int|void|PositionFromLine
    ('which pos begins the 2nd line?', lambda: printfn(ScEditor.PositionFromLine(1))),
    # int|void|stringresult|GetSelText
    ('return selected text', lambda: printfn(ScEditor.GetSelText())),
    # position|int|int|CharPositionFromPoint
    ('what is char position at x,y 1,1?', lambda: printfn(ScEditor.CharPositionFromPoint(1, 1))),
    # position|position|void|BraceMatch
    ('position of matching brace or -1', lambda: printfn(ScEditor.BraceMatch(ScEditor.GetCurrentPos()))),
    # void|bool|colour|SetSelBack
    ('make selection orange', lambda: printfn(ScEditor.SetSelBack(True, ScConst.MakeColor(192, 96, 0)))),
    # void|int|int|HideLines
    ('Make the 3rd and 4th lines disappear', lambda: printfn(ScEditor.HideLines(2, 3))),
    # void|int|string|UserListShow
    ('Display a list of strings a|b|c', lambda: printfn(ScEditor.UserListShow(1, 'a b c'))),
    # void|int|void|GotoLine
    ('go to 1st line', lambda: printfn(ScEditor.GotoLine(0))),
    # void|length|string|AddText
    ('add text "Test" to doc', lambda: printfn(ScEditor.AddText('Test'))),
    # void|position|position|SetSel
    ('select the 3-6th char', lambda: printfn(ScEditor.SetSel(3, 6))),
    # void|void|string|SetText
    ('set entire doc to string "hi"', lambda: printfn(ScEditor.SetText('hi'))),
    # void|void|void|ClearAll
    ('clear entire doc', lambda: printfn(ScEditor.ClearAll()))]

# test all permutations of data types
testForEditorPaneProperties = [
    # bool|int|void|GetFoldExpanded
    ("is the fold on 4th line expanded?", lambda: printfn(ScEditor.GetFoldExpanded(3))),
    # void|int|bool|SetFoldExpanded
    ("expand the 4th line (not its children)", lambda: printfn(ScEditor.SetFoldExpanded(3, True))),
    # bool|void|void|GetSelectionEmpty
    ("is selection empty?", lambda: printfn(ScEditor.GetSelectionEmpty())),
    # void|int|void|SetCaretWidth
    ("make the caret wide", lambda: printfn(ScEditor.SetCaretWidth(9))),
    # void|colour|void|SetCaretFore
    ("make caret orange", lambda: printfn(ScEditor.SetCaretFore(ScConst.MakeColor(192, 96, 0)))),
    # colour|void|void|GetCaretFore
    ("get foreground color of caret (rgb).", lambda: printfn(ScConst.GetColor(ScEditor.GetCaretFore()))),
    # int|int|void|GetLineIndentation
    ("get indentation of the 4th line", lambda: printfn(ScEditor.GetLineIndentation(3))),
    # int|position|void|GetCharAt
    ("get 3rd char", lambda: printfn(chr(ScEditor.GetCharAt(2)))),
    # int|void|void|GetLineCount
    ("count lines in doc", lambda: printfn(ScEditor.GetLineCount())),
    # position|int|void|GetLineEndPosition
    ("get distance until end of line", lambda: printfn(ScEditor.GetLineEndPosition(ScEditor.LineFromPosition(ScEditor.GetCurrentPos())) - ScEditor.GetCurrentPos())),
    # position|void|void|GetCurrentPos
    ("current pos?", lambda: printfn(ScEditor.GetCurrentPos())),
    # stringresult|int|void|GetStyleFont
    ("style font for style # 1", lambda: printfn(ScEditor.GetStyleFont(1))),
    # stringresult|string|void|GetProperty
    ("what is the value of property 'fold.html'?", lambda: printfn(ScEditor.GetProperty('fold.html'))),
    # stringresult|void|void|GetLexerLanguage
    ("GetLexerLanguage", lambda: printfn(ScEditor.GetLexerLanguage())),
    # void|void|string|SetLexerLanguage
    ("replace selection with 'Test'", lambda: printfn(ScEditor.ReplaceSel('Test'))),
    # void|bool|void|SetViewEOL
    ("toggle view eol chars", lambda: printfn(ScEditor.SetViewEOL(not ScEditor.GetViewEOL()))),
    # void|int|colour|SetMarkerBack
    ("make marker type 1 mint green (ctrl F2 to see it)", lambda: printfn(ScEditor.SetMarkerBack(1, ScConst.MakeColor(0, 250, 200)))),
    # void|int|int|SetLineIndentation
    ("set indentation of 4th line to 0", lambda: printfn(ScEditor.SetLineIndentation(3, 0))),
    # void|position|void|SetCurrentPos
    ("set position/beginning of selection to beginning", lambda: printfn(ScEditor.SetCurrentPos(0)))]

allFunctions = []
allFunctions.extend(testForAppFunctions)
allFunctions.extend(testForEditorPaneFunctions)
allFunctions.extend(testForEditorPaneProperties)

currentFnSet = None
currentFnIndex = 0

def nonInteractiveTests():
    assertEq(2, ScConst.SCFIND_WHOLEWORD)
    assertEq(1, ScConst.SCMOD_SHIFT)
    assertEq(2140, ScConst.SCI_GETREADONLY)
    assertEq(6, ScConst.INDIC_BOX)
    assertEq(106, ScConst.IDM_SAVE)
    assertEq(1, ScConst.CARETSTYLE_LINE)
    assertEq(0x00010051, ScConst.MakeKeymod(ord('Q'), True, False, False))
    assertEq(0x00020051, ScConst.MakeKeymod(ord('Q'), False, True, False))
    assertEq(0x00040051, ScConst.MakeKeymod(ord('Q'), False, False, True))
    assertEq(0x000201ff, ScConst.MakeColor(255, 1, 2))
    assertEq(0x00ff0201, ScConst.MakeColor(1, 2, 255))
    assertEq((255, 1, 2), ScConst.GetColor(0x000201ff))
    assertEq((1, 2, 255), ScConst.GetColor(0x00ff0201))
    
    assertException(lambda: ScConst.NOT_A_CONSTANT, RuntimeError, 'Could not find constant')
    assertException(lambda: ScApp.CmdNotACommand(), RuntimeError)
    assertException(lambda: ScEditor.NotAFunction(), RuntimeError)
    assertException(lambda: ScEditor.GetNotAFunction(), RuntimeError)
    assertException(lambda: ScEditor.SetNotAFunction(), RuntimeError)
    
    # missing arguments
    assertException(lambda: printfn(ScEditor.SetCurrentPos()), RuntimeError)
    assertException(lambda: printfn(ScEditor.GetCharAt()), RuntimeError)
    
    # we should enforce read-only/write-only
    assertException(lambda: ScEditor.SetCharAt(12, ord('A')), RuntimeError, 'read-only')
    assertException(lambda: printfn(ScEditor.GetMarkerBack(1)), RuntimeError, 'write-only')
    
    # this will trigger the case where stringResultLen is 0. we should handle that case.
    assertEq('', ScEditor.GetProperty('nonexistent'))
    
    # are modules loaded from the .zip
    import os, traceback, re
    for module in [os, traceback, re]:
        assertTrue('python27.zip' in module.__file__)

def First():
    global currentFnSet, currentFnIndex
    if currentFnSet is None:
        nonInteractiveTests()
        
        if sys.platform.startswith('win'):
            allFunctions.append(('Open a message box', lambda: ScApp.MsgBox('opened message box')))
        
        currentFnSet = allFunctions
        currentFnIndex = -1
        Next()
        
    elif currentFnIndex < len(currentFnSet):
        print('Doing this: ' + currentFnSet[currentFnIndex][0])
        currentFnSet[currentFnIndex][1]()
    else:
        print('Nothing to do anymore.')
        
def Next():
    global currentFnSet, currentFnIndex
    if currentFnSet is None:
        print('Not initialized, please press ' + ScApp.GetProperty('customcommand.begin_tests.shortcut') +
            ' to begin')
        return
    currentFnIndex += 1
    if currentFnIndex >= len(currentFnSet):
        print('Done')
        return
        
    print('\n\nFrom now on, pressing ' + ScApp.GetProperty('customcommand.begin_tests.shortcut') +
         ' will start the action:\n"' + currentFnSet[currentFnIndex][0] + '"')
    print('To go next, press ' + ScApp.GetProperty('customcommand.begin_tests_next.shortcut'))
