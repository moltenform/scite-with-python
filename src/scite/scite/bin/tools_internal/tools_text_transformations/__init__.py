
from scite_extend_ui import *

def StartTool():
    label = 'Modify selected text:'
    choices = ['upper|Upper case', 'lower|Lower case', 'title|Title case']
    ScAskUserChoice(choices=choices, label=label, callback=OnCallback)

def OnCallback(action):
    if action == 'upper':
        return modifyText(lambda s: s.upper())
    elif action == 'lower':
        return modifyText(lambda s: s.lower())
    elif action == 'title':
        return modifyText(titleCase)
    elif not action:
        pass
    else:
        print 'Unknown action ', action

def titleCase(s):
    result = ''
    for i, c in enumerate(s):
        if i == 0 or not s[i - 1].isalpha():
            result += c.upper()
        else:
            result += c.lower()
            
    return result

def modifyText(fn):
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

if __name__ == '__main__':
    def assertEq(expected, received):
        if expected != received:
            import pprint
            msg = '\nassertion failed, expected:\n'
            msg += pprint.pformat(expected)
            msg += '\nbut got:\n'
            msg += pprint.pformat(received)
            raise AssertionError(msg)
        
    assertEq('', titleCase(''))
    assertEq('A', titleCase('a'))
    assertEq('Aa', titleCase('aa'))
    assertEq('Aa Aa', titleCase('aa aa'))
    assertEq('Aa Aa', titleCase('AA AA'))
    assertEq('A B C D', titleCase('a b c d'))
    assertEq('A.B|C/D"E\'F\\G-H_I:J', titleCase('a.b|c/d"e\'f\\g-h_i:j'))
    assertEq('0A1Bb2Ccc3', titleCase('0a1bb2ccc3'))
    assertEq('0A1Bb2Ccc3', titleCase('0A1Bb2Ccc3'))
    assertEq('0A1Bb2Ccc3', titleCase('0A1BB2CCC3'))
    
    
    
    
    