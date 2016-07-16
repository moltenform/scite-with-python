
from scite_extend_ui import *

class ChangeOrder(object):
    def go(self):
        self.choices = ['sortaz|Sort A-Z', 'sortza|Sort Z-A', 'reverse|Reverse', 
            'shuffle|Quick shuffle', 'sortnum|Sort numbers naturally', 
            'sortcol2|Sort by 2nd col', 'sortcol3|Sort by 3rd col']
        label = 'Please choose from this list how to change the order of selected lines:'
        ScAskUserChoice(choices=self.choices, label=label, callback=self.onChoiceMade)
     
    def onChoiceMade(self, choice):
        from __init__ import modifyTextInScite
        return modifyTextInScite(lambda text: self.runSort(text, choice))

    def runSort(self, text, choice):
        # look for a method named choice
        assert choice in [s.split('|')[0] for s in self.choices]
        method = self.__getattribute__(choice)
        
        # validate lines and get newline character
        newlineChar = self.getLineCharacter(text)
        if not newlineChar:
            return None
        
        # split text into lines
        lines = text.split(newlineChar)
        method(lines)
        return newlineChar.join(lines)
        
    def getLineCharacter(self, text, silent=None):
        text = text or ''
        if '\n' not in text:
            print(silent or 'Please select at least two lines.')
            return False
        
        if '\r\n' in text:
            # make sure it doesn't have both \r\n and \n.
            textNoWindows = text.replace('\r\n', '')
            if '\n' in textNoWindows:
                print(silent or 'Contains both unix and windows newlines, ' +
                    'please address this first.')
                return False
            
            return '\r\n'
        else:
            return '\n'

    def sortaz(self, lines):
        lines.sort()

    def sortza(self, lines):
        lines.sort(reverse=True)
    
    def reverse(self, lines):
        lines.reverse()

    def shuffle(self, lines):
        # we call it quick shuffle in UI because the number of permutations is often 
        # larger than the RNG period, and so for some lengths many orderings will never be seen.
        import random
        random.shuffle(lines)
        
    def sortnum(self, lines):
        import changeordernaturalsort
        changeordernaturalsort.naturalsort(lines)

    def sortcol2(self, lines):
        return self.sortcoln(lines, 1)

    def sortcol3(self, lines):
        return self.sortcoln(lines, 2)
    
    def sortcoln(self, lines, whichColToSort):
        def key(text):
            # the idea is to move the desired column to the front as if it were the first
            parts = text.split()
            
            if whichColToSort <= len(parts) - 1:
                parts.insert(0, parts[whichColToSort])
            else:
                # column is empty, so add empty to the front
                parts.insert(0, '')
            return parts
            
        lines.sort(key=key)

def DoChangeOrder():
    ChangeOrder().go()

if __name__ == '__main__':
    from ben_python_common import assertEq
    
    # unit tests
    obj = ChangeOrder()
    silent = ' ' # print empty lines instead of warnings
    assertEq(False, obj.getLineCharacter(None, silent))
    assertEq(False, obj.getLineCharacter('', silent))
    assertEq(False, obj.getLineCharacter('abc', silent))
    assertEq('\n', obj.getLineCharacter('\n', silent))
    assertEq('\n', obj.getLineCharacter('\n\n\n', silent))
    assertEq('\n', obj.getLineCharacter('abc\nabc', silent))
    assertEq('\n', obj.getLineCharacter('\nabc\nabc\n', silent))
    assertEq('\r\n', obj.getLineCharacter('abc\r\nabc', silent))
    assertEq('\r\n', obj.getLineCharacter('\r\nabc\r\nabc\r\n', silent))
    assertEq(False, obj.getLineCharacter('\r\n\n', silent))
    assertEq(False, obj.getLineCharacter('\n\r\n', silent))
    assertEq(False, obj.getLineCharacter('a\na\r\na', silent))
    assertEq(False, obj.getLineCharacter('a\r\na\na', silent))
    
    # first col alternates between a and b
    # second col counts upwards
    # third col counts downwards
    test = 'a 1 5|b 2 4|a 3 3|b 4 2|a 5 1'.split('|')
    normalSort, reverseSort, sort2nd, sort3rd = list(test), list(test), list(test), list(test)
    obj.sortaz(normalSort)
    obj.sortza(reverseSort)
    obj.sortcol2(sort2nd)
    obj.sortcol3(sort3rd)
    expectedNormalSort = ['a 1 5', 'a 3 3', 'a 5 1', 'b 2 4', 'b 4 2']
    expectedReverseSort = ['b 4 2', 'b 2 4', 'a 5 1', 'a 3 3', 'a 1 5']
    expectedSort2nd = ['a 1 5', 'b 2 4', 'a 3 3', 'b 4 2', 'a 5 1']
    expectedSort3rd = ['a 5 1', 'b 4 2', 'a 3 3', 'b 2 4', 'a 1 5']
    assertEq(expectedNormalSort, normalSort)
    assertEq(expectedReverseSort, reverseSort)
    assertEq(expectedSort2nd, sort2nd)
    assertEq(expectedSort3rd, sort3rd)
    
    # cases where the line has only one col, exactly two cols, or more than two cols
    # if it only has one col it should be sorted to the beginning
    testEmptyCases = 'a  z  1|b y|c  x|d  |e|f  a'.split('|')
    expectedEmptyCases = ['d  ', 'e', 'f  a', 'c  x', 'b y', 'a  z  1']
    obj.sortcol2(testEmptyCases)
    assertEq(testEmptyCases, expectedEmptyCases)
    
