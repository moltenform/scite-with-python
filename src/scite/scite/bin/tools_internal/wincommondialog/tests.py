# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from __init__ import *

def testDisallowCastToBool(obj):
    didThrow = False
    try:
        # we want to stop this pattern
        if obj:
            print('Yes')
    except RuntimeError:
        didThrow = True
    assertTrue(didThrow, 'we expected this to throw because we\'ve disallowed cast to bool.')

def tests():
    import os
    import sys
    
    def announce(s):
        showMsg(s)
    
    inp = raw_input if sys.version[0] <= 2 else input
    if inp('Run interactive tests? y/n') != 'y':
        return
        
    announce('Showing an "info" dialog with title=title and text=text:')
    showMsg(text='text', title='title')
    announce('Showing an "warning" dialog with title=title and text=text:')
    showWarning(text='text', title='title')
    announce('Showing an "error" dialog with title=title and text=text:')
    showError(text='text', title='title')
    
    chosen = askYesNo('Please click Yes', 'title')
    assertTrue(chosen)
    chosen = askYesNo('Please click No', 'title')
    assertTrue(not chosen)
    chosen = askOKCancel('Please click OK', 'title')
    assertTrue(chosen)
    chosen = askOKCancel('Please click Cancel', 'title')
    assertTrue(not chosen)
    
    chosen = askYesNoCancel('Please click Yes', 'title')
    assertEq('yes', chosen.value())
    testDisallowCastToBool(chosen)
    chosen = askYesNoCancel('Please click No', 'title')
    assertEq('no', chosen.value())
    testDisallowCastToBool(chosen)
    chosen = askYesNoCancel('Please click Cancel', 'title')
    assertEq('cancel', chosen.value())
    testDisallowCastToBool(chosen)
    
    # don't test starting directory because it changes based on user's previous file selections, see
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms646839(v=vs.85).aspx
    announce('The next dialog should accept any one file, please click cancel.')
    assertEq(None, askOpenFile())

    announce('The next dialog should accept any .py file, please click cancel.')
    assertEq(None, askOpenFile(types='py'))
    
    announce('The next dialog should accept many files of any type, please click cancel.')
    assertEq(None, askOpenFile(mult=True))
    
    announce('The next dialog should accept many files of type .py, please click cancel.')
    assertEq(None, askOpenFile(types='py', mult=True))
    
    announce('The next dialog should accept any one file, please select a file')
    chosen = askOpenFile()
    print('File chosen was %s' % chosen)
    assertTrue(os.path.isabs(chosen) and files.isfile(chosen))
    
    announce('The next dialog should accept many files of any type, please choose just one file.')
    chosen = askOpenFile(mult=True)
    print('File chosen was %s' % chosen[0])
    assertTrue(len(chosen) == 1 and os.path.isabs(chosen[0]) and files.isfile(chosen[0]))

    announce('The next dialog should accept many files of any type, please choose several files.')
    chosen = askOpenFile(mult=True)
    print('Files chosen were \r\n%s' % '\r\n'.join(chosen))
    assertTrue(len(chosen) > 1 and all(os.path.isabs(f) and files.isfile(f) for f in chosen))
    
    announce('The next dialog should save to any type, please click cancel.')
    assertEq(None, askSaveFile())
    
    announce('The next dialog should save to jpg files, please click cancel.')
    assertEq(None, askSaveFile(types='jpg'))
    
    announce('The next dialog should save to jpg files, please type in "Test" and press enter (not Test.jpg).')
    chosen = askSaveFile(types='jpg', autoFixExtension=False)
    assertTrue(os.path.isabs(chosen) and not files.isfile(chosen) and chosen.endswith('Test'))
    
    announce('The next dialog should save to jpg files, please type in "Test" again and press enter (not Test.jpg).')
    chosen = askSaveFile(types='jpg')
    assertTrue(os.path.isabs(chosen) and not files.isfile(chosen) and chosen.endswith('Test.jpg'))
    
    announce('The next dialog should save to jpg files, please type in "Test.jpg" and press enter.')
    chosen = askSaveFile(types='jpg', autoFixExtension=False)
    assertTrue(os.path.isabs(chosen) and not files.isfile(chosen) and chosen.endswith('Test.jpg'))
    
    result = askInput('Please click Cancel', title='title', default='default text')
    assertTrue(result is None and not isinstance(result, str))
    
    result = askInput('Please type in no text and click OK', title='title', default='')
    assertTrue(result == '' and isinstance(result, str))
    
    result = askInput('Please type in "abc def" and click OK', title='title', default='abc def')
    assertTrue(result == 'abc def')
    
    result = askInput('Please type in "abc|def" and click OK', title='title', default='abc|def')
    assertTrue(result == 'abc|def')
    
    result = askInput('Please type in "|||" and click OK', title='title', default='|||')
    assertTrue(result == '|||')
    
    result = askInput('Please type in "text_cancel" and click OK', title='title', default='text_cancel')
    assertTrue(result == 'text_cancel')
    
    announce('In the next dialog, please pick pure red')
    chosen = askColor()
    assertEq((255, 0, 0), chosen)
    announce('In the next dialog, please pick pure green')
    chosen = askColor()
    assertEq((0, 255, 0), chosen)
    announce('In the next dialog, please pick pure blue')
    chosen = askColor()
    assertEq((0, 0, 255), chosen)

    print('Tests complete.')

if __name__ == '__main__':
    tests()
