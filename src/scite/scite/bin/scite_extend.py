# SciTE Python Extension
# Ben Fisher, 2016

import SciTEModule
import exceptions

debugTracing = False

class ScApp(object):
    '''
    Methods starting with "Cmd" are routed to SciTE,
    See documentation for a list of supported methods.
    example: ScApp.Trace('test')
    example: ScApp.CmdQuit()
    '''
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
        
    def GetFilePath(self):
        return self.GetProperty('FilePath')
        
    def GetFileName(self):
        return self.GetProperty('FileNameExt')
        
    def GetFileDirectory(self):
        return self.GetProperty('FileDir')
        
    def GetLanguage(self):
        return self.GetProperty('Language')
        
    def GetCurrentSelection(self):
        return self.GetProperty('CurrentSelection')
    
    def GetCurrentWord(self):
        return self.GetProperty('CurrentWord')
        
    def GetSciteDirectory(self):
        return self.GetProperty('SciteDefaultHome')
        
    def GetSciteUserDirectory(self):
        return self.GetProperty('SciteUserHome')
        
    def __getattr__(self, s):
        if s.startswith('Cmd'):
            # return a callable object; it looks like a method to the caller.
            return (lambda: SciTEModule.app_SciteCommand(s))
        else:
            raise exceptions.AttributeError

class ScConst(object):
    '''
    ScApp is a class for retrieving a SciTE constants from IFaceTable.cxx
    example: n = ScConst.SCFIND_WHOLEWORD
    See documentation for a list of supported constants.
    '''
    def __init__(self):
        self.eventTypeUnknown = 0
        self.eventTypeClicked = 1
        self.eventTypeChange = 2
        self.eventTypeFocusIn = 3
        self.eventTypeFocusOut = 4
        
    def __getattr__(self, s):
        if s.startswith('_'):
            raise exceptions.AttributeError
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
    
    def StopEventPropagation(self):
        return 'StopEventPropagation'

class ScPane(object):
    '''
    ScPane represents a Scintilla window: either the main code editor or the output pane.
    Methods beginning with 'Get' are property queries sent to Scintilla.
    Methods beginning with 'Set' are property changes sent to Scintilla.
    Methods beginning with 'Cmd' are commands sent to Scintilla.
    See documentation for a list of supported methods.
    
    example: print('language is ' + ScEditor.GetLexerLanguage())
    example: print('using tabs is ' + ScEditor.GetUseTabs())
    example: ScEditor.SetUseTabs(False)
    example: ScEditor.CmdLineDuplicate()
    '''
    
    paneNumber = -1
    def __init__(self, paneNumber):
        self.paneNumber = paneNumber
        
        # some scintilla functions start with the word "get", and aren't property gets.
        self._dictIsScintillaFnNotGetter = dict(GetCurLine=1, GetHotspotActiveBack=1,
            GetHotspotActiveFore=1, GetLastChild=1, GetLexerLanguage=1, GetLine=1,
            GetLineSelEndPosition=1, GetLineSelStartPosition=1, GetProperty=1, GetPropertyExpanded=1,
            GetSelText=1, GetStyledText=1, GetTag=1, GetText=1, GetTextRange=1)
        
        # some scintilla functions start with the word "set", and aren't property sets.
        self._dictIsScintillaFnNotSetter = dict(SetCharsDefault=1, SetFoldFlags=1,
            SetFoldMarginColour=1, SetFoldMarginHiColour=1, SetHotspotActiveBack=1,
            SetHotspotActiveFore=1, SetLengthForEncode=1, SetLexerLanguage=1, SetSavePoint=1,
            SetSel=1, SetSelBack=1, SetSelFore=1, SetSelection=1, SetStyling=1, SetStylingEx=1,
            SetText=1, SetVisiblePolicy=1, SetWhitespaceBack=1, SetWhitespaceFore=1,
            SetXCaretPolicy=1, SetYCaretPolicy=1)
    
    # pane methods
    def Append(self, txt):
        return SciTEModule.pane_Append(self.paneNumber, txt)

    def InsertText(self, txt, pos):
        return SciTEModule.pane_Insert(self.paneNumber, pos, txt)
        
    def Remove(self, npos1, npos2):
        return SciTEModule.pane_Remove(self.paneNumber, npos1, npos2)
        
    def GetText(self, n1, n2):
        return SciTEModule.pane_Textrange(self.paneNumber, n1, n2)
    
    def FindText(self, s, pos1=0, pos2=-1, wholeWord=False, matchCase=False, regExp=False, flags=0): 
        if wholeWord:
            flags |= SciTEModule.ScConst.SCFIND_WHOLEWORD
        if matchCase:
            flags |= SciTEModule.ScConst.SCFIND_MATCHCASE
        if regExp:
            flags |= SciTEModule.ScConst.SCFIND_REGEXP
            
        return SciTEModule.pane_FindText(self.paneNumber, s, flags, pos1, pos2)
        
    # helpers
    def Write(self, txt, pos=-1):
        if pos == -1:
            pos = self.GetCurrentPos()
        SciTEModule.pane_Insert(self.paneNumber, pos, txt)
        self.CmdGotoPos(pos + len(txt))
        
    def GetAllText(self):
        return self.CmdTextrange(0, self.GetLength())
        
    def GetCurLine(self):
        nLine = self.CmdLineFromPosition(self.GetCurrentPos())
        return self.GetLine(nLine)
        
    def CopyText(self, s):
        return SciTEModule.pane_ScintillaFn(self.paneNumber, 'CopyText', (len(s),s))
        
    def SetText(self, s):
        return SciTEModule.pane_ScintillaFn(self.paneNumber, 'SetText', (None, s))
        
    def AutoCStops(self, s):
        return SciTEModule.pane_ScintillaFn(self.paneNumber, 'AutoCStops', (None, s))
        
    def AutoCSelect(self, s):
        return SciTEModule.pane_ScintillaFn(self.paneNumber, 'AutoCSelect', (None, s))
        
    def ReplaceSel(self, s):
        return SciTEModule.pane_ScintillaFn(self.paneNumber, 'ReplaceSel', (None, s))
        
    def SetLexerLanguage(self, s):
        return SciTEModule.pane_ScintillaFn(self.paneNumber, 'SetLexerLanguage', (None, s))
        
    def LoadLexerLibrary(self, s):
        return SciTEModule.pane_ScintillaFn(self.paneNumber, 'LoadLexerLibrary', (None, s))

    # getters and setters
    def __getattr__(self, sprop):
        if sprop.startswith('Get'):
            if sprop in self._dictIsScintillaFnNotGetter:
                return (lambda *args: SciTEModule.pane_ScintillaFn(self.paneNumber, sprop, args))
            else:
                sprop = sprop[3:]
                return (lambda param=None: SciTEModule.pane_ScintillaGet(self.paneNumber, sprop, param))
        elif sprop.startswith('Set'):
            if sprop in self._dictIsScintillaFnNotSetter:
                return (lambda *args: SciTEModule.pane_ScintillaFn(self.paneNumber, sprop, args))
            else:
                sprop = sprop[3:]
                return (lambda a1, a2=None: SciTEModule.pane_ScintillaSet(self.paneNumber, sprop, a1, a2))
        elif sprop.startswith('Cmd'):
            sprop = sprop[3:]
            return (lambda *args: SciTEModule.pane_ScintillaFn(self.paneNumber, sprop, args))
        else:
            raise exceptions.AttributeError
    
def OnEvent(eventName, args):
    # user strip events are handled differently
    if eventName == 'OnUserStrip':
        return SciTEModule.ScToolUIManager.OnUserStrip(*args)
        
    callbacks = SciTEModule.registeredCallbacks.get(eventName, None)
    if callbacks:
        for command, path in callbacks:
            try:
                module = findCallbackModuleFromPath(command, path)
                val = callCallbackModule(module, command, eventName, args)
                if val == SciTEModule.ScConst.StopEventPropagation():
                    # the user has asked that we not process any other callbacks
                    return val
            except Exception:
                # print the Exception, but let other event handlers run
                import traceback
                print('Exception thrown when calling event %s for %s; %s' % (eventName, command, traceback.format_exc()))

def findCallbackModuleFromPath(command, path):
    # it's more intuitive for each module's state to persist.
    cached = SciTEModule.cacheCallbackModule.get(path, None)
    if cached:
        return cached
    
    import sys, os, importlib
    expectedPythonModdir = os.path.join(SciTEModule.ScApp.GetSciteDirectory(), path)
    expectedPythonInit = os.path.join(expectedPythonModdir, '__init__.py')
    if not os.path.isfile(expectedPythonInit):
        raise RuntimeError, 'command %s could not find a file at %s' % (command, expectedPythonInit)
    
    # I could use imp.load_source to load the __init__.py directly, but then it can't access its submodules
    pathsaved = sys.path
    try:
        sys.path.append(os.path.split(expectedPythonModdir)[0])
        module = importlib.import_module(os.path.split(expectedPythonModdir)[1])
    finally:
        sys.path = pathsaved
    
    SciTEModule.cacheCallbackModule[path] = module
    return module

def findCallbackModule(command):
    path = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.path')
    assert path, 'in command %s, path must be defined to use ThisModule.' % command
    return findCallbackModuleFromPath(command, path)

def callCallbackModule(module, command, eventName, args):
    function = getattr(module, eventName, None)
    if not function:
        raise RuntimeError, 'command %s registered for event %s but we could not find function of this name' % (command, eventName)
    else:
        return function(*args)

def registerCallbacks(command, path, callbacks):
    assert path, 'in command %s, defining a callback requires specifying a path' % command
    
    callbacks = (callbacks or '').split('|')
    for eventName in callbacks:
        eventName = eventName.strip()
        if eventName:
            assert eventName.startswith('On')
            SciTEModule.ScApp.EnableNotification(eventName)
            
            if eventName not in SciTEModule.registeredCallbacks:
                SciTEModule.registeredCallbacks[eventName] = []
                
            SciTEModule.registeredCallbacks[eventName].append((command, path))
    
def findChosenProperty(command, suffixes):
    suffixChosen = None
    valChosen = None
    for suffix in suffixes:
        val = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.action.' + suffix)
        if val != None:
            if valChosen != None:
                assert False, 'command %s shouldn\'t have an action for both %s and %s'%(command, suffixChosen, suffix)
            else:
                suffixChosen = suffix
                valChosen = val
    return valChosen, suffixChosen

def lookForRegistration():
    SciTEModule.ScApp.SetProperty('ScitePythonExtension.Temp', '$(star *customcommandsregister.)')
    commands = SciTEModule.ScApp.GetProperty('ScitePythonExtension.Temp')
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
    filetypes = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.filetypes')
    callbacks = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.callbacks')
    path = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.path')
    nameTemporary = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.name')
    shortcutTemporary = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.shortcut')
    modeTemporary = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.mode')
    stdinTemporary = SciTEModule.ScApp.GetProperty('customcommand.' + command + '.stdin')
    actionTemporary, subsystem = findChosenProperty(command, ['waitforcomplete_console', 'waitforcomplete', 'start', 'py'])
    
    if not filetypes:
        filetypes = '*'
    
    if callbacks and (' ' in callbacks or '\t' in callbacks or '/' in callbacks or '\\' in callbacks):
        assert False, 'in command %s, callbacks invalid, expected syntax like OnOpen|OnSwitchFile.' % command
    
    if not nameTemporary:
        assert False, 'in command %s, must define a name' % command
        
    if path and subsystem != 'py':
        assert False, 'in command %s, currently path is only needed for python modules' % command
    
    if shortcutTemporary and shortcutTemporary.lower() in heuristicDuplicateShortcut:
        raise RuntimeError, 'command %s, the shortcut %s was apparently already registered ' % (command, shortcutTemporary)
    else:
        heuristicDuplicateShortcut[(shortcutTemporary or '').lower()] = True
    
    if stdinTemporary and subsystem != 'waitforcomplete_console':
        assert False, 'in command %s, providing stdin only supported for waitforcomplete_console' % command
    
    if not actionTemporary or not subsystem:
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
        actionPrefix = 'py:from SciTEModule import findCallbackModule, ScEditor, ScOutput, ScApp, ScConst; '
        if 'ThisModule()' in actionTemporary:
            assert path, 'in command %s, use of ThisModule requires setting .path'
            actionPrefix += 'ThisModule = lambda: findCallbackModule("%s"); ' % command
    
    if callbacks:
        registerCallbacks(command, path, callbacks)
                
    SciTEModule.ScApp.SetProperty('command.name.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.name)')
    SciTEModule.ScApp.SetProperty('command.shortcut.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.shortcut)')
    SciTEModule.ScApp.SetProperty('command.mode.%d.%s' % (number, filetypes), modePrefix + '$(customcommand.' + command + '.mode)')
    SciTEModule.ScApp.SetProperty('command.input.%d.%s' % (number, filetypes), '$(customcommand.' + command + '.stdin)')
    SciTEModule.ScApp.SetProperty('command.%d.%s' % (number, filetypes), actionPrefix + '$(customcommand.' + command + '.action.' + subsystem + ')')
        

from scite_extend_ui import ScToolUIManager, ScToolUIBase
SciTEModule.ScEditor = ScPane(0)
SciTEModule.ScOutput = ScPane(1)
SciTEModule.ScApp = ScApp()
SciTEModule.ScConst = ScConst()
SciTEModule.ScToolUIManager = ScToolUIManager()
SciTEModule.ScToolUIBase = ScToolUIBase
SciTEModule.registeredCallbacks = dict()
SciTEModule.cacheCallbackModule = dict()
SciTEModule.findCallbackModule = findCallbackModule

lookForRegistration()

