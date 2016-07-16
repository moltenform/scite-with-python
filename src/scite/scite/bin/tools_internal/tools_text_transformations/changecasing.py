
from scite_extend_ui import *

class ChangeCasing(object):
    def go(self):
        self.choices = ['upper|Upper case', 'lower|Lower case', 'title|Title case']
        label = 'Please choose a way from this list to change the selected text:'
        ScAskUserChoice(choices=self.choices, label=label, callback=self.onChoiceMade)
    
    def onChoiceMade(self, choice):
        # look for a method named choice, and call it
        from __init__ import modifyTextInScite
        assert choice in [s.split('|')[0] for s in self.choices]
        method = self.__getattribute__(choice)
        return modifyTextInScite(method)

    def upper(self, s):
        return s.upper()
        
    def lower(self, s):
        return s.lower()

    def title(self, s):
        result = ''
        for i, c in enumerate(s):
            if i == 0 or not s[i - 1].isalpha():
                result += c.upper()
            else:
                result += c.lower()
                
        return result

def DoChangeCasing():
    ChangeCasing().go()

if __name__ == '__main__':
    from ben_python_common import assertEq
    
    # unit tests
    obj = ChangeCasingImpl()
    assertEq('', obj.titleCase(''))
    assertEq('A', obj.titleCase('a'))
    assertEq('Aa', obj.titleCase('aa'))
    assertEq('Aa Aa', obj.titleCase('aa aa'))
    assertEq('Aa Aa', obj.titleCase('AA AA'))
    assertEq('A B C D', obj.titleCase('a b c d'))
    assertEq('A.B|C/D"E\'F\\G-H_I:J', obj.titleCase('a.b|c/d"e\'f\\g-h_i:j'))
    assertEq('0A1Bb2Ccc3', obj.titleCase('0a1bb2ccc3'))
    assertEq('0A1Bb2Ccc3', obj.titleCase('0A1Bb2Ccc3'))
    assertEq('0A1Bb2Ccc3', obj.titleCase('0A1BB2CCC3'))
    