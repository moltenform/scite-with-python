
knownNames = '''{"Abbrev", 242},
{"About", 902},
{"Activate", 320},
{"AllowAccess", 119},
{"BlockComment", 243},
{"BookmarkClearAll", 224},
{"BookmarkNext", 221},
{"BookmarkNextSelect", 225},
{"BookmarkPrev", 223},
{"BookmarkPrevSelect", 226},
{"BookmarkToggle", 222},
{"BoxComment", 246},
{"Buffer", 1200},
{"BufferSep", 505},
{"Build", 302},
{"Clean", 308},
{"Clear", 206},
{"ClearOutput", 420},
{"Close", 105},
{"CloseAll", 503},
{"Compile", 301},
{"Complete", 233},
{"CompleteWord", 234},
{"Copy", 204},
{"CopyAsRtf", 245},
{"CopyPath", 118},
{"Cut", 203},
{"DirectionDown", 806},
{"DirectionUp", 805},
{"Duplicate", 250},
{"EncodingDefault", 150},
{"EncodingUCookie", 154},
{"EncodingUcs2be", 151},
{"EncodingUcs2le", 152},
{"EncodingUtf8", 153},
{"EnterSelection", 256},
{"EolConvert", 433},
{"EolCr", 431},
{"EolCrlf", 430},
{"EolLf", 432},
{"Expand", 235},
{"ExpandEnsureChildrenVisible", 238},
{"Filer", 114},
{"Find", 210},
{"FindInFiles", 215},
{"FindNext", 211},
{"FindNextBack", 212},
{"FindNextBackSel", 214},
{"FindNextSel", 213},
{"FinishedExecute", 305},
{"FoldMargin", 406},
{"FullScreen", 961},
{"Go", 303},
{"Goto", 220},
{"Help", 901},
{"HelpScite", 903},
{"Import", 1300},
{"InsAbbrev", 247},
{"Join", 248},
{"Language", 1400},
{"LineNumberMargin", 407},
{"LoadSession", 132},
{"LwrCase", 241},
{"MacroList", 314},
{"MacroPlay", 313},
{"MacroRecord", 311},
{"MacroStopRecord", 312},
{"MacroSep", 310},
{"MatchBrace", 230},
{"MatchCase", 801},
{"MonoFont", 450},
{"MoveTabLeft", 509},
{"MoveTabRight", 508},
{"MruFile", 1000},
{"MruSep", 120},
{"MruSub", 121},
{"New", 101},
{"NextFile", 502},
{"NextFileStack", 507},
{"NextMatchPpc", 262},
{"NextMsg", 306},
{"OnTop", 960},
{"Open", 102},
{"OpenAbbrevProperties", 463},
{"OpenDirectoryProperties", 465},
{"OpenFilesHere", 413},
{"OpenGlobalProperties", 462},
{"OpenLocalProperties", 460},
{"OpenLuaExternalfile", 464},
{"OpenSelected", 103},
{"OpenUserProperties", 461},
{"Paste", 205},
{"PasteAndDown", 208},
{"PrevFile", 501},
{"PrevFileStack", 506},
{"PrevMatchPpc", 260},
{"PrevMsg", 307},
{"Print", 131},
{"PrintSetup", 130},
{"Quit", 140},
{"ReadOnly", 416},
{"Redo", 202},
{"Regexp", 802},
{"Replace", 216},
{"Revert", 104},
{"RunWin", 351},
{"Save", 106},
{"SaveACopy", 116},
{"SaveAll", 504},
{"SaveAs", 110},
{"SaveAsHtml", 111},
{"SaveAsPdf", 113},
{"SaveAsRtf", 112},
{"SaveAsTex", 115},
{"SaveAsXml", 117},
{"SaveSession", 133},
{"SelectAll", 207},
{"SelectionAddEach", 258},
{"SelectionAddNext", 257},
{"SelectionForFind", 217},
{"SelectToBrace", 231},
{"SelectToNextMatchPpc", 263},
{"SelectToPrevMatchPpc", 261},
{"SelMargin", 405},
{"ShowCalltip", 232},
{"Split", 249},
{"SplitVertical", 401},
{"SrcWin", 350},
{"StatusWin", 353},
{"StopExecute", 304},
{"StreamComment", 244},
{"SwitchPane", 421},
{"TabSize", 440},
{"TabWin", 354},
{"ToggleOutput", 409},
{"ToggleParameters", 412},
{"ToggleFoldAll", 236},
{"ToggleFoldRecursive", 237},
{"Tools", 1100},
{"ToolWin", 352},
{"Undo", 201},
{"Unslash", 804},
{"UprCase", 240},
{"ViewEol", 403},
{"ViewGuides", 404},
{"ViewSpace", 402},
{"ViewStatusBar", 411},
{"ViewTabBar", 410},
{"ViewToolbar", 408},
{"WholeWord", 800},
{"Wrap", 414},
{"WrapAround", 803},
{"WrapOutput", 415},'''


knownOverrideNames = [
	('IncSearch', 252, 'IncrementalSearch'),
	('UprCase', 240, 'UpperCase'),
	('LwrCase', 241, 'LowerCase'),
]

def getMap():
	map = {}
	for name in knownNames.replace('\r\n','\n').split('\n'):
		p1, p2 = name.split('", ')
		_, p1 = p1.split('{"')
		p2, _ = p2.split('},')
		number = int(p2)
		goodName = p1
		lowerName = p1.lower()
		map[number] = (lowerName, goodName)
	for tp in knownOverrideNames:
		number = tp[1]
		goodName = tp[2]
		lowerName = tp[0].lower()
		map[number] = (lowerName, goodName)
		
	return map
	


def go():
	map = getMap()
	results = []
	for line in open(pathToSciteH):
		line = line.strip()
		if line.startswith('#define IDM_'):
			_,origname,val = line.split()
			name = origname.replace('IDM_', '').lower().replace('_', '')
			ival = int(val)
			if ival not in map:
				results.append('{"'+name+'", NOTSEENBEFORE '+val+'},')
			else:
				lowerName, goodName = map[ival]
				if name != lowerName:
					results.append('{"'+name+'", NAMEWASCHANGED '+val+'},')
				else:
					results.append('{"'+goodName+'", '+origname+'},')
					
				
	results.sort()
	for line in results:
		print line
	

pathToSciteH = r'C:\b\pydev\dev\scite-with-python\scite-with-python-maybe\src\scite\scite\src\Scite.h'
go()