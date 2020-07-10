# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import os
from scite_extend_ui import ScEditor, ScApp

# ctrl-shift-t to re-open a closed tab
# useful because it's not limited to 20 entries
gClosedTabs = []
gSavedSep = ord(' ')
gSavedMaxHeight = 1
def OnClose(file):
    if file not in gClosedTabs and os.path.isfile(file):
        gClosedTabs.insert(0, file)

def OnOpen(file):
    # remove it from the list if it's opened in any form
    global gClosedTabs
    gClosedTabs = [item for item in gClosedTabs if item != file]

def reopenClosedTab():
    global gSavedSep, gSavedMaxHeight
    if len(gClosedTabs) > 0:
        gSavedSep = ScEditor.GetAutoCSeparator()
        gSavedMaxHeight = ScEditor.GetAutoCMaxHeight()
        itemList = '\n'.join(gClosedTabs)
        ScEditor.SetAutoCSeparator(ord('\n'))
        ScEditor.SetAutoCMaxHeight(20)
        ScEditor.UserListShow(ScEditor.UserListIDs.reopenClosedTabs, itemList)
            
def OnUserListSelection(chosen, id):
    global gClosedTabs
    if id == ScEditor.UserListIDs.reopenClosedTabs:
        ScEditor.SetAutoCSeparator(gSavedSep)
        ScEditor.SetAutoCMaxHeight(gSavedMaxHeight)
        if os.path.isfile(chosen):
            # remove it from the list -- for example if filename is invalid, ensures it is no longer in the list
            gClosedTabs = [item for item in gClosedTabs if item != chosen]
            ScApp.OpenFile(chosen)
        else:
            print("No longer exists: " + chosen)

