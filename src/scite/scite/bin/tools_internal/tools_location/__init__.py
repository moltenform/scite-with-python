# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from scite_extend_ui import ScApp, ScEditor, ScConst
import os

# ctrl-shift-j to move to start/end of block
from goblocklocation import *

# ctrl-shift-o to open selected text
from openselectedtext import *

# ctrl-shift-t to re-open closed file
from reopenclosedfile import *

# location tracking is a custom feature for scite-with-python, but it's implemented in c++
def LocationNext():
    ScApp.LocationNext()

def LocationPrev():
    ScApp.LocationPrev()

#~ # why OnKey?
#~ # otherwise open-in-selection won't work in the output pane
#~ def OnKey(key, shift, ctrl, alt):
    #~ if (key==ord('o') or key==ord('O')) and shift and ctrl:
        #~ ScApp.GetActivePane()
