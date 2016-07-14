# SciTE Python Extension
# Ben Fisher, 2016

import SciTEModule
import exceptions


class ScApp():
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
        return SciTEModule.app_SetProperty(s, v)
    
    def UnsetProperty(self, s):
        return SciTEModule.app_UnsetProperty(s)
        
    def UpdateStatusBar(self, v=None):
        return SciTEModule.app_UpdateStatusBar(v)
        
    def GetFilePath(self):
        return self.GetProperty('FilePath')
        
    def GetFileName(self):
        return self.GetProperty('FileNameExt')
        
    def GetLanguage(self):
        return self.GetProperty('Language')
        
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


class ScConst():
    '''
    ScApp is a class for retrieving a SciTE constants from IFaceTable.cxx
    example: n = ScConst.SCFIND_WHOLEWORD
    See documentation for a list of supported constants.
    '''
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


class ScPane():
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
        
    def Textrange(self, n1, n2):
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
        self.GotoPos(pos + len(txt))
        
    def GetAllText(self):
        return self.Textrange(0, self.GetLength())
        
    def GetCurLine(self):
        nLine = self.LineFromPosition(self.GetCurrentPos())
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


SciTEModule.ScEditor = ScPane(0)
SciTEModule.ScOutput = ScPane(1)
SciTEModule.ScApp = ScApp()
SciTEModule.ScConst = ScConst()

echoEvents = True

def OnEvent(eventName, args):
    print eventName, args

