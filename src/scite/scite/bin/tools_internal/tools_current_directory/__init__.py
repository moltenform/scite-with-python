
from scite_extend_ui import *

def CopyCurrentDirectory():
    from ben_python_common import setClipboardText
    dir = ScApp.GetFileDirectory()
    setClipboardText(dir)
