# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3
# See documentation at https://moltenform.com/page/scite-with-python/doc/writingplugin.html

import SciTEModule

debugTracing = False

class ScAppClass(object):
    '''
    Methods starting with "Cmd" are routed to SciTE,
    See https://moltenform.com/page/scite-with-python/doc/writingpluginapi.html for a list of supported methods.
    example:
        from scite_extend_ui import ScApp
        ScApp.Trace('test')
        ScApp.CmdQuit()
    '''
    def __init__(self):
        self.registeredCallbacks = dict()
        self.cachedCallbackModules = dict()
    
    def Trace(self, s):
        '''write to ScOutput, doesn't include newline'''
        return SciTEModule.app_Trace(s)
    
    def MsgBox(self, s):
        '''Show message box with text s'''
        return SciTEModule.app_MsgBox(s)
        
    def OpenFile(self, s):
        '''Open file'''
        return SciTEModule.app_OpenFile(s)
        
    def GetProperty(self, s):
        '''Returns value of property'''
        return SciTEModule.app_GetProperty(s)
        
    def SetProperty(self, s, v):
        '''Set value of property'''
        if debugTracing:
            print('SetProperty %s=%s'%(s, v))

        return SciTEModule.app_SetProperty(s, v)
    
    def UnsetProperty(self, s):
        '''Unset property'''
        return SciTEModule.app_UnsetProperty(s)
        
    def UpdateStatusBar(self, updateSlowData=False):
        '''Update status bar'''
        return SciTEModule.app_UpdateStatusBar(updateSlowData)
        
    def EnableNotification(self, eventName, enabled=True):
        '''Enables notifcation (doesn't need to be called by plugins)'''
        return SciTEModule.app_EnableNotification(eventName, 1 if enabled else 0)
    
    def LocationNext(self):
        '''Go to next location'''
        return SciTEModule.app_GetNextOrPreviousLocation(1)
        
    def LocationPrev(self):
        '''Go to previous location'''
        return SciTEModule.app_GetNextOrPreviousLocation(0)
    
    def GetFilePath(self, cannotBeUntitled=True):
        '''Returns full file path'''
        if cannotBeUntitled:
            # we usually don't want untitled documents to look like they have a path
            return self.GetProperty('FilePath') if len(self.GetFileName()) > 0 else ''
        else:
            return self.GetProperty('FilePath')
        
    def GetFileName(self):
        '''Returns file name'''
        return self.GetProperty('FileNameExt')
        
    def GetFileDirectory(self):
        '''Returns directory of file'''
        return self.GetProperty('FileDir')
        
    def GetSciteDirectory(self):
        '''Returns SciTE location'''
        return self.GetProperty('SciteDefaultHome')
        
    def GetSciteUserDirectory(self):
        '''Returns SciTE user dir location'''
        return self.GetProperty('SciteUserHome')
        
    def GetExternalPython(self):
        import os
        from ben_python_common import files
        python = self.GetProperty('customcommand.externalpython')
        python = files.findBinaryOnPath(python)
        if not os.path.isfile(python):
            print('''Could not find Python 2 installation, please open the file \n%s\n
    and set the property \ncustomcommand.externalpython\n to the directory where Python 2 is installed.''' %
            os.path.join(self.GetSciteDirectory(), 'properties', 'python.properties'))
            return None
        else:
            return python
    
    def RequestThatEventContinuesToPropagate(self):
        '''Call this to allow event propagation to continue, i.e. to let a keyboard shortcut
        be passed on to its default handlers. Can be used to add a hook a keyboard shortcut while
        still allowing the default behavior to occur.
        In most cases this isn't needed because the plugin can call a ScApp.Cmd method to send an IDM command.
        
        RequestThatEventContinuesToPropagate only works for tools in py_immediate mode, e.g.
        customcommand.name_of_tool.action.py_immediate=ThisModule().myAction()'''
        raise RequestThatEventContinuesToPropagate()
        
    def __getattr__(self, s):
        '''Run a command, see the full list in https://moltenform.com/page/scite-with-python/doc/writingpluginapi.html'''
        if s.startswith('Cmd'):
            # return a callable object; it looks like a method to the caller.
            commandName = s[len('Cmd'):]
            return (lambda: SciTEModule.app_SciteCommand(commandName))
        else:
            raise AttributeError()

class ScConstClass(object):
    '''
    a class for retrieving a SciTE constant.
    example:
        from scite_extend_ui import ScConst
        matchType = ScConst.SCFIND_MATCHCASE
        ScEditor.SearchNext(matchType, 'a')
        color = ScConst.MakeColor(0, 250, 200)
        ScEditor.SetMarkerBack(1, color)
    See https://moltenform.com/page/scite-with-python/doc/writingpluginapi.html for a list of constants.
    '''
    def __init__(self):
        self.eventTypeUnknown = 0
        self.eventTypeClicked = 1
        self.eventTypeChange = 2
        self.eventTypeFocusIn = 3
        self.eventTypeFocusOut = 4
        self.StopEventPropagation = 'StopEventPropagation'
        
    def __getattr__(self, s):
        if s.startswith('_'):
            raise AttributeError()
        else:
            return SciTEModule.app_GetConstant(s)
            
    def MakeKeymod(self, keycode, shift=False, ctrl=False, alt=False):
        keycode = keycode & 0xffff
        modifiers = 0
        
        if shift:
            modifiers |= SciTEModule.app_GetConstant('SCMOD_SHIFT')
        
        if ctrl:
            modifiers |= SciTEModule.app_GetConstant('SCMOD_CTRL')
        
        if alt:
            modifiers |= SciTEModule.app_GetConstant('SCMOD_ALT')
            
        return keycode | (modifiers << 16)
        
    def MakeColor(self, red, green, blue):
        assert 0 <= red <= 255
        assert 0 <= green <= 255
        assert 0 <= blue <= 255
        return red + (green << 8) + (blue << 16)
        
    def GetColor(self, val):
        red = val & 0x000000ff
        green = (val & 0x0000ff00) >> 8
        blue = (val & 0x000ff0000) >> 16
        return (red, green, blue)

class ScPaneClassUtils(object):
    '''
    Helpers for ScPaneClass
    example:
        from scite_extend_ui import ScEditor
        ScEditor.Utils.ExpandSelectionToIncludeEntireLines()
    '''
    def __init__(self, pane):
        self.pane = pane
    
    def GetEolCharacter(self):
        '''Return current EOL character, e.g. \r\n'''
        n = self.pane.GetEOLMode()
        if n == 0:
            return '\r\n'
        elif n == 1:
            return '\r'
        else:
            return '\n'
            
    def ExpandSelectionToIncludeEntireLines(self):
        '''Ensure entire lines are selected'''
        startline = self.pane.LineFromPosition(self.pane.GetSelectionStart())
        endline = self.pane.LineFromPosition(self.pane.GetSelectionEnd()) + 1
        startpos = self.pane.PositionFromLine(startline)
        endpos = self.pane.PositionFromLine(endline)
        
        # endpos might be at a newline character, though, so subtract from the selection until it is not.
        while self.pane.GetCharAt(endpos - 1) in (ord('\r'), ord('\n')):
            endpos -= 1
        self.pane.SetSelection(startpos, endpos)
    
    def SetClipboardText(self, s):
        self.pane.CopyText(s)
    
    def GetClipboardText(self):
        # SciTE apparently provides CopyText but no GetCopiedText
        # On Windows:
        #       Tkinter is a large dependency
        #       Pyperclip doesn't work from inside the SciTE context, on Gtk fails, on Win returns garbage
        #       We can run Pyperclip in an external context and read from stdout.
        # On Gtk:
        #       reading from printclipboard.py causes a deadlock,
        #       printclipboard.py is waiting for SciTE to send the clipboard data while
        #       SciTE is waiting for printclipboard.py to exit.
        #       Providing a C hook into gtk_widget_get_clipboard would cause the same problem.
        #       Also, using SciTE to paste does not work because paste is asynchronous, see ScintillaGTK::Paste
        import os, sys
        if sys.platform.startswith('win'):
            python = ScApp.GetExternalPython()
            if not python:
                return None
            
            script = os.path.join(ScApp.GetSciteDirectory(), 'tools_internal', 'ben_python_common', 'printclipboard.py')
            if not os.path.isfile(script):
                print('Could not find script at %s.' % script)
                return None
            
            # specify -O (look for .pyo files) and -B (won't try to write .pyc or .pyo files)
            args = [python, '-O', '-B', script]
            from ben_python_common import files
            retcode, stdout, stderr = files.run(args, shell=False, throwOnFailure=False, captureoutput=True, wait=True)
            if retcode != 0:
                return None
            else:
                return stdout
        else:
            raise RuntimeError('GetClipboardText not supported on this platform')

class ScPaneClass(object):
    '''
    represents a Scintilla window.
    ScEditor is an instance of this class representing the main code editor.
    ScOutput is an instance of this class representing the output pane.
    See https://moltenform.com/page/scite-with-python/doc/writingpluginapi.html for a list of supported methods.
    example:
        from scite_extend_ui import ScEditor
        print('language is ' + ScEditor.GetLexerLanguage())
        print('using tabs is ' + ScEditor.GetUseTabs())
        ScEditor.SetUseTabs(False)
        ScEditor.LineDuplicate()
    '''
    
    def __init__(self, paneNumber):
        self.paneNumber = paneNumber
        self.Utils = ScPaneClassUtils(self)
    
    # pane methods
    def PaneAppend(self, txt):
        '''Append text'''
        return SciTEModule.pane_Append(self.paneNumber, txt)

    def PaneInsertText(self, txt, pos):
        '''Insert text (without changing selection)'''
        return SciTEModule.pane_Insert(self.paneNumber, pos, txt)
        
    def PaneWrite(self, txt, pos=None):
        '''Insert text, and update selection'''
        if pos is None:
            pos = self.GetCurrentPos()
        SciTEModule.pane_Insert(self.paneNumber, pos, txt)
        self.GotoPos(pos + len(txt))
        
    def PaneRemoveText(self, npos1, npos2):
        '''Remove text between these positions'''
        return SciTEModule.pane_Remove(self.paneNumber, npos1, npos2)
        
    def PaneGetText(self, n1, n2):
        '''Get text between these positions'''
        return SciTEModule.pane_Textrange(self.paneNumber, n1, n2)
    
    def PaneFindText(self, s, pos1=0, pos2=-1, wholeWord=False, matchCase=False, regExp=False, flags=0):
        '''Find text'''
        if wholeWord:
            flags |= ScConst.SCFIND_WHOLEWORD
        if matchCase:
            flags |= ScConst.SCFIND_MATCHCASE
        if regExp:
            flags |= ScConst.SCFIND_REGEXP
            
        return SciTEModule.pane_FindText(self.paneNumber, s, flags, pos1, pos2)
    
    # helpers where the Scintilla version is less convenient to use
    def GetLineText(self, line):
        '''Returns text of specified line'''
        return self.GetLine(line)[0]
    
    def GetSelectedText(self):
        '''Returns selected text'''
        return self.GetSelText()[0]
        
    def GetCurrentLineText(self):
        '''Returns text of current line'''
        return self.GetCurLine()[0]

    # redirect most methods on this object to call into Scintilla.
    def __getattr__(self, sprop):
        '''See https://moltenform.com/page/scite-with-python/doc/writingpluginapi.html for a list of supported methods.'''
        if sprop.startswith('_'):
            raise AttributeError()
        else:
            return (lambda *args: SciTEModule.pane_SendScintilla(self.paneNumber, sprop, *args))

class RequestThatEventContinuesToPropagate(Exception):
    # see ScApp.RequestThatEventContinuesToPropagate
    pass

def OnEvent(eventName, args):
    # user strip events are handled differently
    if eventName == 'OnUserStrip':
        import scite_extend_ui
        return scite_extend_ui.ScToolUIManager.OnUserStrip(*args)
    
    # on key events might be part of a multi key shortcut
    if eventName == 'OnKey':
        import scite_extend_ui
        val = scite_extend_ui.ScMultiKeyManager.OnKey(args)
        if val == ScConst.StopEventPropagation:
            return val
    
    # call into each plugin that registered for this event
    callbacks = ScApp.registeredCallbacks.get(eventName, None)
    if callbacks:
        for command, path in callbacks:
            try:
                module = findCallbackModuleFromPath(command, path)
                val = callCallbackModule(module, command, eventName, args)
                if val == ScConst.StopEventPropagation:
                    # the user has asked that we not process any other callbacks
                    return val
            except:
                # print the Exception, but let other event handlers run
                import traceback
                print('Exception thrown when calling event %s for %s; %s' % (eventName, command, traceback.format_exc()))

def findCallbackModuleFromPath(command, path):
    # it's more intuitive for each module's state to persist.
    cached = ScApp.cachedCallbackModules.get(path, None)
    if cached:
        return cached
    
    import sys, os, importlib
    expectedPythonModdir = os.path.join(ScApp.GetSciteDirectory(), path)
    expectedPythonInit = os.path.join(expectedPythonModdir, '__init__.py')
    if not os.path.isfile(expectedPythonInit):
        raise RuntimeError('command %s could not find a file at %s' % (command, expectedPythonInit))
    
    # I could use imp.load_source to load the __init__.py directly, but then it can't access its submodules
    pathsaved = sys.path
    newPath = list(sys.path)
    newPath.append(os.path.split(expectedPythonModdir)[0])
    try:
        sys.path = newPath
        module = importlib.import_module(os.path.split(expectedPythonModdir)[1])
    finally:
        sys.path = pathsaved
    
    ScApp.cachedCallbackModules[path] = module
    return module

def findCallbackModule(command):
    path = ScApp.GetProperty('customcommand.' + command + '.path')
    assert path, 'in command %s, path must be defined to use ThisModule.' % command
    return findCallbackModuleFromPath(command, path)

def callCallbackModule(module, command, eventName, args):
    function = getattr(module, eventName, None)
    if not function:
        raise RuntimeError('command %s registered for event %s but we could not find function of this name' % (command, eventName))
    else:
        return function(*args) if args else function()

def registerCallbacks(command, path, callbacks):
    assert path, 'in command %s, defining a callback requires specifying a path' % command
    
    callbacks = (callbacks or '').split('|')
    for eventName in callbacks:
        eventName = eventName.strip()
        if eventName:
            assert eventName.startswith('On')
            ScApp.EnableNotification(eventName)
            
            if eventName not in ScApp.registeredCallbacks:
                ScApp.registeredCallbacks[eventName] = []
                
            ScApp.registeredCallbacks[eventName].append((command, path))
    
def findChosenProperty(command, suffixes):
    suffixChosen = None
    valChosen = None
    for suffix in suffixes:
        val = ScApp.GetProperty('customcommand.' + command + '.action.' + suffix)
        if val:
            if valChosen:
                assert False, 'command %s shouldn\'t have an action for both %s and %s'%(command, suffixChosen, suffix)
            else:
                suffixChosen = suffix
                valChosen = val
    return valChosen, suffixChosen

def addToolsInternalToPythonPath():
    '''Make it easier for scripts to import modules from the tools_internal directory'''
    import os, sys
    dir = os.path.join(ScApp.GetSciteDirectory(), 'tools_internal')
    sys.path.append(dir)

def lookForRegistration():
    addToolsInternalToPythonPath()
    ScApp.SetProperty('ScitePythonExtension.Temp', '$(star *customcommandsregister.)')
    commands = ScApp.GetProperty('ScitePythonExtension.Temp')
    commands = (commands or '').split('|')
    number = 10 # assign this command number, 0 to 9 are given shortcuts Ctrl+0 to Ctrl+9
    heuristicDuplicateShortcut = dict()
    for command in commands:
        command = command.strip()
        if ' ' in command or '\t' in command or '/' in command or '\\' in command:
            assert False, 'command %s has invalid chars' % command
        elif command:
            registerCustomCommand(heuristicDuplicateShortcut, command, number)
            number += 1
    
    if number >= 80:
        print('warning: max number of tools reached.')

def registerCustomCommand(heuristicDuplicateShortcut, command, number):
    # some of the following are 'temporary' because we shouldn't use the value in the future, it's already expanded
    # e.g. if the action contains a reference to '$(FilePath)' then actionTemporary contains the expanded form, frozen
    filetypes = ScApp.GetProperty('customcommand.' + command + '.filetypes')
    callbacks = ScApp.GetProperty('customcommand.' + command + '.callbacks')
    path = ScApp.GetProperty('customcommand.' + command + '.path')
    nameTemporary = ScApp.GetProperty('customcommand.' + command + '.name')
    shortcutTemporary = ScApp.GetProperty('customcommand.' + command + '.shortcut')
    modeTemporary = ScApp.GetProperty('customcommand.' + command + '.mode')
    stdinTemporary = ScApp.GetProperty('customcommand.' + command + '.stdin')
    actionTemporary, subsystem = findChosenProperty(command,
        ['waitforcomplete_console', 'waitforcomplete', 'start', 'py_immediate', 'py'])
    
    isPython = subsystem and subsystem.startswith('py')
    
    if not filetypes:
        filetypes = '*'
    
    if '"' in command or "'" in command or ' ' in command or '\n' in command or '\r' in command:
        assert False, 'in command %s, command name should not have whitespace or quote characters.' % command
    
    if callbacks and (' ' in callbacks or '\t' in callbacks or '/' in callbacks or '\\' in callbacks):
        assert False, 'in command %s, callbacks invalid, expected syntax like OnOpen|OnSave.' % command
    
    if not nameTemporary:
        assert False, 'in command %s, must define a name' % command
        
    if not callbacks and (path and not isPython):
        assert False, 'in command %s, currently path is only needed for python modules' % command
    
    if shortcutTemporary and shortcutTemporary.lower() in heuristicDuplicateShortcut:
        raise RuntimeError('command %s, the shortcut %s was apparently already registered ' % (command, shortcutTemporary))
    else:
        heuristicDuplicateShortcut[(shortcutTemporary or '').lower()] = True
    
    if stdinTemporary and subsystem != 'waitforcomplete_console':
        assert False, 'in command %s, providing stdin only supported for waitforcomplete_console' % command
    
    if not callbacks and (not actionTemporary or not subsystem):
        assert False, 'in command %s, must define exactly one action' % command
    
    if subsystem == 'py_immediate' and actionTemporary and '$(' in actionTemporary:
        assert False, 'in command %s, py_immediate actions cannot contain $() expansions'
    
    # map subsystem names to SciTE's subsystem names
    if subsystem == 'waitforcomplete_console':
        modePrefix = 'subsystem:console,savebefore:no'
    elif subsystem == 'waitforcomplete':
        modePrefix = 'subsystem:windows,savebefore:no'
    elif subsystem == 'start':
        modePrefix = 'subsystem:shellexec,savebefore:no'
    elif subsystem == 'py_immediate':
        modePrefix = 'subsystem:immediate,savebefore:no'
    else:
        modePrefix = 'subsystem:director,savebefore:no'
    
    if modeTemporary:
        modePrefix += ','
    
    actionPrefix = ''
    if subsystem and isPython:
        actionPrefix = 'py:'
        if 'ThisModule()' in actionTemporary:
            assert path, 'in command %s, use of ThisModule requires setting .path'
            actionPrefix += 'ThisModule = lambda: scite_extend_ui.findCallbackModule("%s"); ' % command
    
    if callbacks:
        registerCallbacks(command, path, callbacks)
    
    if actionTemporary:
        # the immediate subsystem apparently doesn't run $() expanation, and so set the action directly.
        if subsystem == 'py_immediate':
            actionSet = actionPrefix + ' ' + actionTemporary
        else:
            actionSet = actionPrefix + '$(customcommand.' + command + '.action.' + subsystem + ')'
            
        ScApp.SetProperty('command.name.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.name)')
        ScApp.SetProperty('command.shortcut.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.shortcut)')
        ScApp.SetProperty('command.mode.%d.%s' % (number, filetypes), modePrefix + '$(customcommand.' + command + '.mode)')
        ScApp.SetProperty('command.input.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.stdin)')
        ScApp.SetProperty('command.%d.%s' % (number, filetypes), actionSet)

try:
    # create singleton instances
    ScEditor = ScPaneClass(0)
    ScOutput = ScPaneClass(1)
    ScApp = ScAppClass()
    ScConst = ScConstClass()
    lookForRegistration()
except:
    import traceback
    traceback.print_exc()
    raise

