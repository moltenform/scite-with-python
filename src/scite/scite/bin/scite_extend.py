# SciTE Python Extension
# Ben Fisher, 2016

import SciTEModule
import exceptions


# ScApp is a normal app



class ScPane():
	paneNumber = -1
	def __init__(self, paneNumber):
		self.paneNumber = paneNumber
		
	#Custom helpers
	def Write(self, txt, pos=-1):
		if pos==-1: pos = self.GetCurrentPos()
		SciTEModule.pane_Insert(self.paneNumber, pos, txt)
		self.GotoPos(pos+len(txt))
	def GetAllText(self):
		return self.Textrange(0, self.GetLength())
		
	# overrides to make it simpler for callers.
	def GetCurLine(self):
		nLine = self.LineFromPosition(self.GetCurrentPos())
		return self.GetLine(nLine)
	def CopyText(self, s): return SciTEModule.pane_ScintillaFn(self.paneNumber, 'CopyText', (len(s),s))
	def SetText(self, s): return SciTEModule.pane_ScintillaFn(self.paneNumber, 'SetText', (None, s))
	def AutoCStops(self, s): return SciTEModule.pane_ScintillaFn(self.paneNumber, 'AutoCStops', (None, s))
	def AutoCSelect(self, s): return SciTEModule.pane_ScintillaFn(self.paneNumber, 'AutoCSelect', (None, s))
	def ReplaceSel(self, s): return SciTEModule.pane_ScintillaFn(self.paneNumber, 'ReplaceSel', (None, s))
	def SetLexerLanguage(self, s): return SciTEModule.pane_ScintillaFn(self.paneNumber, 'SetLexerLanguage', (None, s))
	def LoadLexerLibrary(self, s): return SciTEModule.pane_ScintillaFn(self.paneNumber, 'LoadLexerLibrary', (None, s))

	# pane methods
	def Append(self, txt): return SciTEModule.pane_Append(self.paneNumber, txt)
	def InsertText(self, txt, pos): return SciTEModule.pane_Insert(self.paneNumber,pos, txt)
	def Remove(self, npos1, npos2): return SciTEModule.pane_Remove(self.paneNumber, npos1, npos2)
	def Textrange(self, n1, n2): return SciTEModule.pane_Textrange(self.paneNumber, n1, n2)
	# SciTEModule.pane_ScintillaFn(self.paneNumber, s, *args)  (see __getattr__)
	# SciTEModule.pane_ScintillaGet(self.paneNumber, s, *args)  (see __getattr__)
	# SciTEModule.pane_ScintillaSet(self.paneNumber, s, *args)  (see __getattr__)
	def FindText(self,s,n1=0,n2=-1,wholeWord=False,matchCase=False,regExp=False, nFlags=0): 
		if wholeWord: nFlags |= SciTEModule.ScApp.SCFIND_WHOLEWORD
		if matchCase: nFlags |= SciTEModule.ScApp.SCFIND_MATCHCASE
		if regExp: nFlags |= SciTEModule.ScApp.SCFIND_REGEXP
		return SciTEModule.pane_FindText(self.paneNumber,s,nFlags,n1,n2)
	
	
	
	def __getattr__(self, sprop):
		if sprop.startswith('_'):
			#if looking for a special method, don't try to do anything.
			raise exceptions.AttributeError
		elif sprop.startswith('Get'):
			if sprop in SciTEModule._dictIsScintillaFnNotGetter:
				return (lambda *args: SciTEModule.pane_ScintillaFn(self.paneNumber, sprop, args))
			else:
				sprop = sprop[3:]
				return (lambda param=None: SciTEModule.pane_ScintillaGet(self.paneNumber, sprop, param))
		elif sprop.startswith('Set'):
			if sprop in SciTEModule._dictIsScintillaFnNotSetter:
				return (lambda *args: SciTEModule.pane_ScintillaFn(self.paneNumber, sprop, args))
			else:
				sprop = sprop[3:]
				return (lambda a1, a2=None: SciTEModule.pane_ScintillaSet(self.paneNumber, sprop, a1, a2))
		else:
			return (lambda *args: SciTEModule.pane_ScintillaFn(self.paneNumber, sprop, args))
		raise exceptions.AttributeError
	
	def MakeKeymod(self, keycode, fShift=False, fCtrl=False, fAlt=False):
		keycode = keycode&0xffff
		modifiers = 0
		if fShift: modifiers |= SciTEModule.ScApp.SCMOD_SHIFT
		if fCtrl: modifiers |= SciTEModule.ScApp.SCMOD_CTRL
		if fAlt: modifiers |= SciTEModule.ScApp.SCMOD_ALT
		return keycode | (modifiers << 16)
	def MakeColor(self, red, green, blue):
		assert 0<=red<=255
		assert 0<=green<=255
		assert 0<=blue<=255
		return red + (green << 8) + (blue << 16)
	def GetColor(self, val):
		red = val & 0x000000ff
		green = (val & 0x0000ff00) >> 8
		blue = (val & 0x000ff0000) >> 16
		return (red, green, blue)
	

class ScApp():
	def Trace(self, s): return SciTEModule.app_Trace(s)
	def MsgBox(self, s): return SciTEModule.app_MsgBox(s)
	def OpenFile(self, s): return SciTEModule.app_OpenFile(s)
	def GetProperty(self, s): return SciTEModule.app_GetProperty(s)
	def SetProperty(self, s, v): return SciTEModule.app_SetProperty(s, v)
	def UnsetProperty(self, s): return SciTEModule.app_UnsetProperty(s)
	def UpdateStatusBar(self, v=None): return SciTEModule.app_UpdateStatusBar(v)
	# SciTEModule.app_SciteCommand(self.paneNumber, s, *args)  (see __getattr__)
	# SciTEModule.app_GetConstant(self.paneNumber, s, *args)  (see __getattr__)
	
	def __getattr__(self, s):
		if s.startswith('_'):
			#if looking for a special method, don't try to do anything.
			raise exceptions.AttributeError
		elif s.upper() == s and '_' in s:
			return SciTEModule.app_GetConstant(s)
		else:
			return (lambda: SciTEModule.app_SciteCommand(s))
	
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
	
	# limitation: if this is called many times, it will only run once. alternative is to write own grep script, or to use symlinks of desired directories
	# benefit: faster than launching external program
	def ScheduleFindInFiles(self, sQuery, sDirectory=None, filetypes=None, wholeword=None, matchcase=None):
		# find.input is not the right property to set.
		# also, don't change find.command to '', because user might want to use custom app.
		SciTEModule.ScApp.SetProperty('find.what', sQuery)
		
		if sDirectory!=None: SciTEModule.ScApp.SetProperty('find.directory', sDirectory)
		if filetypes!=None: SciTEModule.ScApp.SetProperty('find.files', filetypes)
		if wholeword!=None: SciTEModule.ScApp.SetProperty('find.filesnow.wholeword', '1' if wholeword else '')
		if matchcase!=None: SciTEModule.ScApp.SetProperty('find.filesnow.matchcase', '1' if matchcase else '')
		SciTEModule.ScApp.FindInFilesStart()
		

# some methods start with "get" but are actually a "function". user shouldn't care about this implementation detail
SciTEModule._dictIsScintillaFnNotGetter = {
"GetCurLine":1, "GetHotspotActiveBack":1, "GetHotspotActiveFore":1, "GetLastChild":1, "GetLexerLanguage":1, "GetLine":1, "GetLineSelEndPosition":1, "GetLineSelStartPosition":1, "GetProperty":1, "GetPropertyExpanded":1, "GetSelText":1, "GetStyledText":1, "GetTag":1, "GetText":1, "GetTextRange":1 }
SciTEModule._dictIsScintillaFnNotSetter = {
"SetCharsDefault":1, "SetFoldFlags":1, "SetFoldMarginColour":1, "SetFoldMarginHiColour":1, "SetHotspotActiveBack":1, "SetHotspotActiveFore":1, "SetLengthForEncode":1, "SetLexerLanguage":1, "SetSavePoint":1, "SetSel":1, "SetSelBack":1, "SetSelFore":1, "SetSelection":1, "SetStyling":1, "SetStylingEx":1, "SetText":1, "SetVisiblePolicy":1, "SetWhitespaceBack":1, "SetWhitespaceFore":1, "SetXCaretPolicy":1, "SetYCaretPolicy":1 }


SciTEModule.ScEditor = ScPane(0)
SciTEModule.ScOutput = ScPane(1)
SciTEModule.ScApp = ScApp()

echoEvents = True

def OnStart():
	if echoEvents: print 'See OnStart'

def OnOpen(filename):
	if echoEvents: print 'See OnOpen', filename

def OnClose(filename):
	if echoEvents: print 'See OnClose', filename

def OnMarginClick():
	if echoEvents: 
		print 'See OnMarginClick'

def OnSwitchFile(filename):
	if echoEvents: print 'See OnSwitchFile', filename
	# testing if ScApp commands can be sent
	SciTEModule.ScApp.Quit()
	
def OnBeforeSave(filename):
	if echoEvents: print 'See OnBeforeSave', filename
	
def OnSave(filename):
	if echoEvents: print 'See OnSave', filename
	
def OnSavePointReached():
	if echoEvents: print 'See OnSavePointReached'
	
def OnSavePointLeft():
	if echoEvents: print 'See OnSavePointLeft'

def OnChar(nChar):
	pass

def OnDoubleClick():
	if echoEvents: print 'See OnDoubleClick'

def OnUserListSelection(type, selectedText):
	if echoEvents: print 'See OnUserListSelection', type, selectedText


def OnKey(keycode, shift, ctrl, alt):
	if echoEvents: 
		print 'See OnKey', keycode, shift, ctrl, alt
		
