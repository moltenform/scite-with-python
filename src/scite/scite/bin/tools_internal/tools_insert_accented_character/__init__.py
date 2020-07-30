# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from scite_extend_ui import ScEditor, ScAskUserChoiceByPressingKey

lowerGrave = dict(a=u'\u00E0', e=u'\u00E8', i=u'\u00EC', o=u'\u00F2', u=u'\u00F9')
lowerAcute = dict(a=u'\u00E1', e=u'\u00E9', i=u'\u00ED', o=u'\u00F3', u=u'\u00FA', y=u'\u00FD')
lowerCircumflex = dict(a=u'\u00E2', e=u'\u00EA', i=u'\u00EE', o=u'\u00F4', u=u'\u00FB')
lowerTilde = dict(a=u'\u00E3', o=u'\u00F5', r=u'\u00E5')
lowerDiaeresis = dict(a=u'\u00E4', e=u'\u00EB', i=u'\u00EF', o=u'\u00F6', u=u'\u00FC', y=u'\u00FF')
lowerConsonants = dict(c=u'\u00E7', d=u'\u00F0', n=u'\u00F1', t=u'\u00FE')
upperGrave = dict(a=u'\u00C0', e=u'\u00C8', i=u'\u00CC', o=u'\u00D2', u=u'\u00D9')
upperAcute = dict(a=u'\u00C1', e=u'\u00C9', i=u'\u00CD', o=u'\u00D3', u=u'\u00DA', y=u'\u00DD')
upperCircumflex = dict(a=u'\u00C2', e=u'\u00CA', i=u'\u00CE', o=u'\u00D4', u=u'\u00DB')
upperTilde = dict(a=u'\u00C3', o=u'\u00D5', r=u'\u00C5')
upperDiaeresis = dict(a=u'\u00C4', e=u'\u00CB', i=u'\u00CF', o=u'\u00D6', u=u'\u00DC')
upperConsonants = dict(c=u'\u00C7', d=u'\u00D0', n=u'\u00D1', t=u'\u00DE', s=u'\u00DF')
punctuation = dict(e=u'\u00A1', q=u'\u00BF', t=u'\u00A2', p=u'\u00A3', s=u'\u00A7', c=u'\u00A9',
    a=u'\u00AA', j=u'\u00AB', k=u'\u00BB', n=u'\u00AC', r=u'\u00AE', o=u'\u00B0', m=u'\u00B1',
    _0=u'\u00BA', _1=u'\u00B9', _2=u'\u00B2', _3=u'\u00B3', _8=u'\u00B7', _4=u'\u00BC', _5=u'\u00BD', _6=u'\u00BE',
    x=u'\u00F7', y=u'\u00D7')

index = dict(
    G=('lower-case grave accent', lowerGrave), A=('lower-case acute accent', lowerAcute), _6=('lower-case circumflex', lowerCircumflex), T=('lower-case tilde', lowerTilde), D=('lower-case diaeresis/umlaut', lowerDiaeresis), C=('lower-case consonants', lowerConsonants),
    H=('upper-case grave accent', upperGrave), S=('upper-case acute accent', upperAcute), _7=('upper-case circumflex', upperCircumflex), Y=('upper-case tilde', upperTilde), F=('upper-case diaeresis/umlaut', upperDiaeresis), V=('upper-case consonants', upperConsonants),
    P=('add punctuation', punctuation))

def isString(s):
    import sys
    if sys.version[0] > 2:
        return isinstance(val, str)
    else:
        return isinstance(val, basestring)

def choicesFromDict(d):
    ret = []
    for dictkey in d:
        character = dictkey.replace('_', '').upper()
        val = d[dictkey]
        showText = val if isString(val) else val[0]
        showText = showText.encode('utf-8')
        ret.append(character + '|' + dictkey + '|' + showText)
    
    sortElement = 0 if d is punctuation else 2
    return sorted(ret, key=lambda s: s.split('|')[sortElement])

class ChooseCharacter(object):
    def __init__(self, newDict):
        self.newDict = newDict

    def go(self):
        self.choices = choicesFromDict(self.newDict)
        ScAskUserChoiceByPressingKey(
            choices=self.choices, callback=self.onChoiceMade)
     
    def onChoiceMade(self, choice):
        resultingChar = self.newDict.get(choice, None)
        if resultingChar:
            resultingCharUtf8 = resultingChar.encode('utf-8')
            editorEncoded, len = ScEditor.EncodedFromUTF8(resultingCharUtf8)
            ScEditor.ReplaceSel(editorEncoded)
            
    
class ChooseCharacterType(object):
    def go(self):
        self.choices = choicesFromDict(index)
        ScAskUserChoiceByPressingKey(
            choices=self.choices, callback=self.onChoiceMade)
     
    def onChoiceMade(self, choice):
        chosenTuple = index.get(choice, None)
        if chosenTuple:
            name, newDict = chosenTuple
            ChooseCharacter(newDict).go()


def DoInsertAccentedCharacter():
    ChooseCharacterType().go()

