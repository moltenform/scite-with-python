
import os
import re

class PropSetFile(object):
	props = None
	def __init__(self):
		self.props = dict()

	def Set(self, key, val):
		self.props[key] = val

	def GetString(self, key):
		return self.props.get(key, '')

	def GetInt(self, key, default=0):
		s = self.Expanded(self.GetString(key))
		return int(s) if s else default

	def ReadOneFile(self, filename):
		self.ReadString(readall(filename, 'rb'))

	def Evaluate(self, key):
		if ' ' in key:
			raise RuntimeError("We don't yet support functions like $(expand )")
		else:
			return self.GetString(key)

	def _expandOnce(self, s):
		if s.startswith('$(') and s.endswith(')'):
			propname = s[2:-1]
			return self.Evaluate(propname)
		elif '$(' in s:
			raise RuntimeError("We don't yet support expressions containing $()", s)
		else:
			return s

	def Expanded(self, s):
		maxIters = 100
		i = 0
		while '$(' in s and i < maxIters:
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
				self._ReadLine(s)
				s = ''
		
		self._ReadLine(s)
			
	def _ReadLine(self, s):
		if s.startswith('#') or not s.strip():
			return
			
		# we don't yet support if/then
		if s.startswith('if '):
			return
		
		# we don't yet support if/then
		if s[0] == '\t':
			s = s[1:]
		
		# we don't yet support sections
		if s[0] == '[':
			return
		
		# we don't yet run import
		if s.startswith('import '):
			return
		
		try:
			key, val = s.split('=', 1)
			self.Set(key, val)
		except:
			print('Encountered exception for line "%s"' % s)
			raise
			
def getAllProperties(dir):
	props = PropSetFile()
	for (path, dirs, files) in os.walk(dir):
		if not path.endswith(os.sep + 'disabled') and not 'tools_example' in path:
			for file in files:
				if file.endswith('.properties'):
					full = os.path.join(path, file)
					props.ReadOneFile(full)
	return props

def takeBatch(iterable, size):
    import itertools
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))

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
			binding = KeyBinding()
			binding.setKeyFromString(keyPress)
			binding.command = 'set language ' + languageName.replace('&', '')
			binding.priority = 40
			binding.platform = 'unknown'
			binding.setName = 'properties *language'
			results.append(binding)

def readCommandShortcutGeneral(results, props, key, keyCommandName, platform):
	commandName = props.GetString(keyCommandName)
	if commandName:
		shortcut = props.GetString(key)
		if shortcut.strip():
			binding = KeyBinding()
			binding.setKeyFromString(shortcut)
			binding.command = commandName
			binding.priority = 50
			binding.platform = platform
			binding.setName = 'properties command'
			results.append(binding)

def readCommandShortcut(results, props, key):
	cmd, shtcut, number, filetypes = key.split('.', 3)
	platform = props.Expanded(filetypes)
	platform = 'any' if platform in ('*', '*.*') else platform
	keyCommandName = 'command.name.' + number + '.' + filetypes
	readCommandShortcutGeneral(results, props, key, keyCommandName, platform=platform)

def readImplicitShortcutFromCommand(results, props, key):
	matchObj = re.match(r'^command\.name\.([0-9])\.([^=]+)', key)
	if matchObj:
		number = matchObj.group(1)
		filetypes = matchObj.group(2)
		name = props.Expanded(props.GetString(key))
		setShortcutKey = 'command.shortcut.' + number + '.' + filetypes
		if name and not props.GetString(setShortcutKey):
			binding = KeyBinding()
			binding.keyChar = number
			binding.control = True
			binding.command = name
			binding.priority = 50
			binding.platform = props.Expanded(filetypes)
			binding.platform = 'any' if binding.platform in ('*', '*.*') else binding.platform
			binding.setName = 'properties command (implicit)'
			results.append(binding)

def readCustomCommandShortcut(results, props, key):
	keyParts = key.split('.')
	keyCommandName = '.'.join(keyParts[0:-1]) + '.name'
	readCommandShortcutGeneral(results, props, key, keyCommandName, platform='any')

def readPropertiesUserShortcuts(results, props, key):
	value = props.GetString(key)
	parts = value.split('|')
	for pair in takeBatch(parts, 2):
		if pair and len(pair) == 2:
			shortcut, command = pair
			binding = KeyBinding()
			binding.setKeyFromString(shortcut)
			binding.command = command
			binding.priority = 60
			binding.platform = 'unknown'
			binding.setName = 'properties user.shortcuts'
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
	shift = False
	control = False
	alt = False
	keyChar = None
	command = None
	priority = 0
	platform = 'all'
	setName = None
	
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
		return (self.keyChar, self.shift, self.control, self.alt, self.priority, self.command)
	
	def __repr__(self):
		return '|'.join((self.getKeyString(), self.command, str(self.priority), self.platform, self.setName))

def addBindingsManual(bindings, s):
	lines = s.replace('\r\n', '\n').split('\n')
	for line in lines:
		if line.strip():
			try:
				binding = KeyBinding()
				modifiersAndKey, binding.command, binding.priority, binding.platform, binding.setName = line.split('|')
				binding.setKeyFromString(modifiersAndKey)
				binding.priority = int(binding.priority)
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
	
	return allLines[linesThatMatchStart[0]:endLine+1]
		

def readall(filename, mode='r'):
	with open(filename, mode) as f:
		return f.read()

def escapeXml(s):
	s = s.replace('&', '&amp;')
	s = s.replace('<', '&lt;').replace('>', '&gt;')
	return s.replace('"', '&quot;').replace("'", '&apos;')

def assertEq(expected, received):
    if expected != received:
        raise AssertionError('expected %s but got %s' %(expected, received))

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

*language.sql=S&QL|sql||
*language.html=H&TML|html|Control+Alt+Shift+F11|
*language.php=P&HP|php|$(keyMissing)|
*language.xml=&XML|xml|$(keyXML)|
keyXML=Alt+Shift+/

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

	props = PropSetFile()
	props.ReadString(mockProperties)
	results = readFromProperties(props)
	results.sort(key=lambda obj: obj.getSortKey())

	expected = '''Alt+Shift+/|set language XML|40|unknown|properties *language
Ctrl+4|Test Ddd|50|any|properties command (implicit)
Ctrl+Aaa|Test Aaa|50|any|properties command
Ctrl+Bbb|Test Bbb|50|any|properties command
Ctrl+Alt+Shift+F11|set language HTML|40|unknown|properties *language
Shift+F12|Test Custom|50|any|properties command
Ctrl+PageDown|IDM_NEXTFILE|60|unknown|properties user.shortcuts
Shift+Tab|Test Ccc|50|*.y|properties command
Ctrl+Shift+V|IDM_PASTEANDDOWN|60|unknown|properties user.shortcuts'''
	expectedArr = []
	addBindingsManual(expectedArr, expected)
	assertEqArray(expectedArr, results)
	
	
if __name__ == '__main__':
	tests()
