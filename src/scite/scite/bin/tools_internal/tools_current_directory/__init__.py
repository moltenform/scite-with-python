# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from scite_extend_ui import *

def CopyCurrentDirectory():
    dir = ScApp.GetFileDirectory()
    ScEditor.Utils.SetClipboardText(dir)
