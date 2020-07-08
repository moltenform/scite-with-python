# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

class ChangeCasing(object):
    def go(self):
        from scite_extend_ui import ScAskUserChoiceByPressingKey
        self.choices = ['U|upper|Upper case', 'L|lower|Lower case', 'T|title|Title case']
        label = 'Please choose a way to change the selected text:'
        ScAskUserChoiceByPressingKey(choices=self.choices, label=label, callback=self.onChoiceMade)
    
    def onChoiceMade(self, choice):
        # look for a method named choice, and call it
        from __init__ import modifyTextSupportsMultiSelection
        assert choice in [s.split('|')[1] for s in self.choices]
        method = self.__getattribute__(choice)
        return modifyTextSupportsMultiSelection(method, resetSelection=False)

    def upper(self, s):
        return s.upper()
        
    def lower(self, s):
        return s.lower()

    def title(self, s):
        result = ''
        for i, c in enumerate(s):
            # if it's not adjacent to a letter, make it capitalized.
            if i == 0 or not s[i - 1].isalpha():
                result += c.upper()
            else:
                result += c.lower()
                
        return result

def DoChangeCasing():
    from scite_extend_ui import ScEditor
    ChangeCasing().go()

if __name__ == '__main__':
    from ben_python_common import assertEq
    
    # unit tests
    obj = ChangeCasing()
    assertEq('', obj.title(''))
    assertEq('A', obj.title('a'))
    assertEq('Aa', obj.title('aa'))
    assertEq('Aa Aa', obj.title('aa aa'))
    assertEq('Aa Aa', obj.title('AA AA'))
    assertEq('A B C D', obj.title('a b c d'))
    assertEq('A.B|C/D"E\'F\\G-H_I:J', obj.title('a.b|c/d"e\'f\\g-h_i:j'))
    assertEq('0A1Bb2Ccc3', obj.title('0a1bb2ccc3'))
    assertEq('0A1Bb2Ccc3', obj.title('0A1Bb2Ccc3'))
    assertEq('0A1Bb2Ccc3', obj.title('0A1BB2CCC3'))
    