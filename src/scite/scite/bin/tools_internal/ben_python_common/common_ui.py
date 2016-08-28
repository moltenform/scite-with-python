# BenPythonCommon,
# 2015 Ben Fisher, released under the GPLv3 license.

from .common_util import *
from . import files

def getInputBool(sPrompt):
    sPrompt += ' '
    while True:
        s = getRawInput(sPrompt).strip()
        if s == 'y':
            return True
        if s == 'n':
            return False
        if s == 'Y':
            return 1
        if s == 'N':
            return 0
        if s == 'BRK':
            raise KeyboardInterrupt()
            
def getInputYesNoCancel(sPrompt):
    sPrompt += ' y/n/cancel '
    while True:
        s = getRawInput(sPrompt).strip()
        if s == 'y':
            return 'Yes'
        if s == 'n':
            return 'No'
        if s == 'cancel':
            return 'Cancel'
        if s == 'BRK':
            raise KeyboardInterrupt()

def getInputInt(sPrompt, min=0, max=0xffffffff):
    sPrompt += ' between %d and %d ' % (min, max)
    while True:
        s = getRawInput(sPrompt).strip()
        if s.isdigit() and min <= int(s) <= max:
            return int(s)
        if s == 'BRK':
            raise KeyboardInterrupt()

def getInputString(sPrompt, bConfirm=True):
    sPrompt += ' '
    while True:
        s = getRawInput(sPrompt).strip()
        if s == 'BRK':
            raise KeyboardInterrupt()
        if s:
            if not bConfirm or getInputBool('you intended to write: ' + s):
                return unicode(s)

# returns -1, 'Cancel' on cancel
def getInputFromChoices(sPrompt, arrChoices, fnOtherCommands=None, otherCommandsContext=None):
    trace('0) cancel')
    for i, choice in enumerate(arrChoices):
        trace('%d) %s'%(i + 1, choice))
    while True:
        s = getRawInput(sPrompt).strip()
        if s == '0':
            return -1, 'Cancel'
        if s == 'BRK':
            raise KeyboardInterrupt()
        if s.isdigit():
            n = int(s) - 1
            if n >= 0 and n < len(arrChoices):
                return n, arrChoices[n]
            else:
                trace('out of range')
                continue
        if fnOtherCommands:
            breakLoop = fnOtherCommands(s, arrChoices, otherCommandsContext)
            if breakLoop:
                return (-1, breakLoop)

def getRawInput(prompt):
    import sys
    if sys.version_info[0] <= 2:
        return raw_input(getPrintable(prompt))
    else:
        return input(getPrintable(prompt))

def err(s=''):
    raise RuntimeError('fatal error\n' + getPrintable(s))
    
def alert(s):
    trace(s)
    getRawInput('press Enter to continue')
    
def warn(s):
    trace('warning\n' + getPrintable(s))
    if not getInputBool('continue?'):
        raise RuntimeError('user chose not to continue after warning')
    
def getInputBoolGui(sPrompt):
    "Ask yes or no. Returns True on yes and False on no."
    import tkMessageBox
    return tkMessageBox.askyesno(title=' ', message=sPrompt)
    
def getInputYesNoCancelGui(sPrompt):
    choice, choiceText = getInputFromChoicesGui(sPrompt, ['Yes', 'No', 'Cancel'])
    if choice == -1:
        return 'Cancel'
    elif choice == 0:
        return 'Yes'
    elif choice == 1:
        return 'No'
    else:
        return 'Cancel'
    
def getInputFloatGui(sPrompt, default=None, min=0.0, max=100.0, title=''):
    "validated to be an float (decimal number). Returns None on cancel."
    import tkSimpleDialog
    kwargs = dict(initialvalue=default) if default is not None else dict()
    return tkSimpleDialog.askfloat(' ', sPrompt, minvalue=min, maxvalue=max, **kwargs)
    
# returns '' on cancel
def getInputStringGui(prompt, initialvalue=None, title=' '):
    import Tkinter
    import tkSimpleDialog
    root = Tkinter.Tk()
    root.withdraw()
    options = dict(initialvalue=initialvalue) if initialvalue else dict()
    s = tkSimpleDialog.askstring(title, prompt, **options)
    return '' if s is None else s

def findUnusedLetter(dictUsed, newWord):
    for i, c in enumerate(newWord):
        if c.isalnum() and c.lower() not in dictUsed:
            dictUsed[c] = True
            return i
    return None

# returns -1, 'Cancel' on cancel
def getInputFromChoicesGui(sPrompt, arOptions):
    import Tkinter
    assert len(arOptions) > 0
    retval = [None]

    def setresult(v):
        retval[0] = v
    
    # http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
    class ChoiceDialog(object):
        def __init__(self, parent):
            top = self.top = Tkinter.Toplevel(parent)
            Tkinter.Label(top, text=sPrompt).pack()
            top.title('Choice')

            lettersUsed = dict()
            box = Tkinter.Frame(top)
            for i, text in enumerate(arOptions):
                opts = dict()
                opts['text'] = text
                opts['width'] = 10
                opts['command'] = lambda which=i: self.onbtn(which)
                
                whichToUnderline = _findUnusedLetter(lettersUsed, text)
                if whichToUnderline is not None:
                    opts['underline'] = whichToUnderline
                    
                    # if the label is has t underlined, t is keyboard shortcut
                    top.bind(text[whichToUnderline].lower(), lambda _, which=i: self.onbtn(which))
                    
                if i == 0:
                    opts['default'] = Tkinter.ACTIVE
                    
                w = Tkinter.Button(box, **opts)
                w.pack(side=Tkinter.LEFT, padx=5, pady=5)
            
            top.bind("<Return>", lambda unused: self.onbtn(0))
            top.bind("<Escape>", lambda unused: self.cancel())
            box.pack(pady=5)
            parent.update()

        def cancel(self):
            self.top.destroy()

        def onbtn(self, nWhich):
            setresult(nWhich)
            self.top.destroy()

    root = Tkinter.Tk()
    root.withdraw()
    d = ChoiceDialog(root)
    root.wait_window(d.top)
    result = retval[0]
    if result is None:
        return -1, 'Cancel'
    else:
        return result, arOptions[result]

def errGui(s=''):
    import tkMessageBox
    tkMessageBox.showerror(title='Error', message=getPrintable(s))
    raise RuntimeError('fatal error\n' + getPrintable(s))
    
def alertGui(s):
    import tkMessageBox
    tkMessageBox.showinfo(title=' ', message=getPrintable(s))
    
def warnGui(s):
    import tkMessageBox
    if not tkMessageBox.askyesno(title='Warning', message=getPrintable(s) + '\nContinue?', icon='warning'):
        raise RuntimeError('user chose not to continue after warning')
        

gDirectoryHistory = dict()
def _getFileDialogGui(fn, initialdir, types, title):
    if initialdir is None:
        initialdir = gDirectoryHistory.get(repr(types), '.')
    
    kwargs = dict()
    if types is not None:
        aTypes = [(type.split('|')[1], type.split('|')[0]) for type in types]
        defaultExtension = aTypes[0][1]
        kwargs['defaultextension'] = defaultExtension
        kwargs['filetypes'] = aTypes
    
    result = fn(initialdir=initialdir, title=title, **kwargs)
    if result:
        gDirectoryHistory[repr(types)] = files.split(result)[0]
        
    return result

def getOpenFileGui(initialdir=None, types=None, title='Open'):
    "Specify types in the format ['.png|Png image','.gif|Gif image'] and so on."
    import tkFileDialog
    return _getFileDialogGui(tkFileDialog.askopenfilename, initialdir, types, title)
    
def getSaveFileGui(initialdir=None, types=None, title='Save As'):
    "Specify types in the format ['.png|Png image','.gif|Gif image'] and so on."
    import tkFileDialog
    return _getFileDialogGui(tkFileDialog.asksaveasfilename, initialdir, types, title)

def _dbgHookCallback(exctype, value, traceback):
    DBG()
    msg('unhandled exception ' + value)
    sys.__excepthook__(exctype, value, traceback)

def registerDebughook(b=True):
    if b:
        sys.excepthook = _dbgHookCallback
    else:
        sys.excepthook = sys.__excepthook__
    
def softDeleteFile(s):
    import os
    trashdir = os.path.expanduser('~') + u'/local/less_important/trash'
    if not files.exists(trashdir):
        trashdir = u'C:\\data\\local\\less_important\\trash'
        if not files.exists(trashdir):
            raise Exception('please edit softDeleteFile() in common_ui.py ' +
                'and specify a directory for removed files.')
            
    # as a prefix, the first 2 chars of the parent directory
    prefix = files.getname(files.getparent(s))[0:2] + '_'
    newname = trashdir + files.sep + prefix + files.split(s)[1] + getRandomString()
    if files.exists(newname):
        raise Exception('already exists ' + newname +
            '. is this directory full of files, or was the random seed reused?')
    files.move(s, newname, False)
    return newname
