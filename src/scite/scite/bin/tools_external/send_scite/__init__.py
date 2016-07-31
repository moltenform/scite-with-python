
import ctypes
import sys
from ctypes import wintypes

# Note: this code isn't currently for the full Director interface (SciTEDirector.html),
# it's for one-off messages sent to a SciTE main window.
# So, to retrieve the hwnd, either use findFirstSciteInstance below,
# or use the property $(SciTEWindowID). Not $(WindowID), which is for a director.

WM_COPYDATA = 0x4a

context64bit = sys.maxsize > 2**32
if context64bit:
    class COPYDATASTRUCT(ctypes.Structure):
        _fields_ = [
            ('dwData', ctypes.c_ulonglong),
            ('cbData', ctypes.wintypes.DWORD),
            ('lpData', ctypes.c_void_p),
        ]
else:
    class COPYDATASTRUCT(ctypes.Structure):
        _fields_ = [
            ('dwData', ctypes.wintypes.DWORD),
            ('cbData', ctypes.wintypes.DWORD),
            ('lpData', ctypes.c_void_p),
        ]

def findFirstSciteInstance(windowClass='SciTEWindow'):
    receiver = None # null pointer
    hwnd = ctypes.windll.user32.FindWindowA(windowClass, receiver)
    return hwnd or None

def sendCopyDataMessage(hwnd, message, dwData=0):
    assert isinstance(message, str)
    sender_hwnd = 0
    buf = ctypes.create_string_buffer(message)

    copydata = COPYDATASTRUCT()
    copydata.dwData = dwData
    copydata.cbData = buf._length_
    copydata.lpData = ctypes.cast(buf, ctypes.c_void_p)
    return ctypes.windll.user32.SendMessageA(
        hwnd, WM_COPYDATA, sender_hwnd, ctypes.byref(copydata))

def escapeMessage(message):
    # doesn't hit void SciTEWin::Run(const GUI::gui_char *cmdLine)
    # doesn't hit void UniqueInstance::WindowCopyData(const char *s, size_t len)
    # doesn't hit void DirectorExtension static LRESULT HandleCopyData(LPARAM lParam)
    # LRESULT UniqueInstance::CopyData(COPYDATASTRUCT *pcds)
    # GUI::gui_string SciTEWin::ProcessArgs(const GUI::gui_char *cmdLine)
    # bool SciTEBase::ProcessCommandLine(GUI::gui_string &args, int phase)
    
    if '"' in message:
        print('We currently do not support sending " character.')
        return None
    
    if '\r' in message or '\n' in message:
        print('We currently do not support sending newline characters.')
        return None
    
    # need to escape backslashes
    message = message.replace('\\', '\\\\')
    
    # at least in this build of SciTE,
    # message expects preceding dash.
    return '"' + '-' + message + '"'
        
def sendSciteMessage(hwnd, message):
    needToEscape = True
    if needToEscape:
        message = escapeMessage(message)
        if not message:
            return None

    return sendCopyDataMessage(hwnd, message, dwData=0)
