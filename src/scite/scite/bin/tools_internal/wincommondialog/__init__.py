
from ben_python_common import *


def showMsg(text, title=''):
    callProc(['simple', 'info', title, text])

def showError(text, title=''):
    callProc(['simple', 'error', title, text])

def showWarning(text, title=''):
    callProc(['simple', 'warning', title, text])
    
def askYesNo(text, title=''):
    retcode, stdout = callProc(['simple', 'yesno', title, text])
    return True if retcode == 8 else False

def askOKCancel(text, title=''):
    retcode, stdout = callProc(['simple', 'okcancel', title, text])
    return True if retcode == 8 else False

def askYesNoCancel(text, title=''):
    # be helpful and throw an error if the caller mistakenly has the pattern "if result:"
    # instead of "if result == 'cancel'"
    class WrapResult(object):
        def __init__(self, value):
            self.val = value
        def __nonzero__(self):
            raise RuntimeError('you must use .value() to check the value.')
        def __bool__(self):
            raise RuntimeError('you must use .value() to check the value.')
        def value(self):
            return self.val
            
    retcode, stdout = callProc(['simple', 'yesnocancel', title, text])
    if retcode == 8:
        return WrapResult('yes')
    elif retcode == 4:
        return WrapResult('no')
    else:
        return WrapResult('cancel')

def askColor():
    retcode, stdout = callProc(['color'])
    parts = stdout.split('|')
    if (parts[1] == 'color_cancel'):
        return None
    else:
        return (int(parts[2]), int(parts[3]), int(parts[4]))

def askFileBase(action, types=None, startdir=None, mult=False):
    # note: in Python 3 this will support unicode, but in Python 2 it will not, 
    # see files.runWithoutWaitUnicode for my workaround for a similar case.
    if types and ('*' in types or '.' in types):
        raise ValueError('types should be just the extension, e.g. "png" not "*.png"')
    args = ['file', action, types or '*' ]
    if startdir:
        args.append(startdir)
    retcode, stdout = callProc(args)
    parts = stdout.split('|')
    if (parts[1] == 'file_cancel'):
        return None
    elif mult:
        if len(parts) == 4:
            return [parts[2]]
        else:
            dir = parts[2]
            filenames = parts[3:]
            filenames.pop() # remove the trailng | character
            return [files.join(dir, filename) for filename in filenames]
    else:
        assertTrue(len(parts) == 4, 'expected length of 4')
        return parts[2]
        
def askOpenFile(types=None, startdir=None, mult=False):
    action = 'openmult' if mult else 'open'
    return askFileBase(action, types=types, startdir=startdir, mult=mult)
        
def askSaveFile(types=None, startdir=None, autoFixExtension=True):
    result = askFileBase(action='save', types=types, startdir=startdir)
    
    # add the extension if the user didn't add it...
    # we can do this because we only support one extension, otherwise we'd have to 
    # do this in C++ and look at ofn.nFilterIndex.
    if result and types and autoFixExtension and not result.lower().endswith('.' + types.lower()):
        proposedName = result + '.' + types
        if not files.exists(proposedName):
            return proposedName
    
    return result

def playSound(path='Asterisk'):
    # special sounds are 'Asterisk' 'Default' 'Exclamation' 'Question'
    retcode, stdout = callProc(['sound', path])
    return retcode == 0

def askInput(prompt='Please provide input:', title='', default=''):
    retcode, stdout = callProc(['text', title, prompt, default])
    maxSplits = 2
    parts = stdout.split('|')
    if parts[1] == 'text_cancel':
        return None
    else:
        # it's possible that the user typed in some | characters
        result = parts[2:]
        result.pop() # remove the trailng | character
        return '|' .join(result)
        
def callProc(args):
    import os
    mypath = os.path.realpath(__file__)
    exepath = files.join(files.getparent(mypath), 'wincommondialog.exe')
    if not files.isfile(exepath):
        raise RuntimeError('cannot find commondialog, expected to see it at ' + exepath)
    
    args.insert(0, exepath)
    retcode, stdout, stderr = files.run(args, throwOnFailure=False, stripText=False, captureoutput=True)
    return retcode, stdout

def testDisallowCastToBool(obj):
    didThrow = False
    try:
        # we want to stop this pattern
        if obj:
            print('Yes')
    except RuntimeError:
        didThrow = True
    assertTrue(didThrow, 'we expected this to throw because we\'ve disallowed cast to bool.')


    