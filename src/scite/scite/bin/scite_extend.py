# SciTE Python Extension
# Ben Fisher, 2016

import SciTEModule

debugTracing = False

class ScAppClass(object):
    '''
    Methods starting with "Cmd" are routed to SciTE,
    See documentation for a list of supported methods.
    example:
        from scite_extend_ui import ScApp
        ScApp.Trace('test')
        ScApp.CmdQuit()
    '''
    def __init__(self):
        self.registeredCallbacks = dict()
        self.cachedCallbackModules = dict()
    
    def Trace(self, s):
        return SciTEModule.app_Trace(s)
    
    def MsgBox(self, s):
        return SciTEModule.app_MsgBox(s)
        
    def OpenFile(self, s):
        return SciTEModule.app_OpenFile(s)
        
    def GetProperty(self, s):
        return SciTEModule.app_GetProperty(s)
        
    def SetProperty(self, s, v):
        if debugTracing:
            print('SetProperty %s=%s'%(s, v))

        return SciTEModule.app_SetProperty(s, v)
    
    def UnsetProperty(self, s):
        return SciTEModule.app_UnsetProperty(s)
        
    def UpdateStatusBar(self, updateSlowData=False):
        return SciTEModule.app_UpdateStatusBar(updateSlowData)
        
    def EnableNotification(self, eventName, enabled=True):
        return SciTEModule.app_EnableNotification(eventName, 1 if enabled else 0)
    
    def LocationNext(self):
        return SciTEModule.app_GetNextOrPreviousLocation(1)
        
    def LocationPrev(self):
        return SciTEModule.app_GetNextOrPreviousLocation(0)
        
    def _printSupportedCalls(self, whatToPrint=2):
        # 1=constants, 2=app methods, 3=pane methods (as called), 4=pane methods (as defined internally)
        ScOutput.BeginUndoAction()
        SciTEModule.app_PrintSupportedCalls(whatToPrint)
        ScOutput.EndUndoAction()
    
    def GetFilePath(self, cannotBeUntitled=True):
        if cannotBeUntitled:
            # we usually don't want untitled documents to look like they have a path
            return self.GetProperty('FilePath') if len(self.GetFileName()) > 0 else ''
        else:
            return self.GetProperty('FilePath')
        
    def GetFileName(self):
        return self.GetProperty('FileNameExt')
        
    def GetFileDirectory(self):
        return self.GetProperty('FileDir')
        
    def GetSciteDirectory(self):
        return self.GetProperty('SciteDefaultHome')
        
    def GetSciteUserDirectory(self):
        return self.GetProperty('SciteUserHome')
        
    def __getattr__(self, s):
        if s.startswith('Cmd'):
            # return a callable object; it looks like a method to the caller.
            commandName =  s[len('Cmd'):]
            return (lambda: SciTEModule.app_SciteCommand(commandName))
        else:
            raise AttributeError()

class ScConstClass(object):
    '''
    a class for retrieving a SciTE constants from IFaceTable.cxx
    example:
        from scite_extend_ui import ScConst 
        n = ScConst.SCFIND_WHOLEWORD
    See documentation for a list of supported constants.
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
        print(ScEditor.Utils.GetEolCharacter())
    '''
    pane = None
    def __init__(self, pane):
        self.pane = pane
        
    def GetAllText(self):
        return self.pane.Textrange(0, self.pane.GetLength())
        
    def GetCurLine(self):
        nLine = self.pane.LineFromPosition(self.pane.GetCurrentPos())
        return self.pane.GetLine(nLine)
    
    def GetEolCharacter(self):
        n = self.pane.GetEOLMode()
        if n == 0:
            return '\r\n'
        elif n == 1:
            return '\r'
        else:
            return '\n'
            
    def ExpandSelectionToIncludeEntireLines(self):
        startline = self.pane.LineFromPosition(self.pane.GetSelectionStart())
        endline = self.pane.LineFromPosition(self.pane.GetSelectionEnd()) + 1
        startpos = self.pane.PositionFromLine(startline)
        endpos = self.pane.PositionFromLine(endline)
        
        # endpos might be at a newline character, though, so subtract from the selection until it is not.
        while self.pane.GetCharAt(endpos - 1) in (ord('\r'), ord('\n')):
            endpos -= 1
        self.pane.SetSelection(startpos, endpos)
        
class ScPaneClass(object):
    '''
    represents a Scintilla window, either the main code editor or the output pane.
    Methods beginning with 'Get' are property queries sent to Scintilla.
    Methods beginning with 'Set' are property changes sent to Scintilla.
    Methods beginning with 'Cmd' are commands sent to Scintilla.
    See documentation for a list of supported methods.
    example:
        from scite_extend_ui import ScEditor
        print('language is ' + ScEditor.GetLexerLanguage())
        print('using tabs is ' + ScEditor.GetUseTabs())
        ScEditor.SetUseTabs(False)
        ScEditor.LineDuplicate()
    '''
    
    paneNumber = -1
    def __init__(self, paneNumber):
        self.paneNumber = paneNumber
        self.Utils = ScPaneClassUtils(self)
    
    # pane methods
    def PaneAppend(self, txt):
        return SciTEModule.pane_Append(self.paneNumber, txt)

    def PaneInsertText(self, txt, pos):
        return SciTEModule.pane_Insert(self.paneNumber, pos, txt)
        
    def PaneRemoveText(self, npos1, npos2):
        return SciTEModule.pane_Remove(self.paneNumber, npos1, npos2)
        
    def PaneGetText(self, n1, n2):
        return SciTEModule.pane_Textrange(self.paneNumber, n1, n2)
    
    def PaneFindText(self, s, pos1=0, pos2=-1, wholeWord=False, matchCase=False, regExp=False, flags=0): 
        if wholeWord:
            flags |= ScConst.SCFIND_WHOLEWORD
        if matchCase:
            flags |= ScConst.SCFIND_MATCHCASE
        if regExp:
            flags |= ScConst.SCFIND_REGEXP
            
        return SciTEModule.pane_FindText(self.paneNumber, s, flags, pos1, pos2)
        
    def PaneWrite(self, txt, pos=None):
        if pos is None:
            pos = self.GetCurrentPos()
        SciTEModule.pane_Insert(self.paneNumber, pos, txt)
        self.GotoPos(pos + len(txt))
    
    # helpers where the Scintilla version is less convenient to use
    def GetLineText(self, line):
        return self.GetLine(line)[0]
    
    def GetSelectedText(self):
        return self.GetSelText()[0]
        
    def GetCurrentLineText(self):
        return self.GetCurLine()[0]

    # redirect most methods on this object to call into Scintilla.
    def __getattr__(self, sprop):
        if sprop.startswith('_'):
            raise AttributeError()
        else:
            return (lambda *args: SciTEModule.pane_SendScintilla(self.paneNumber, sprop, *args))

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
        raise RuntimeError, 'command %s could not find a file at %s' % (command, expectedPythonInit)
    
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
        raise RuntimeError, 'command %s registered for event %s but we could not find function of this name' % (command, eventName)
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
    actionTemporary, subsystem = findChosenProperty(command, ['waitforcomplete_console', 'waitforcomplete', 'start', 'py'])
    
    if not filetypes:
        filetypes = '*'
    
    if callbacks and (' ' in callbacks or '\t' in callbacks or '/' in callbacks or '\\' in callbacks):
        assert False, 'in command %s, callbacks invalid, expected syntax like OnOpen|OnSave.' % command
    
    if not nameTemporary:
        assert False, 'in command %s, must define a name' % command
        
    if not callbacks and (path and subsystem != 'py'):
        assert False, 'in command %s, currently path is only needed for python modules' % command
    
    if shortcutTemporary and shortcutTemporary.lower() in heuristicDuplicateShortcut:
        raise RuntimeError, 'command %s, the shortcut %s was apparently already registered ' % (command, shortcutTemporary)
    else:
        heuristicDuplicateShortcut[(shortcutTemporary or '').lower()] = True
    
    if stdinTemporary and subsystem != 'waitforcomplete_console':
        assert False, 'in command %s, providing stdin only supported for waitforcomplete_console' % command
    
    if not callbacks and (not actionTemporary or not subsystem):
        assert False, 'in command %s, must define exactly one action' % command
    
    # map subsystem names to SciTE's subsystem names
    if subsystem == 'waitforcomplete_console':
        modePrefix = 'subsystem:console,savebefore:no'
    elif subsystem == 'waitforcomplete':
        modePrefix = 'subsystem:windows,savebefore:no'
    elif subsystem == 'start':
        modePrefix = 'subsystem:shellexec,savebefore:no'
    else:
        modePrefix = 'subsystem:director,savebefore:no'
    
    if modeTemporary:
        modePrefix += ','
    
    actionPrefix = ''
    if subsystem == 'py':
        actionPrefix = 'py:from scite_extend_ui import *; '
        if 'ThisModule()' in actionTemporary:
            assert path, 'in command %s, use of ThisModule requires setting .path'
            actionPrefix += 'ThisModule = lambda: findCallbackModule("%s"); ' % command
    
    if callbacks:
        registerCallbacks(command, path, callbacks)
    
    if actionTemporary:
        ScApp.SetProperty('command.name.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.name)')
        ScApp.SetProperty('command.shortcut.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.shortcut)')
        ScApp.SetProperty('command.mode.%d.%s' % (number, filetypes), modePrefix + '$(customcommand.' + command + '.mode)')
        ScApp.SetProperty('command.input.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.stdin)')
        ScApp.SetProperty('command.%d.%s' % (number, filetypes), actionPrefix + '$(customcommand.' + command + '.action.' + subsystem + ')')
        
# create singleton instances
ScEditor = ScPaneClass(0)
ScOutput = ScPaneClass(1)
ScApp = ScAppClass()
ScConst = ScConstClass()
lookForRegistration()

