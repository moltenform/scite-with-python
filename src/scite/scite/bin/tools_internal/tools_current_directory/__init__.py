
from scite_extend_ui import *

def CopyCurrentDirectory():
    dir = ScApp.GetFileDirectory()
    ScEditor.Utils.SetClipboardText(dir)
