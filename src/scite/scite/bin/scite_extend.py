# SciTE Python Extension
# Ben Fisher, 2016

# from CScite import ScEditor, ScOutput, ScApp

echoEvents = True

def OnStart():
	if echoEvents: print 'See OnStart'

def OnLoad(filename):
	if echoEvents: print 'See OnLoad', filename

def OnOpen(filename):
	if echoEvents: print 'See OnOpen', filename

def OnClose(filename):
	if echoEvents: print 'See OnClose', filename

def OnMarginClick():
	if echoEvents: 
		print 'See OnMarginClick'

def OnSwitchFile(filename):
	if echoEvents: print 'See OnSwitchFile', filename
	
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
		

