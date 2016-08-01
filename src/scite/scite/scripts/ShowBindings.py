
import os
import re

class PropSetFile(object):
	def __init__(self, platform, root):
		self.props = dict()
		self.platform = platform
		self.root = root
		self.condition = None
		self.filesSeen = dict()

	def GetString(self, key):
		return self.props.get(key, '')

	def GetInt(self, key, default=0):
		s = self.Expanded(self.GetString(key))
		return int(s) if s else default

	def _expandOnce(self, s):
		if s.startswith('$(') and s.endswith(')'):
			propname = s[2:-1]
			assert ' ' not in propname, "We don't yet support $(expand) etc."
			return self.GetString(propname)
		elif '$(' in s:
			assert False, "We don't yet support expressions containing $() " + s
		else:
			return s

	def Expanded(self, s):
		i = 0
		while '$(' in s and i < 200:
			s = self._expandOnce(s)
			i += 1
		return s

	def ReadFile(self, filename):
		assert os.path.abspath(filename) not in self.filesSeen, 'cannot import a file twice'
		self.filesSeen[os.path.abspath(filename)] = 1
		if os.path.isfile(filename):
			self.ReadString(readall(filename))

	def ReadString(self, contents):
		contents = contents.replace('\r\n', '\n').split('\n')
		s = ''
		for line in contents:
			s += line
			if line.endswith('\\'):
				s = s[0:-1]
			else:
				self._readLine(s)
				s = ''
		
		self._readLine(s)
	
	def _importStar(self):
		assert not self.Expanded(self.GetString('imports.include')), 'imports.include not supported'
		exclude = self.Expanded(self.GetString('imports.exclude')).split(' ')
		filesList = [os.path.splitext(name)[0] for name in os.listdir(self.root) if name.endswith('.properties')]
		for name in filesList:
			if name not in exclude:
				name = os.path.join(self.root, name + '.properties')
				if os.path.abspath(name) not in self.filesSeen:
					self.ReadFile(name)

	def _readLine(self, s):
		if s.startswith('#') or not s.strip():
			return
		elif s.startswith('module '):
			assert False, 'Sc1.properties not supported'
		elif s.startswith('import '):
			filename = s[len('import '):]
			if filename == '*':
				self._importStar()
			else:
				self.ReadFile(os.path.join(self.root, filename + '.properties'))
			return
		elif s.startswith('if PLAT_WIN'):
			self.condition = 'win32'
			return
		elif s.startswith('if PLAT_MAC'):
			self.condition = 'mac'
			return
		elif s.startswith('if PLAT_GTK'):
			self.condition = 'gtk'
			return
		elif s.startswith('if PLAT_UNIX'):
			self.condition = 'gtk' # ok because this script isn't supported for mac.
			return
		elif s.startswith('if '):
			raise RuntimeError("Unsupported conditional " + s)
			
		if self.condition:
			if s[0] == '\t':
				if self.platform != self.condition:
					return
				else:
					s = s[1:]
			else:
				self.condition = None
		
		if s[0] != '[': # we don't yet support sections
			parts = s.split('=', 1)
			if len(parts) == 0:
				warn('unrecognized line in properties: ' + s)
			else:
				self.props[parts[0]] = parts[1]

def getAllProperties(propertiesMain, propertiesUser, platform, rootDir=None):
	rootDir = rootDir or os.path.split(propertiesMain)[0]
	props = PropSetFile(platform, rootDir)
	if propertiesMain:
		props.ReadFile(propertiesMain)
	if propertiesUser:
		props.ReadFile(propertiesUser)
	return props

def readShortcutLanguageMenu(results, props, key):
	value = props.GetString(key)
	if value.strip():
		languageName, languageShort, keyPress, _ = value.split('|')
		keyPress = props.Expanded(keyPress)
		if keyPress.strip():
			command = 'set language ' + languageName.replace('&', '')
			results.append(KeyBinding('properties *language', command, keyPress, priority=40, platform='any'))

def readShortcutFromCommand(results, props, key):
	matchObj = re.match(r'^command\.name\.([0-9]+)\.([^=]+)', key)
	if matchObj:
		number = matchObj.group(1)
		filetypes = matchObj.group(2)
		name = props.Expanded(props.GetString(key))
		platform = props.Expanded(filetypes)
		platform = 'any' if platform == '*' else platform
		setShortcutKey = 'command.shortcut.' + number + '.' + filetypes
		setShortcutValue = props.GetString(setShortcutKey)
		if name and len(number) == 1 and not setShortcutValue:
			binding = KeyBinding('properties command (implicit)', name, priority=50, platform=platform)
			binding.keyChar = number
			binding.control = True
			results.append(binding)
		elif name and setShortcutValue:
			results.append(KeyBinding('properties command', name, setShortcutValue, priority=50, platform=platform))

def readPropertiesUserShortcuts(results, props, key):
	value = props.GetString(key)
	parts = value.split('|')
	for pair in takePairs(parts):
		if pair and len(pair) == 2:
			results.append(KeyBinding('properties user.shortcuts', pair[1], pair[0], priority=60, platform='any'))

def readFromProperties(bindings, props):
	for key in props.props:
		if key.startswith('*language.'):
			readShortcutLanguageMenu(bindings, props, key)
		elif key == 'user.shortcuts':
			readPropertiesUserShortcuts(bindings, props, key)
		elif key.startswith('command.name.'):
			readShortcutFromCommand(bindings, props, key)

def readUserDefinedKeys(props):
	mapMenuPathToNewAccel = dict()
	for key in props.props:
		if key.startswith('menukey.'):
			val = props.Expanded(props.GetString(key))
			if val:
				mapMenuPathToNewAccel[key[len('menukey.'):]] = val
	return mapMenuPathToNewAccel

def getMapFromIdmToMenuText():
	map = dict()
	with open(os.path.join("..", "win32", "SciTERes.rc"), "rt") as f:
		for l in f:
			l = l.strip()
			if l.startswith("MENUITEM") and "SEPARATOR" not in l:
				l = l.replace("MENUITEM", "").strip()
				text, symbol = l.split('",', 1)
				symbol = symbol.strip()
				text = text[1:].replace("&", "").replace("...", "")
				if "\\t" in text:
					text = text.split("\\t", 1)[0]
				map[symbol] = text
	return map

def writeOutputFile(bindings, outputFile):
	mapSciteToString = getMapFromIdmToMenuText()
	mapScintillaToString = getMapScintillaToString()
	with open(outputFile, 'w') as out:
		out.write(startFile.replace('%script%', __file__))
		out.write("<h2>Current key bindings</h2>\n")
		out.write("<table><tr><th> </th><th> </th><th> </th><th> </th></tr>\n")
		for binding in bindings:
			writeOutputBinding(out, binding, mapSciteToString, mapScintillaToString)
			
		out.write("</table>\n")
		out.write("</body>\n</html>\n")

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

def normalizeMenuPath(s, platform):
	s = s.replace('&' if platform == 'win32' else '_', '')		# menupath='menukey/File/Save As...'
	s = s.replace('.', '')		# menupath='menukey/File/Save As'
	s = s.replace('/', '.')		# menupath='menukey.File.Save As'
	s = s.replace(' ', '_')	# menupath='menukey.File.Save_As'
	return s.lower()	# menupath='menukey.file.save_as'

def readFromSciTEItemFactoryEntry(parts, bindings, mapUserDefinedKeys):
	path, accel, gcallback, command, itemType, whitespace = parts
	accel = accel.lstrip(' "').rstrip('"')
	if accel != 'NULL' and accel != '':
		path = path.strip('"').lstrip('"{/')
		name = path.split('/')[-1].replace('_', '')
		userDefined = mapUserDefinedKeys.get(normalizeMenuPath(path, 'gtk'), '')
		if userDefined == '""' or userDefined == 'none':
			return
		
		accel = userDefined or accel
		accel = accel.replace('>space', '>Space')
		bindings.append(KeyBinding('SciTEItemFactoryEntry', name, accel, priority=80, platform='gtk'))

def readFromSciTEResAccelTableEntry(parts, bindings):
	key, command, modifiers = [part.strip() for part in parts]
	if key.startswith('"'):
		key = key.replace('"', '')
	elif key.startswith('VK_'):
		key = key[len('VK_'):].replace('MULTIPLY', '*')
		key = key[0] + key[1:].lower()
	elif key == '187':
		return
	
	modparts = [m.strip() for m in modifiers.split(',') if m.strip() != 'VIRTKEY']
	modifiers = ('+'.join(modparts) + '+') if modparts else ''
	bindings.append(KeyBinding('SciTERes accel', command, modifiers + key, priority=80, platform='win32'))

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
		
	map=dict(SCI_CTRL=(True, False, False), SCI_ALT=(False, True, False), SCI_SHIFT=(False, False, True), 
		SCMOD_META=(True, False, False), SCI_CSHIFT=(True, False, True), SCI_ASHIFT=(False, True, True),
		SCI_SCTRL_META=(True, False, True), SCI_CTRL_META=(True, False, False), SCI_NORM=(False, False, False))
	binding = KeyBinding('Scintilla keymap', command, priority=0, platform='any')
	binding.control, binding.alt, binding.shift = map[modifiers]
	binding.keyChar = key
	bindings.append(binding)

def readFromSciTEItemFactoryList(bindings, mapUserDefinedKeys):
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
				readFromSciTEItemFactoryEntry(parts, bindings, mapUserDefinedKeys)

def readFromSciTEResAccelTable(bindings):
	start = '''ACCELS ACCELERATORS'''
	lines = retrieveCodeLines('../win32/SciTERes.rc', start, 'END')
	for line in lines:
		if line.startswith('\t'):
			line = line.strip()
			if line and 'IDM_TOOLS+' not in line and not line.startswith('//'):
				parts = line.split(',', 2)
				if len(parts) != 3:
					raise RuntimeError('accelerator item did not have 3 parts ' + line)
				else:
					readFromSciTEResAccelTableEntry(parts, bindings)

def readFromScintillaKeyMap(bindings):
	start = '''const KeyToCommand KeyMap::MapDefault[] = {'''
	lines = retrieveCodeLines('../../scintilla/src/KeyMap.cxx', start, '};')
	insideMac = False
	for line in lines:
		line = line.strip()
		if line == '#if OS_X_KEYS':
			insideMac = True
		elif line == '#endif' or line == '#else':
			insideMac = False
		elif line.startswith('#if '):
			raise RuntimeError('unknown preprocessor condition in keymap.cxx ' + line)
		elif not insideMac and line.startswith('{'):
			parts = line.split(',')
			if len(parts) != 4:
				raise RuntimeError('line started with { but did not have 4 parts ' + line)
			else:
				readFromScintillaKeyMapEntry(parts, bindings)

def main(propertiesMain, propertiesUser):
	assert not os.path.isfile('../src/PythonExtension.cxx'), 'Please run ShowBindingsDetectChanges.py instead.'
	for platform in ('gtk', 'win32'):
		props = getAllProperties(propertiesMain, propertiesUser, platform)
		platformCapitalized = platform[0].upper() + platform[1:]
		outputFile = 'CurrentBindings%s.html' % platformCapitalized
		bindings = []
		readFromScintillaKeyMap(bindings)
		addCallsToAssignKeyBindings(bindings, props)
		readFromProperties(bindings, props)
		mapUserDefinedKeys = readUserDefinedKeys(props)
		if platform == 'gtk':
			addBindingsManual(bindings, gtkKmapBindings)
			readFromSciTEItemFactoryList(bindings, mapUserDefinedKeys)
		else:
			readFromSciTEResAccelTable(bindings)
		
		bindings.sort(key=lambda obj: obj.getSortKey())
		writeOutputFile(bindings, outputFile)

class KeyBinding(object):
	def __init__(self, setName, command, shortcut=None, priority=0, platform='all'):
		self.control = False
		self.alt = False
		self.shift = False
		self.keyChar = None
		self.command = command
		self.priority = priority
		self.platform = platform
		self.setName = setName
		if shortcut:
			self.setKeyFromString(shortcut)
	
	def setKeyFromString(self, s):
		s = s.replace('<control>', 'Ctrl+').replace('<alt>', 'Alt+').replace('<shift>', 'Shift+')
		self.keyChar = s.split('+')[-1]
		modifiers = s.split('+')[0:-1]
		for item in modifiers:
			item = item.lower()
			if item == 'control':
				self.control = True
			elif item == 'ctrl':
				self.control = True
			elif item == 'alt':
				self.alt = True
			elif item == 'shift':
				self.shift = True
			else:
				raise ValueError('unrecognized modifier')
		
		if self.keyChar[0] != self.keyChar[0].upper():
			raise ValueError('key should be upper case ' + s)
			
	def getKeyString(self):
		s = 'Ctrl+' if self.control else ''
		s += 'Alt+' if self.alt else ''
		s += 'Shift+' if self.shift else ''
		return s + self.keyChar
		
	def getSortKey(self):
		return (self.keyChar, self.control, self.alt, self.shift, self.priority, self.command)
	
	def __repr__(self):
		return '|'.join((self.getKeyString(), self.command, str(self.priority), self.platform, self.setName))

def addBindingsManual(bindings, s):
	lines = s.replace('\r\n', '\n').split('\n')
	for line in lines:
		if line.strip():
			keys, command, priority, platform, setName = line.split('|')
			bindings.append(KeyBinding(setName, command, keys, priority=int(priority), platform=platform))

def retrieveCodeLines(filename, startingLine, endingLine, mustInclude=None):
	allLines = readall(filename, 'rb').replace('\r\n', '\n').split('\n')
	
	# confirm that the first line is in the file exactly once
	linesThatMatchStart = [i for i, line in enumerate(allLines) if line == startingLine]
	if len(linesThatMatchStart) != 1:
		raise RuntimeError(
			'\n%s\n seen %d times in \n%s\n, rather than once.' % (startingLine, len(linesThatMatchStart), filename))
	
	lineNumber = linesThatMatchStart[0]
	seenMustInclude = False
	endLine = None
	while lineNumber < len(allLines):
		lineNumber += 1
		if allLines[lineNumber] == endingLine and (seenMustInclude or not mustInclude):
			endLine = lineNumber
			break
		elif allLines[lineNumber] == mustInclude:
			seenMustInclude = True

	if endLine is None:
		raise RuntimeError('Failure: ending line %s not found in file %s' % (endingLine, filename))

	return allLines[linesThatMatchStart[0]:endLine + 1]

def takePairs(iterable):
	import itertools
	it = iter(iterable)
	item = list(itertools.islice(it, 2))
	while item:
		yield item
		item = list(itertools.islice(it, 2))

def warn(prompt):
	print(prompt)
	while True:
		s = getInput('Continue? y/n')
		if s == 'y':
			break
		elif s == 'n':
			raise RuntimeError('chose not to continue')

def getInput(prompt):
	import sys
	if sys.version_info[0] <= 2:
		return raw_input(prompt)
	else:
		return input(prompt)

def readall(filename, mode='rb'):
	with open(filename, mode) as f:
		return f.read()

def escapeXml(s):
	s = s.replace('&', '&amp;')
	s = s.replace('<', '&lt;').replace('>', '&gt;')
	return s.replace('"', '&quot;').replace("'", '&apos;')

def assertEq(expected, received):
	if expected != received:
		raise AssertionError('expected %s but got %s' % (expected, received))

def assertEqArray(expected, received):
	assertEq(len(expected), len(received))
	for i in range(len(expected)):
		assertEq(repr(expected[i]), repr(received[i]))

def addCallsToAssignKeyBindings(bindings, props):
	# from SciTEBase::ReadProperties
	s = '''Control+Shift+L|SCI_LINEDELETE|1|any|SciTEProps.cxx AssignKey\n'''
	if props.GetInt("os.x.home.end.keys"):
		s += '''Home|SCI_SCROLLTOSTART|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_NULL|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_NULL|1|any|SciTEProps.cxx AssignKey
End|SCI_SCROLLTOEND|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_NULL|1|any|SciTEProps.cxx AssignKey'''
	else:
		if props.GetInt("wrap.aware.home.end.keys", 0):
			if props.GetInt("vc.home.key", 1):
				s += '''Home|SCI_VCHOMEWRAP|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_VCHOMEWRAPEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_VCHOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEENDWRAP|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDWRAPEXTEND|1|any|SciTEProps.cxx AssignKey'''
			else:
				s += '''Home|SCI_HOMEWRAP|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_HOMEWRAPEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_HOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEENDWRAP|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDWRAPEXTEND|1|any|SciTEProps.cxx AssignKey'''
		else:
			if props.GetInt("vc.home.key", 1):
				s += '''Home|SCI_VCHOME|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_VCHOMEEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_VCHOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEEND|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDEXTEND|1|any|SciTEProps.cxx AssignKey'''
			else:
				s += '''Home|SCI_HOME|1|any|SciTEProps.cxx AssignKey
Shift+Home|SCI_HOMEEXTEND|1|any|SciTEProps.cxx AssignKey
Shift+Alt+Home|SCI_HOMERECTEXTEND|1|any|SciTEProps.cxx AssignKey
End|SCI_LINEEND|1|any|SciTEProps.cxx AssignKey
Shift+End|SCI_LINEENDEXTEND|1|any|SciTEProps.cxx AssignKey'''
	addBindingsManual(bindings, s)

# from KeyToCommand kmap[] in SciTEGTK.cxx
gtkKmapBindings = r'''Control+Tab|IDM_NEXTFILESTACK|30|gtk|KeyToCommand kmap[]
Shift+Control+Tab|IDM_PREVFILESTACK|30|gtk|KeyToCommand kmap[]
Control+Enter|IDM_COMPLETEWORD|30|gtk|KeyToCommand kmap[]
Alt+F2|IDM_BOOKMARK_NEXT_SELECT|30|gtk|KeyToCommand kmap[]
Alt+Shift+F2|IDM_BOOKMARK_PREV_SELECT|30|gtk|KeyToCommand kmap[]
Control+F3|IDM_FINDNEXTSEL|30|gtk|KeyToCommand kmap[]
Control+Shift+F3|IDM_FINDNEXTBACKSEL|30|gtk|KeyToCommand kmap[]
Control+F4|IDM_CLOSE|30|gtk|KeyToCommand kmap[]
Control+J|IDM_PREVMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+Shift+J|IDM_SELECTTOPREVMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+K|IDM_NEXTMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+Shift+K|IDM_SELECTTONEXTMATCHPPC|30|gtk|KeyToCommand kmap[]
Control+*|IDM_EXPAND|30|gtk|KeyToCommand kmap[]'''

startFile = """<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<!--Generated by scite/scripts/%script% -->
<style type="text/css">
body { font-family:verdana, Geneva, sans-serif; font-size: 80% }
table { border: 1px solid #1F1F1F; border-collapse: collapse; }
td { border: 1px solid; border-color: #E0E0E0 #000000; padding: 1px 5px 1px 5px; }
th { border: 1px solid #1F1F1F; padding: 1px 5px 1px 5px; }
thead { background-color: #000000; color: #FFFFFF; }
</style>
<body>
"""

def tests():
	propstring = r'''
a=b=c
test.expand=$(span)
if PLAT_GTK
	plat=gtk
if PLAT_WIN
	plat=win
span=a\
b\
c
testfileendswithslash=test''' + '\\'
	props = PropSetFile('gtk', '.')
	props.ReadString(propstring)
	assertEq('b=c', props.GetString('a'))
	assertEq('abc', props.GetString('span'))
	assertEq('abc', props.Expanded(props.GetString('test.expand')))
	assertEq('gtk', props.GetString('plat'))
	assertEq('test', props.GetString('testfileendswithslash'))
	
if __name__ == '__main__':
	tests()
	
	
	propertiesMain = '../bin/SciTEGlobal.properties'
	propertiesUser = None
	main(propertiesMain, propertiesUser)

