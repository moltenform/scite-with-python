# -*- coding: utf-8 -*-
# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

def InsertSectionBreakText():
    from scite_extend_ui import ScEditor
    block = u'▃'
    amount = 32
    whatToWrite = u''
    whatToWrite += u'# ' + block * int(amount / 2)
    whatToWrite += '  '
    whatToWrite += block * int(amount / 2)
    whatToWriteBytes = whatToWrite.encode('utf-8')
    
    ScEditor.BeginUndoAction()
    try:
        ScEditor.PaneWrite(whatToWriteBytes)
        for _ in range(1 + int(amount / 2)):
            ScEditor.CharLeft()
    finally:
        ScEditor.EndUndoAction()


