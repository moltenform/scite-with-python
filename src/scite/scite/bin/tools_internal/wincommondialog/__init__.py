# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from ben_python_common import *

def showMsg(text, title=''):
    '''show a simple message box'''
    callProc(['simple', 'info', title, text])

def showError(text, title=''):
    '''show a simple message box with error icon'''
    callProc(['simple', 'error', title, text])

def showWarning(text, title=''):
    '''show a simple message box with warning icon'''
    callProc(['simple', 'warning', title, text])
    
def askYesNo(text, title=''):
    '''ask user to choose Yes or No'''
    retcode, stdout = callProc(['simple', 'yesno', title, text])
    return True if retcode == 8 else False

def askOKCancel(text, title=''):
    '''ask user to choose OK or Cancel'''
    retcode, stdout = callProc(['simple', 'okcancel', title, text])
    return True if retcode == 8 else False

def askYesNoCancel(text, title=''):
    '''ask user to choose Yes, No, or Cancel.
    call .value() on the object that is returned to see the result'''
    retcode, stdout = callProc(['simple', 'yesnocancel', title, text])
    if retcode == 8:
        return DisallowCastToBool('yes')
    elif retcode == 4:
        return DisallowCastToBool('no')
    else:
        return DisallowCastToBool('cancel')

def askColor():
    '''shows system color picker, returns results as tuple of red, green, blue'''
    retcode, stdout = callProc(['color'])
    try:
        parts = stdout.split('|')
        if (parts[1] == 'color_cancel'):
            return None
        else:
            return (int(parts[2]), int(parts[3]), int(parts[4]))
    except:
        print('retcode=%d; stdout=%s' % (retcode, stdout))
        raise

def askFileBase(action, types=None, startdir=None, mult=False):
    '''open file dialog.
    note: in Python 3 this will support unicode, but in Python 2 it will not,
    see files.runWithoutWaitUnicode for my workaround for a similar case.'''
    if types and ('*' in types or '.' in types):
        raise ValueError('types should be just the extension, e.g. "png" not "*.png"')
    args = ['file', action, types or '*']
    if startdir:
        args.append(startdir)
    retcode, stdout = callProc(args)
    try:
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
    except:
        print('retcode=%d; stdout=%s' % (retcode, stdout))
        raise
        
def askOpenFile(types=None, startdir=None, mult=False):
    '''shows system file picker.'''
    action = 'openmult' if mult else 'open'
    results = askFileBase(action, types=types, startdir=startdir, mult=mult)
    
    # confirm files exist.
    if results:
        assertTrue(all(files.isfile(filename) for filename in (results if mult else [results])),
            'Unicode not supported due to limitation in the Python 2 subprocess module.')
    return results

def askSaveFile(types=None, startdir=None, autoFixExtension=True):
    '''shows file picker, by default will automatically append specified file extension.'''
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
    '''play a sound. provide path to wav file or one of 'Asterisk' 'Default' 'Exclamation' 'Question' '''
    retcode, stdout = callProc(['sound', path])
    return retcode == 0

def askInput(prompt='Please provide input:', title='', default=''):
    '''ask user to provide text'''
    retcode, stdout = callProc(['text', title, prompt, default])
    try:
        parts = stdout.split('|')
        if parts[1] == 'text_cancel':
            return None
        else:
            # it's possible that the user typed in some | characters
            result = parts[2:]
            result.pop() # remove the trailng | character
            return '|' .join(result)
    except:
        print('retcode=%d; stdout=%s' % (retcode, stdout))
        raise
        
def callProc(args):
    import os
    mypath = os.path.realpath(__file__)
    exepath = files.join(files.getparent(mypath), 'wincommondialog.exe')
    if not files.isfile(exepath):
        raise RuntimeError('cannot find commondialog, expected to see it at ' + exepath)
    
    args.insert(0, exepath)
    retcode, stdout, stderr = files.run(args, throwOnFailure=False, stripText=False, captureOutput=True)
    return retcode, stdout

class DisallowCastToBool(object):
    ''' for results that are more than just true or false,
    prevent the caller from writing the code if result: ... else ...
    the caller should instead say if result.value() == 'yes': ...'''
    def __init__(self, value):
        self.val = value
    
    def __nonzero__(self):
        raise RuntimeError('you must use .value() to check the value.')
    
    def __bool__(self):
        raise RuntimeError('you must use .value() to check the value.')
    
    def value(self):
        return self.val
