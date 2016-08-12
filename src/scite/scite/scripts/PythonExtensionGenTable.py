
# use this script to generate the table of constants
# static IFaceConstant rgFriendlyNamedIDMConstants[]
# in PythonExtension.cxx

# the results will be printed to stdout, to update the table
# you'll have to manually paste into PythonExtension.cxx.

# the goal is to map from symbol names like IDM_ABBREV
# to method names like ScApp.CmdAbbrev()
# 'currentNames' are constants that have already been assigned a method name
# so, if the constants has been changed and this script is run,
# 		if "NOTSEENBEFORE" is seen in the output, this means new constants have been added.
#  			please add the constant number and an appropriate method name to currentNames
#  		if "assert False, 'was the constant name changed?" is seen, this means constants name was changed.
# 			please update currentNames to reflect the name change.
# PythonExtensionGenTable.py will then run cleanly after making these updates.

currentNames = '''242|Abbrev
902|About
320|Activate
119|AllowAccess
243|BlockComment
224|BookmarkClearAll
221|BookmarkNext
225|BookmarkNextSelect
223|BookmarkPrev
226|BookmarkPrevSelect
222|BookmarkToggle
246|BoxComment
1200|Buffer
505|BufferSep
302|Build
308|Clean
206|Clear
420|ClearOutput
105|Close
503|CloseAll
301|Compile
233|Complete
234|CompleteWord
204|Copy
245|CopyAsRtf
118|CopyPath
203|Cut
806|DirectionDown
805|DirectionUp
250|Duplicate
150|EncodingDefault
154|EncodingUCookie
151|EncodingUcs2be
152|EncodingUcs2le
153|EncodingUtf8
256|EnterSelection
433|EolConvert
431|EolCr
430|EolCrlf
432|EolLf
235|Expand
238|ExpandEnsureChildrenVisible
114|Filer
210|Find
215|FindInFiles
211|FindNext
212|FindNextBack
214|FindNextBackSel
213|FindNextSel
305|FinishedExecute
406|FoldMargin
961|FullScreen
303|Go
220|Goto
901|Help
903|HelpScite
1300|Import
247|InsAbbrev
248|Join
1400|Language
407|LineNumberMargin
132|LoadSession
241|LwrCase
314|MacroList
313|MacroPlay
311|MacroRecord
312|MacroStopRecord
310|MacroSep
230|MatchBrace
801|MatchCase
450|MonoFont
509|MoveTabLeft
508|MoveTabRight
1000|MruFile
120|MruSep
121|MruSub
101|New
502|NextFile
507|NextFileStack
262|NextMatchPpc
306|NextMsg
960|OnTop
102|Open
463|OpenAbbrevProperties
465|OpenDirectoryProperties
413|OpenFilesHere
462|OpenGlobalProperties
460|OpenLocalProperties
464|OpenLuaExternalfile
103|OpenSelected
461|OpenUserProperties
205|Paste
208|PasteAndDown
501|PrevFile
506|PrevFileStack
260|PrevMatchPpc
307|PrevMsg
131|Print
130|PrintSetup
140|Quit
416|ReadOnly
202|Redo
802|Regexp
216|Replace
104|Revert
351|RunWin
106|Save
116|SaveACopy
504|SaveAll
110|SaveAs
111|SaveAsHtml
113|SaveAsPdf
112|SaveAsRtf
115|SaveAsTex
117|SaveAsXml
133|SaveSession
207|SelectAll
258|SelectionAddEach
257|SelectionAddNext
217|SelectionForFind
231|SelectToBrace
263|SelectToNextMatchPpc
261|SelectToPrevMatchPpc
405|SelMargin
232|ShowCalltip
249|Split
401|SplitVertical
350|SrcWin
353|StatusWin
304|StopExecute
244|StreamComment
421|SwitchPane
440|TabSize
354|TabWin
409|ToggleOutput
412|ToggleParameters
236|ToggleFoldAll
237|ToggleFoldRecursive
1100|Tools
352|ToolWin
201|Undo
804|Unslash
240|UprCase
403|ViewEol
404|ViewGuides
402|ViewSpace
411|ViewStatusBar
410|ViewTabBar
408|ViewToolbar
800|WholeWord
414|Wrap
803|WrapAround
415|WrapOutput
252|IncrementalSearch|was IncSearch
240|UpperCase|was UprCase
241|LowerCase|was LwrCase'''

def getMap():
	map = {}
	for line in currentNames.replace('\r\n', '\n').split('\n'):
		parts = line.split('|')
		id = int(parts[0])
		methodName = parts[1]
		nameIntentionallyChanged = len(parts) > 2
		map[id] = (methodName, nameIntentionallyChanged)
		
	return map

def go():
	import sys
	if sys.version_info[0] != 2:
		print('currently, this script is not supported in python 3')
		return
	
	map = getMap()
	results = []
	for line in open(pathToSciteH):
		line = line.strip()
		if line.startswith('#define IDM_'):
			_, origname, val = line.split()
			id = int(val)
			if id not in map:
				results.append('{"' + id + '", NOTSEENBEFORE ' + id + '},')
			else:
				methodName, nameIntentionallyChanged = map[id]
				nameLower = origname.replace('IDM_', '').lower().replace('_', '')
				if not nameIntentionallyChanged and nameLower != methodName.lower():
					assert False, 'was the constant name changed? expected %s and got %s' % (nameLower, methodName)
				
				results.append('{"' + methodName + '", ' + origname + '},')
					
	# must be sorted, because we use the list for binary search.
	results.sort()
	for line in results:
		print(line)
	
if __name__ == "__main__":
	pathToSciteH = '../src/SciTE.h'
	go()
