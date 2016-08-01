
import os
import re

class PropSetFile(object):
	def __init__(self, platform):
		self.props = dict()
		self.condition = None
		self.platform = platform

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

	def _readLine(self, s):
		if s.startswith('#') or not s.strip():
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
		
		# we don't yet support sections or import
		if s[0] != '[' and not s.startswith('import '):
			key, val = s.split('=', 1)
			self.Set(key, val)

def getAllProperties(dir, platform, fnCheckPath=None):
	props = PropSetFile(platform)
	for (path, dirs, files) in os.walk(dir):
		if not fnCheckPath or fnCheckPath(path):
			for file in files:
				if file.endswith('.properties'):
					full = os.path.join(path, file)
					props.ReadOneFile(full)
	return props

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

def readShortcutLanguageMenu(results, props, key):
	value = props.GetString(key)
	if value.strip():
		languageName, languageShort, keyPress, _ = value.split('|')
		keyPress = props.Expanded(keyPress)
		if keyPress.strip():
			command = 'set language ' + languageName.replace('&', '')
			binding = KeyBinding('properties *language', command, priority=40, platform='any')
			binding.setKeyFromString(keyPress)
			results.append(binding)

def addBindingFromCommand(results, props, key, keyCommandName, platform):
	command = props.GetString(keyCommandName)
	if command:
		shortcut = props.GetString(key)
		if shortcut.strip():
			binding = KeyBinding('properties command', command, priority=50, platform=platform)
			binding.setKeyFromString(shortcut)
			results.append(binding)

def readImplicitShortcutFromCommand(results, props, key):
	matchObj = re.match(r'^command\.name\.([0-9])\.([^=]+)', key)
	if matchObj:
		number = matchObj.group(1)
		filetypes = matchObj.group(2)
		name = props.Expanded(props.GetString(key))
		setShortcutKey = 'command.shortcut.' + number + '.' + filetypes
		if name and not props.GetString(setShortcutKey):
			platform = props.Expanded(filetypes)
			platform = 'any' if platform in ('*', '*.*') else platform
			binding = KeyBinding('properties command (implicit)', name, priority=50, platform=platform)
			binding.keyChar = number
			binding.control = True
			results.append(binding)

def readCommandShortcut(results, props, key):
	cmd, shtcut, number, filetypes = key.split('.', 3)
	platform = props.Expanded(filetypes)
	platform = 'any' if platform in ('*', '*.*') else platform
	keyCommandName = 'command.name.' + number + '.' + filetypes
	addBindingFromCommand(results, props, key, keyCommandName, platform=platform)

def readCustomCommandShortcut(results, props, key):
	keyParts = key.split('.')
	keyCommandName = '.'.join(keyParts[0:-1]) + '.name'
	addBindingFromCommand(results, props, key, keyCommandName, platform='any')

def readPropertiesUserShortcuts(results, props, key):
	value = props.GetString(key)
	parts = value.split('|')
	for pair in takePairs(parts):
		if pair and len(pair) == 2:
			shortcut, command = pair
			binding = KeyBinding('properties user.shortcuts', command, priority=60, platform='any')
			binding.setKeyFromString(shortcut)
			results.append(binding)

def readFromProperties(props):
	results = []
	for key in props.props:
		if key.startswith('*language.'):
			readShortcutLanguageMenu(results, props, key)
		elif key == 'user.shortcuts':
			readPropertiesUserShortcuts(results, props, key)
		elif key.startswith('command.shortcut.'):
			readCommandShortcut(results, props, key)
		elif key.startswith('command.name.'):
			readImplicitShortcutFromCommand(results, props, key)
		elif key.startswith('customcommand.') and key.endswith('.shortcut'):
			readCustomCommandShortcut(results, props, key)
	return results

class KeyBinding(object):
	def __init__(self, setName, command, priority, platform):
		self.control = False
		self.alt = False
		self.shift = False
		self.keyChar = None
		self.command = command
		self.priority = priority
		self.platform = platform
		self.setName = setName
	
	def setKeyFromString(self, s):
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
			raise ValueError('key should be upper case')
			
	def getKeyString(self):
		s = ''
		if self.control:
			s += 'Ctrl+'
		if self.alt:
			s += 'Alt+'
		if self.shift:
			s += 'Shift+'
		s += self.keyChar
		return s
		
	def getSortKey(self):
		return (self.keyChar, self.control, self.alt, self.shift, self.priority, self.command)
	
	def __repr__(self):
		return '|'.join((self.getKeyString(), self.command, str(self.priority), self.platform, self.setName))

def addBindingsManual(bindings, s):
	lines = s.replace('\r\n', '\n').split('\n')
	for line in lines:
		if line.strip():
			try:
				modifiersAndKey, command, priority, platform, setName = line.split('|')
				binding = KeyBinding(setName, command, priority=int(priority), platform=platform)
				binding.setKeyFromString(modifiersAndKey)
				bindings.append(binding)
			except ValueError:
				print(line)
				raise

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

def readall(filename, mode='r'):
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

def tests():
	mockProperties = '''
customcommand.test.name=Test Custom
customcommand.test.shortcut=Shift+F12

#customcommand.commented.name=Test cmtd
#customcommand.commented.shortcut=F1

user.shortcuts=\
Ctrl+Shift+V|IDM_PASTEANDDOWN|\
Ctrl+PageDown|IDM_NEXTFILE|

if PLAT_GTK
	*language.sql=S&QL|sql||
	*language.html=H&TML|html|Control+Alt+Shift+F11|
	*language.php=P&HP|php|$(keyMissing)|
	*language.xml=&XML|xml|$(keyXML)|
	keyXML=Alt+Shift+/
if PLAT_WIN
	user.shortcuts=
	*language.xml=&XML|xml|Ctrl+O|

fff=*
command.name.11.$(fff)=Test Aaa
command.11.$(fff)=dostuff(x,y,z)
command.shortcut.11.$(fff)=Ctrl+Aaa

command.name.12.*=Test Bbb
command.12.*=dostuff(x,y,z)
command.shortcut.12.*=Ctrl+Bbb

command.name.4.$(fff)=Test Ddd

command.name.5.*.y=Test Ccc
command.shortcut.5.*.y=Shift+Tab'''

	props = PropSetFile('gtk')
	props.ReadString(mockProperties)
	results = readFromProperties(props)
	results.sort(key=lambda obj: obj.getSortKey())

	expected = '''Alt+Shift+/|set language XML|40|any|properties *language
Ctrl+4|Test Ddd|50|any|properties command (implicit)
Ctrl+Aaa|Test Aaa|50|any|properties command
Ctrl+Bbb|Test Bbb|50|any|properties command
Ctrl+Alt+Shift+F11|set language HTML|40|any|properties *language
Shift+F12|Test Custom|50|any|properties command
Ctrl+PageDown|IDM_NEXTFILE|60|any|properties user.shortcuts
Shift+Tab|Test Ccc|50|*.y|properties command
Ctrl+Shift+V|IDM_PASTEANDDOWN|60|any|properties user.shortcuts'''
	expectedArr = []
	addBindingsManual(expectedArr, expected)
	assertEqArray(expectedArr, results)
	
	
if __name__ == '__main__':
	tests()
