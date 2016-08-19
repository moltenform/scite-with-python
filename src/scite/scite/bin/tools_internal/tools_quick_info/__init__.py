
import ben_python_common
from ben_python_common import files

try:
    from configparser import RawConfigParser, NoOptionError
except ImportError:
    from ConfigParser import RawConfigParser, NoOptionError

def getStorageFilePath():
    from scite_extend_ui import ScApp
    appUserDir = ScApp.GetSciteUserDirectory()
    return ben_python_common.files.join(appUserDir, 'SciTE_quick_info.session')

class BaseAskChoiceStoredData(object):
    def __init__(self, title, sectionName, filename, getOrSet):
        self.title = title
        self.sectionName = sectionName
        self.filename = filename
        self.getOrSet = getOrSet
        self.backingStorage = RawConfigParser()
        self.backingStorage.read(self.filename)
        if not self.backingStorage.has_section(self.sectionName):
            self.backingStorage.add_section(self.sectionName)
        
    def go(self):
        from scite_extend_ui import ScAskUserChoiceByPressingKey
        choices = []
        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789':
            keyToPress = ch
            choiceId = 'key_' + ch
            currentContents = self.getData(choiceId)
            if not self.getOrSet or currentContents:
                label = self.getLabel(ch, currentContents)
                choices.append('|'.join((keyToPress, choiceId, label)))
        
        if not choices:
            print('Nothing stored here yet.')
        else:
            ScAskUserChoiceByPressingKey(label=self.title,
                choices=choices, callback=self.onChoiceMade, showPerforming=False)
    
    def getLabel(self, ch, currentContents):
        if self.getOrSet:
            return '%s %s' % (self.getRetrieveLabel(), self.printable(currentContents))
        elif currentContents:
            return 'store in slot %s (currently %s)' % (ch.lower(), self.printable(currentContents))
        else:
            return 'store in slot %s' % ch.lower()
    
    def onChoiceMade(self, choiceId):
        currentContents = self.getData(choiceId)
        if self.getOrSet:
            if currentContents:
                self.onRetrieve(choiceId, currentContents)
            else:
                print('Nothing is currently stored in this field.')
        else:
            value = self.getValueForInput()
            if value:
                self.storeData(choiceId, value)
                self.onStore(choiceId, value)
    
    def getData(self, choiceId):
        try:
            return self.decode(self.backingStorage.get(self.sectionName, choiceId))
        except NoOptionError:
            return ''
    
    def storeData(self, choiceId, value):
        self.backingStorage.set(self.sectionName, choiceId, self.encode(value))
        with open(self.filename, 'wb') as f:
            self.backingStorage.write(f)
        self.backingStorage.read(self.filename)
    
    def encode(self, s):
        return s.replace('\r\n', '$NEWLINE_RN$').replace('\r', '$NEWLINE_R$').replace('\n', '$NEWLINE_N$')
    
    def decode(self, s):
        return s.replace('$NEWLINE_RN$', '\r\n').replace('$NEWLINE_R$', '\r').replace('$NEWLINE_N$', '\n')
    
    def printable(self, s):
        currentPrintable = s.replace('\r', ' ').replace('\n', ' ')
        if len(currentPrintable) > 200:
            currentPrintable = currentPrintable[0:200] + '...'
        return currentPrintable
        
    def getValueForInput(self):
        raise NotImplementedError()
        
    def onStore(self, choiceId, value):
        print('Stored the value %s' % (self.printable(value)))


class AskChoiceStoredFilepath(BaseAskChoiceStoredData):
    def onRetrieve(self, choiceId, value):
        from scite_extend_ui import ScApp
        print('Opening file:%s' % self.printable(value))
        ScApp.OpenFile(value)
        
    def getValueForInput(self):
        from scite_extend_ui import ScApp
        val = ScApp.GetFilePath()
        if not val:
            print('No file open')
            return None
        else:
            return val
        
    def getRetrieveLabel(self):
        return 'open'

class AskChoiceStoredDirectory(BaseAskChoiceStoredData):
    def onRetrieve(self, choiceId, value):
        print('Opening directory:%s' % self.printable(value))
        ben_python_common.files.openDirectoryInExplorer(value)
        
    def getValueForInput(self):
        import os
        from scite_extend_ui import ScApp
        val = ScApp.GetFilePath()
        if not val:
            print('No file open')
            return None
        else:
            return os.path.split(val)[0]
    
    def getRetrieveLabel(self):
        return 'open'

class AskChoiceStoredString(BaseAskChoiceStoredData):
    def onRetrieve(self, choiceId, value):
        from scite_extend_ui import ScEditor
        print('Copying text to clipboard:%s' % self.printable(value))
        ScEditor.Utils.SetClipboardText(value)

    def getValueForInput(self):
        from scite_extend_ui import ScEditor
        val = ScEditor.GetSelectedText()
        if not val:
            print('First, please select some text.')
            return None
        else:
            return val

    def getRetrieveLabel(self):
        return 'copy'

def getFileList(dir, sortByExtension):
    skipExts = dict(pyc=0, pyo=0, so=0, o=0, a=0, tgz=0, gz=0, rar=0, zip=0, bak=0,
        pdb=0, png=0, jpg=0, gif=0, bmp=0, tif=0, tiff=0, pyd=0, dll=0, exe=0, obj=0, lib=0, webp=0)
    
    skipExts['7z'] = 0
    listFiles = []
    if dir:
        for full, short in files.listfiles(dir):
            if not short.startswith('.'):
                extension = files.splitext(short)[1].lstrip('.')
                if extension not in skipExts:
                    listFiles.append((short, extension))
        
        if sortByExtension:
            listFiles.sort(key=lambda tp: tp[1])
        else:
            listFiles.sort(key=lambda tp: tp[0])
            
    return [file[0] for file in listFiles]

class QuickInfo(object):
    def go(self):
        from scite_extend_ui import ScAskUserChoiceByPressingKey
        self.choices = ['O|storedfilename_get|open remembered file...',
        'P|storedfilename_set|remember current file...\n',
        'J|storeddirectory_get|open remembered directory...',
        'K|storeddirectory_set|remember directory of current file...\n',
        'T|storedstring_get|open remembered text...',
        'Y|storedstring_set|remember selected text...\n',
        'L|listfiles|list files in this directory',
        'M|listfilesext|list files, sort by extension',
        'Z|openscratchfile|open scratch file']
        ScAskUserChoiceByPressingKey(
            choices=self.choices, callback=self.onChoiceMade, showPerforming=False)
    
    def onChoiceMade(self, choice):
        if choice == 'listfilesext':
            return self.listfiles(True)
        elif choice == 'listfiles':
            return self.listfiles(False)
        elif choice == 'openscratchfile':
            return self.openscratchfile()
        else:
            type, action = choice.split('_')
            getOrSet = action == 'get'
            sectionName = type
            classType = None
            if type == 'storedfilename':
                classType = AskChoiceStoredFilepath
            elif type == 'storeddirectory':
                classType = AskChoiceStoredDirectory
            elif type == 'storedstring':
                classType = AskChoiceStoredString
            
            if getOrSet:
                title = ''
            else:
                title = 'Each slot can hold one %s, \nplease choose the slot to assign into:\n' % \
                    type.replace('stored', '')
                
            storageFilename = getStorageFilePath()
            obj = classType(title, sectionName, storageFilename, getOrSet)
            obj.go()

    def openscratchfile(self):
        from scite_extend_ui import ScApp
        propname = 'customcommand.quick_info.scratchfilepath'
        scratchpath = ScApp.GetProperty(propname)
        propertiesfile = files.join(ScApp.GetSciteDirectory(),
                'tools_internal', 'tools_quick_info', 'register.properties')
        if not scratchpath:
            print('No scratch file path set, please open \n%s\n and provide a value for \n%s\n' %
                (propertiesfile, propname))
        elif not files.isfile(scratchpath):
            print(('scratch file path set to %s but this file does not exist, please ' +
                'open \n%s\n and provide a value for \n%s\n') %
                (scratchpath, propertiesfile, propname))
        else:
            ScApp.OpenFile(scratchpath)

    def listfiles(self, sortByExtension):
        from scite_extend_ui import ScApp
        
        # print the filenames, SciTE will make them clickable links
        print('Contents of %s' % ScApp.GetFileDirectory())
        for name in getFileList(ScApp.GetFileDirectory(), sortByExtension):
            print(name + ':1: ')


def DoQuickInfo():
    QuickInfo().go()

class ShowFileChoiceList(object):
    def __init__(self, dir, prefix):
        self.dir = dir
        self.prefix = prefix
    
    def go(self):
        from scite_extend_ui import ScAskUserChoiceByPressingKey
        import string
        if not self.dir:
            return
        
        self.fileList = getFileList(self.dir, sortByExtension=False)
        self.choices = ['U|updirectory|Go up a directory...']
        availableLetters = string.digits + string.uppercase.replace('U', '')
        for i, file in enumerate(self.fileList):
            if i < len(availableLetters):
                character = availableLetters[i]
                s = self.prefix + file
                self.choices.append('%s|%d|%s' % (character, i, s))
        
        label = 'Pick a file to open in %s.' % self.dir
        if len(self.fileList) > len(availableLetters):
            label += '\nToo many files... the rest are ommitted.'
        
        ScAskUserChoiceByPressingKey(
            choices=self.choices, callback=self.onChoiceMade, label=label, showPerforming=False)
    
    def onChoiceMade(self, choiceId):
        import os
        if choiceId == 'updirectory':
            newObject = ShowFileChoiceList(os.path.split(self.dir)[0], '..' + os.sep + self.prefix)
            newObject.go()
        else:
            from scite_extend_ui import ScApp
            index = int(choiceId)
            filename = self.fileList[index]
            ScApp.OpenFile(os.path.join(self.dir, filename))

def DoListFilesInFolder():
    from scite_extend_ui import ScApp
    ShowFileChoiceList(ScApp.GetFileDirectory(), '').go()
    
if __name__ == '__main__':
    from ben_python_common import assertEq
    
    filename = './testcfg.cfg'
    sectionName = 'testSection1'
    obj = AskChoiceStoredString(title='', sectionName='', filename=filename, getOrSet=True)
    roundTrip = lambda input: assertEq(input, obj.decode(obj.encode(input)))
        
    roundTrip('')
    roundTrip('\r\n\r\n')
    roundTrip('\n\n')
    roundTrip('\r\r')
    roundTrip('a \n b \r\n c \r')
    roundTrip('\r\n \r\r \n\n \n\r \r\n')
    
    try:
        # write choice_a='100' into section 1.
        sectionName = 'testSection1'
        obj = AskChoiceStoredString(title='', sectionName=sectionName, filename=filename, getOrSet=True)
        obj.storeData('choice_a', '100')
        
        # write choice_a='has new\n line' into section 2.
        sectionName = 'testSection2'
        obj = AskChoiceStoredString(title='', sectionName=sectionName, filename=filename, getOrSet=True)
        obj.storeData('choice_a', 'has new\n line')
        
        # verify section 1
        sectionName = 'testSection1'
        obj = AskChoiceStoredString(title='', sectionName=sectionName, filename=filename, getOrSet=True)
        assertEq('100', obj.getData('choice_a'))
        
        # verify section 2
        sectionName = 'testSection2'
        obj = AskChoiceStoredString(title='', sectionName=sectionName, filename=filename, getOrSet=True)
        assertEq('has new\n line', obj.getData('choice_a'))
        
        # read missing option should return empty string
        sectionName = 'sectionMissing'
        obj = AskChoiceStoredString(title='', sectionName=sectionName, filename=filename, getOrSet=True)
        assertEq('', obj.getData('choice_missing'))
        
        # read from missing section should create the section and return empty string
        sectionName = 'sectionMissing'
        obj = AskChoiceStoredString(title='', sectionName=sectionName, filename=filename, getOrSet=True)
        assertEq('', obj.getData('choice_a'))
        
    finally:
        if files.exists(filename):
            files.delete(filename)
    
    
    