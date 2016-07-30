
import os

def readall(filename, mode='r'):
	with open(filename, mode) as f:
		return f.read()

class PropSetFile(object):
	props = None
	def __init__(self):
		self.props = dict()
	def Set(self, key, val):
		self.props[key] = val
	def Unset(self, key):
		try:
			del self.props[key]
		except KeyError:
			pass
	def Exists(self, key):
		return key in self.props
	def GetString(self, key):
		return self.props.get(key, '')
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
		
		self._ReadLine(s) # in case file ended with a \
			
	def _ReadLine(self, s):
		if s.startswith('#'):
			return
		if not s.strip():
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
		if not path.endswith(os.sep + 'disabled'):
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
	keyCommandName = cmd + '.name.' + number + '.' + filetypes
	readCommandShortcutGeneral(results, props, key, keyCommandName, platform=platform)

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
			if item == 'Control':
				self.control = True
			elif item == 'Ctrl':
				self.control = True
			elif item == 'Alt':
				self.alt = True
			elif item == 'Shift':
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
	def __str__(self):
		return self.getKeyString() + ' --> ' + self.command
	def __repr__(self):
		return '|'.join((self.getKeyString(), self.command, str(self.priority), self.platform, self.setName))

def addBindingsManual(bindings, s):
	lines = s.replace('\r\n', '\n').split('\n')
	for line in lines:
		if line.strip():
			binding = KeyBinding()
			modifiersAndKey, binding.command, binding.priority, binding.platform, binding.setName = line.split('|')
			binding.setKeyFromString(modifiersAndKey)
			binding.priority = int(binding.priority)
			bindings.append(binding)

def assertEq(expected, received):
    if expected != received:
        raise AssertionError('expected %s but got %s' %(expected, received))

def tests():
	mockProperties = '''
customcommand.test.name=Test Custom
customcommand.test.shortcut=Shift+F12

#customcommand.commented.name=Test cmtd
#customcommand.commented.shortcut=F1

user.shortcuts=\
Ctrl+Shift+V|IDM_PASTEANDDOWN|\
Ctrl+PageUp|IDM_PREVFILE|\
Ctrl+PageDown|IDM_NEXTFILE|

*language.sql=S&QL|sql||
*language.html=H&TML|html|$(keyHTML)|
*language.php=P&HP|php|$(keyMissing)|
*language.xml=&XML|xml|$(keyXML)|
keyHTML=Control+Alt+Shift+F11
keyXML=Alt+Shift+/

fff=*
command.name.11.$(fff)=Test Aaa
command.11.$(fff)=dostuff(x,y,z)
command.shortcut.11.$(fff)=Ctrl+Aaa

command.name.12.*.*=Test Bbb
command.12.*.*=dostuff(x,y,z)
command.shortcut.12.*.*=Ctrl+Bbb

command.name.13.*.y=Test Ccc
command.shortcut.13.*.y=Shift+Tab
'''
	props = PropSetFile()
	props.ReadString(mockProperties)
	results = readFromProperties(props)
	results.sort(key=lambda obj: obj.getSortKey())

	expected = '''
Alt+Shift+/|set language XML|40|unknown|properties *language
Ctrl+Aaa|Test Aaa|50|any|properties command
Ctrl+Bbb|Test Bbb|50|any|properties command
Ctrl+Alt+Shift+F11|set language HTML|40|unknown|properties *language
Shift+F12|Test Custom|50|any|properties command
Ctrl+PageDown|IDM_NEXTFILE|60|unknown|properties user.shortcuts
Ctrl+PageUp|IDM_PREVFILE|60|unknown|properties user.shortcuts
Shift+Tab|Test Ccc|50|*.y|properties command
Ctrl+Shift+V|IDM_PASTEANDDOWN|60|unknown|properties user.shortcuts'''
	expectedArr = []
	addBindingsManual(expectedArr, expected)
	assertEq(len(expectedArr), len(results))
	for i in range(len(expectedArr)):
		assertEq(repr(expectedArr[i]), repr(results[i]))
	
	
if __name__ == '__main__':
	tests()
	
	