
# display current keyboard bindings, including from user properties, SciTE, and Scintilla.

from ShowBindingsDetectChanges import *
from ShowBindingsReadProps import *

def getGtkBindings(props):
	results = []
	detectCodeChanges('../gtk/SciTEGTK.cxx', gtkKeyHandlerMethodExpectedText,
		gtkKeyHandlerMethodExpectedTextMustInclude)
	
	# --- gint SciTEGTK::Key(GdkEventKey *event) {
	# --- send to extension 			extender->OnKey (priority=20)
	# --- check the "kmap" list 	commandID = kmap[i].msg (priority=30)
	addBindingsManual(results, gtkKmapBindings)
	
	# --- check the language menu	commandID = IDM_LANGUAGE + j (priority=40)
	# --- check the tools menu			MenuCommand(IDM_TOOLS + tool_i) (priority=50)
	# --- check user.shortcuts			shortCutItemList[cut_i].menuCommand (priority=60)
	results.extend(readFromProperties(props))
	
	# --- check UI strips			findStrip.KeyDown(event), replaceStrip, userStrip (priority=70)
	# --- FindStrip: Alt-initial letter
	# --- ReplaceStrip: Alt-initial letter
	# --- UserStrip: Escape to close, Alt-initial letter of label to hit a button or set focus
	detectCodeChanges('../gtk/SciTEGTK.cxx', gtkFindStripEscapeSignal)
	detectCodeChanges('../gtk/SciTEGTK.cxx', gtkReplaceStripEscapeSignal)
	detectCodeChanges('../gtk/SciTEGTK.cxx', gtkUserStripEscapeSignal)
	detectCodeChanges('../gtk/SciTEGTK.cxx', gtkFindIncrementEscapeSignal)
	detectCodeChanges('../gtk/Widget.cxx', gtkWidgetCxxStripKeyDown)
	
	# --- check menu items		SciTEItemFactoryEntry menuItems (priority=80)
	readFromSciTEItemFactoryList(results)
	
	return results

def getWindowsBindings(props):
	results = []
	detectCodeChanges('../win32/SciTEWin.cxx', win32KeyHandlerMethodExpectedText)
	
	# --- LRESULT SciTEWin::KeyDown(WPARAM wParam) {
	# --- send to extension 			extender->OnKey (priority=20)
	# --- check the language menu	commandID = IDM_LANGUAGE + j (priority=40)
	# --- check the tools menu			MenuCommand(IDM_TOOLS + tool_i) (priority=50)
	# --- check user.shortcuts			shortCutItemList[cut_i].menuCommand (priority=60)
	results.extend(readFromProperties(props))
	
	# --- check UI strips
	# --- FindStrip::KeyDown
	# --- ReplaceStrip::KeyDown
	# --- UserStrip: Escape to close, Alt-initial letter of label to hit a button or set focus
	detectCodeChanges('../win32/SciTEWinDlg.cxx', win32ModelessHandler)
	detectCodeChanges('../win32/Strips.cxx', win32StripKeyDown)
	
	# --- accelerator table			SciTERes.rc accelerator (priority=80)
	# --- the menu items are just decorative, the accelerator table provides the shortcut.
	readFromSciTEResAccelTable(results)
	
	return results

def getScintillaBindings(props):
	results = []
	detectCodeChanges('../../scintilla/src/Editor.cxx', scintillaKeyHandlerMethodExpectedText,
		scintillaKeyHandlerMethodExpectedTextMustInclude)
	detectCodeChanges('../src/SciTEProps.cxx', callsToAssignKey)
	detectCodeChanges('../src/SciTEBase.cxx', sciteBaseCallAssignKey)
	addCallsToAssignKeyBindings(props, results)
	readFromScintillaKeyMap(results)
	return results

def writeOutputFile(bindings, outputFile):
	import PythonExtensionGenReference
	mapSciteToString = PythonExtensionGenReference.getMapFromIdmToMenuText()
	mapScintillaToString = getMapScintillaToString()
	setsSeen = dict()
	with open(outputFile, 'w') as out:
		out.write(PythonExtensionGenReference.startFile.replace('%script%', __file__))
		out.write("<h2>Current key bindings</h2>\n")
		out.write("<table><tr><th> </th><th> </th><th> </th><th> </th></tr>\n")
		for binding in bindings:
			writeOutputBinding(out, binding, mapSciteToString, mapScintillaToString)
			setsSeen[binding.setName] = 1
			
		out.write("</table>\n")
		out.write("</body>\n</html>\n")
	return setsSeen

def renderCommand(command, mapSciteToString, mapScintillaToString):
	if command.startswith('IDM_BUFFER+'):
		num = command[len('IDM_BUFFER+'):]
		command = 'buffer' + num
	elif command in mapSciteToString:
		command = mapSciteToString[command]
	elif command in mapScintillaToString:
		command = mapScintillaToString[command]
		command = command.replace('V C ', 'Visual Studio-style ')
	elif command.startswith('IDM_'):
		command = command.replace('IDM_', '').lower().replace('_', ' ')
		command = command.replace('matchppc', ' match ppc')
		
	command = command[0].upper() + command[1:].lower()
	command = command.replace('...', '')
	command = command.replace('Buffer', 'Buffer ')
	return command

def writeOutputBinding(out, binding, mapSciteToString, mapScintillaToString):
	out.write('<tr><td>%s</td>' % escapeXml(binding.keyChar))
	out.write('<td>%s</td>' % escapeXml(binding.getKeyString()))
	out.write('<td>%s</td>' % escapeXml(
		renderCommand(binding.command, mapSciteToString, mapScintillaToString)))
	notes = ''
	if '*' in binding.platform:
		notes += 'only %s' % binding.platform
	elif 'properties' in binding.setName:
		notes += 'props'
	
	out.write('<td>%s</td></tr>\n' % escapeXml(notes))

def getMapScintillaToString():
	import re
	mapScintillaToString = dict()
	mapNumberToSciConstant = dict()
	with open('../../scintilla/include/Scintilla.h', 'r') as f:
		for line in f:
			if line.startswith('#define SCI_'):
				poundDefine, constantName, number = line.split()
				mapNumberToSciConstant[number] = constantName
	
	r = re.compile(r'(get|set|fun) ([^=]+)=([0-9]+)\(')
	rSpaceBeforeCapital = re.compile(r'([A-Z])')
	with open('../../scintilla/include/Scintilla.iface', 'r') as f:
		for line in f:
			matchObj = r.match(line)
			if matchObj:
				number = matchObj.group(3)
				sciConst = mapNumberToSciConstant.get(number, None)
				if sciConst is not None:
					name = matchObj.group(2).split(' ')[-1]
					name = rSpaceBeforeCapital.sub(r' \1', name)
					mapScintillaToString[sciConst] = name.lstrip(' ')
	
	return mapScintillaToString

def readFromSciTEItemFactoryEntry(parts, bindings):
	path, shortcut, gcallback, command, itemType, whitespace = parts
	shortcut = shortcut.lstrip(' "').rstrip('"')
	if shortcut != 'NULL' and shortcut != '':
		name = path.split('/')[-1].replace('_', '').rstrip('"')
		command = command.lstrip(' "').rstrip('"')
		if command.startswith('bufferCmdID + '):
			command = command.replace('bufferCmdID + ', 'open buffer ')
		elif not command.startswith('IDM_'):
			warn('unknown command ' + command)
	
		shortcut = shortcut.replace('>', '+').replace('<', '')
		shortcut = shortcut.replace('+space', '+Space')
		binding = KeyBinding('SciTEItemFactoryEntry', name, priority=80, platform='gtk')
		binding.setKeyFromString(shortcut)
		bindings.append(binding)

def readFromSciTEResAccelTableEntry(parts, bindings):
	key, command, modifiers = [part.strip() for part in parts]
	if key.startswith('"'):
		key = key.replace('"', '')
	elif key.startswith('VK_'):
		key = key[len('VK_'):].replace('MULTIPLY', '*')
		key = key[0] + key[1:].lower()
	elif key == '187':
		return
	
	binding = KeyBinding('SciTERes accel', command, priority=80, platform='win32')
	binding.keyChar = key
	modparts = [m.strip() for m in modifiers.split(',')]
	for modpart in modparts:
		if modpart == 'CONTROL':
			binding.control = True
		elif modpart == 'ALT':
			binding.alt = True
		elif modpart == 'SHIFT':
			binding.shift = True
		elif modpart != 'VIRTKEY':
			raise RuntimeError('unknown modifier ' + modifiers)
	
	bindings.append(binding)

def readFromScintillaKeyMapEntry(parts, bindings):
	key, modifiers, command, whitespace = [part.strip() for part in parts]
	command = command.rstrip('} ')
	key = key.lstrip('{ ')
	if key == '0':
		return
	elif key.startswith("'"):
		key = key.replace("'", '')
		key = key.replace('\\\\', '\\')
	elif key.startswith('SCK_'):
		key = key[len('SCK_'):]
		key = key[0] + key[1:].lower()
		
	binding = KeyBinding('Scintilla keymap', command, priority=0, platform='any')
	binding.keyChar = key
	if modifiers == 'SCI_SHIFT':
		binding.shift = True
	elif modifiers == 'SCI_CTRL':
		binding.control = True
	elif modifiers == 'SCI_ALT':
		binding.alt = True
	elif modifiers == 'SCMOD_META':
		binding.control = True
	elif modifiers == 'SCI_CSHIFT':
		binding.control, binding.shift = True, True
	elif modifiers == 'SCI_ASHIFT':
		binding.alt, binding.shift = True, True
	elif modifiers == 'SCI_SCTRL_META':
		binding.control, binding.shift = True, True
	elif modifiers == 'SCI_CTRL_META':
		binding.control = True
	elif modifiers != 'SCI_NORM':
		raise RuntimeError('unknown modifier ' + modifiers)
			
	bindings.append(binding)

def readFromSciTEResMenuEntry(parts):
	nameAndShortcut, command = parts
	if '\\t' in nameAndShortcut:
		nameAndShortcut = nameAndShortcut.lstrip('"').rstrip('\t", ')
		name, shortcutShownToUI = nameAndShortcut.split('\\t')
		name = name.replace('&', '')
		# shortcutShownToUI is just shown in the UI,
		# it doesn't have real effect -- see accelerator table.

def readFromSciTEItemFactoryList(bindings):
	start = '''void SciTEGTK::CreateMenu() {'''
	end = '''	gtk_window_add_accel_group(GTK_WINDOW(PWidget(wSciTE)), accelGroup);'''
	lines = retrieveCodeLines('../gtk/SciTEGTK.cxx', start, end)
	for line in lines:
		line = line.strip()
		if line.startswith('{'):
			parts = line.split(',')
			if len(parts) != 6:
				raise RuntimeError('line started with { but did not have 6 parts ' + line)
			else:
				readFromSciTEItemFactoryEntry(parts, bindings)

def readFromSciTEResAccelTable(bindings):
	start = '''ACCELS ACCELERATORS'''
	lines = retrieveCodeLines('../win32/SciTERes.rc', start, 'END')
	for line in lines:
		if line.startswith('\t'):
			line = line.strip()
			if 'IDM_TOOLS+' not in line and not line.startswith('//'):
				parts = line.split(',', 2)
				if len(parts) != 3:
					raise RuntimeError('accelerator item did not have 3 parts ' + line)
				else:
					readFromSciTEResAccelTableEntry(parts, bindings)

def readFromSciTEResMenus():
	start = '''SciTE MENU'''
	mustContain = '''	MENUITEM "&About SciTE",			IDM_ABOUT'''
	lines = retrieveCodeLines('../win32/SciTERes.rc', start, 'END', mustContain)
	for line in lines:
		line = line.strip()
		if line.startswith('MENUITEM ') and not line.startswith('MENUITEM SEPARATOR'):
			line = line[len('MENUITEM '):]
			parts = line.split(',')
			if len(parts) != 2:
				raise RuntimeError('line started with MENUITEM but did not have 2 parts ' + line)
			else:
				readFromSciTEResMenuEntry(parts)

def readFromScintillaKeyMap(bindings):
	start = '''const KeyToCommand KeyMap::MapDefault[] = {'''
	lines = retrieveCodeLines('../../scintilla/src/KeyMap.cxx', start, '};')
	insideMac = False
	for line in lines:
		line = line.strip()
		if line == '#if OS_X_KEYS':
			insideMac = True
		elif line == '#endif':
			insideMac = False
		elif line.startswith('#if '):
			raise RuntimeError('unknown preprocessor condition in keymap.cxx ' + line)
		elif not insideMac and line.startswith('{'):
			parts = line.split(',')
			if len(parts) != 4:
				raise RuntimeError('line started with { but did not have 4 parts ' + line)
			else:
				readFromScintillaKeyMapEntry(parts, bindings)

def main():
	checkForAnyLogicChanges()
	for platform in ('gtk', 'win32'):
		props = getAllProperties('../bin', platform)
		platformCapitalized = platform[0].upper() + platform[1:]
		outputFile = '../bin/doc/CurrentBindings%s.html' % platformCapitalized
		bindings = []
		bindings.extend(getScintillaBindings(props))
		expectedSets = ['SciTEProps.cxx AssignKey', 'properties *language', 'properties user.shortcuts',
			'properties command (implicit)', 'properties command', 'Scintilla keymap']
		if platform == 'gtk':
			bindings.extend(getGtkBindings(props))
			expectedSets.extend(['KeyToCommand kmap[]', 'SciTEItemFactoryEntry'])
		else:
			bindings.extend(getWindowsBindings(props))
			expectedSets.extend(['SciTERes accel'])
		
		bindings.sort(key=lambda obj: obj.getSortKey())
		setsSeen = writeOutputFile(bindings, outputFile)
		if set(expectedSets) != set(key for key in setsSeen):
			warn('''Warning: nothing found in %s, or saw unexpected %s''' %
				(set(expectedSets) - set(key for key in setsSeen),
				set(key for key in setsSeen) - set(expectedSets)))

def tests():
	entriesRead = []
	line = '''{"/Edit/Make Selection _Lowercase", "<control>U", menuSig, IDM_LWRCASE, 0},'''
	readFromSciTEItemFactoryEntry(line.split(','), entriesRead)
	line = '''{"/View/_Parameters", NULL, menuSig, IDM_TOGGLEPARAMETERS, "<CheckItem>"},'''
	readFromSciTEItemFactoryEntry(line.split(','), entriesRead)
	line = '''{"/Edit/S_how Calltip", "<control><shift>space", menuSig, IDM_SHOWCALLTIP, 0},'''
	readFromSciTEItemFactoryEntry(line.split(','), entriesRead)
	line = '''	"N", IDM_NEW,   VIRTKEY, CONTROL'''
	readFromSciTEResAccelTableEntry(line.split(',', 2), entriesRead)
	line = '''	VK_F8, IDM_TOGGLEOUTPUT, VIRTKEY'''
	readFromSciTEResAccelTableEntry(line.split(',', 2), entriesRead)
	line = r'''    VK_SPACE, IDM_SHOWCALLTIP, VIRTKEY, CONTROL, SHIFT'''
	readFromSciTEResAccelTableEntry(line.split(',', 2), entriesRead)
	line = r'''{'[',			SCI_CSHIFT,	SCI_PARAUPEXTEND},'''
	readFromScintillaKeyMapEntry(line.split(','), entriesRead)
	line = r'''{SCK_UP,			SCI_CTRL_META,	SCI_LINESCROLLUP},'''
	readFromScintillaKeyMapEntry(line.split(','), entriesRead)
	line = r'''{SCK_LEFT,		SCI_NORM,	SCI_CHARLEFT},'''
	readFromScintillaKeyMapEntry(line.split(','), entriesRead)
	expected = '''Ctrl+U|Make Selection Lowercase|80|gtk|SciTEItemFactoryEntry
Ctrl+Shift+Space|Show Calltip|80|gtk|SciTEItemFactoryEntry
Ctrl+N|IDM_NEW|80|win32|SciTERes accel
F8|IDM_TOGGLEOUTPUT|80|win32|SciTERes accel
Ctrl+Shift+Space|IDM_SHOWCALLTIP|80|win32|SciTERes accel
Ctrl+Shift+[|SCI_PARAUPEXTEND|0|any|Scintilla keymap
Ctrl+Up|SCI_LINESCROLLUP|0|any|Scintilla keymap
Left|SCI_CHARLEFT|0|any|Scintilla keymap'''
	expectedArr = []
	addBindingsManual(expectedArr, expected)
	assertEqArray(expectedArr, entriesRead)


if __name__ == '__main__':
	tests()
	main()
