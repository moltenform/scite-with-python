
class ChangeLines(object):
    def go(self):
        from scite_extend_ui import ScAskUserChoiceByPressingKey
        self.choices = ['A|sortaz|Sort A-Z',
            'Z|sortza|Sort Z-A',
            'R|reverse|Reverse', 
            'S|shuffle|Quick shuffle',
            'N|sortnum|Sort numbers naturally', 
            '2|sortcol2|Sort by 2nd col',
            '3|sortcol3|Sort by 3rd col',
            '4|sortcol4|Sort by 4th col',
            'X|splitxml|Split xml by >',
            'T|trimempty|trim empty lines',
            'I|splitwithindent|Split to lines, with indentation',
            'J|joinwithoutindent|Join from trimmed lines',
            'D|joinwithoutindentadddelim|Join from trimmed lines and add ;',
            'Q|insertsequencehelp|How to use insert numbered sequence',
            '0|insertsequence|Insert numbered sequence']
        label = 'Please choose from this list how to change the selected lines:'
        ScAskUserChoiceByPressingKey(
            choices=self.choices, label=label, callback=self.onChoiceMade)
     
    def onChoiceMade(self, choice):
        from __init__ import modifyTextInScite
        from scite_extend_ui import ScEditor
        ScEditor.Utils.ExpandSelectionToIncludeEntireLines()
        return modifyTextInScite(lambda text: self.runSort(text, choice))

    def runSort(self, text, choice):
        # look for a method named choice
        assert choice in [s.split('|')[1] for s in self.choices]
        method = self.__getattribute__(choice)
        
        # validate lines and get newline character
        self.newlineChar = self.getLineCharacter(text, choice=choice)
        if not self.newlineChar:
            return None
        
        # split text into lines
        lines = text.split(self.newlineChar)
        method(lines)
        return self.newlineChar.join(lines)
        
    def getLineCharacter(self, text, silent=None, choice=None):
        import re
        text = text or ''
        
        # we don't expect to end with a newline
        # because of the logic in expandSelectionToIncludeEntireLines.
        assert not text or text[-1] not in ('\r', '\n')
        
        reWindows = re.compile('\r\n', re.M)
        reMacClassic = re.compile('\r[^\n]', re.M)
        reUnix = re.compile('[^\r]\n', re.M)
        hasWindows = re.search(reWindows, text)
        hasMacClassic = re.search(reMacClassic, text)
        hasUnix = re.search(reUnix, text)
        countTypes = sum(bool(found) for found in (hasWindows, hasMacClassic, hasUnix))
        if countTypes == 0:
            if choice not in ('splitxml', 'splitwithindent'):
                print(silent or 'Please select at least two lines.')
                return None
            else:
                from scite_extend_ui import ScEditor
                return ScEditor.GetEolCharacter()
        elif countTypes == 1:
            if hasWindows:
                return '\r\n'
            elif hasMacClassic:
                return '\r'
            else:
                return '\n'
        else:
            print(silent or 'Contains both unix and windows newlines, ' +
                    'please address this first.')
            return None

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
        
    def sortcol4(self, lines):
        return self.sortcoln(lines, 3)
    
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
    
    def splitxml(self, lines):
        # put a nl after every > that wasn't already next to a nl
        for i in range(len(lines)):
            allButLastChar = lines[i][0:-1]
            lastChar = lines[i][-1]
            lines[i] = allButLastChar.replace('>', '>' + self.newlineChar) + lastChar
    
    def trimempty(self, lines):
        # deletes empty lines
        result = [line for line in lines if line.strip()]
        lines[:] = result
    
    def splitwithindent(self, lines, delimiter=';'):
        # splits the lines, but adds an appropriate amount of whitespace before each line
        result = []
        for line in lines:
            countLeftWhitespace = len(line) - len(line.lstrip())
            leftWhitespace = line[0:countLeftWhitespace]
            parts = line.split(delimiter)
            result.extend(((leftWhitespace + part.strip()) for part in parts))
            
        lines[:] = result
        
    def joinwithoutindent(self, lines, delimiter=' '):
        # join and strip unneeded whitespace.
        countLeftWhitespace = len(lines[0]) - len(lines[0].lstrip())
        keepInitialWhitespace = lines[0][0:countLeftWhitespace]
        result = delimiter.join((line.strip() for line in lines))
        lines[:] = [keepInitialWhitespace + result]
        
    def joinwithoutindentadddelim(self, lines):
        self.joinwithoutindent(lines, '; ')
    
    def insertsequencehelp(self, lines):
        import insertsequentialnumbers
        insertsequentialnumbers.insertsequentialnumbershelp()
    
    def insertsequence(self, lines):
        import insertsequentialnumbers
        insertsequentialnumbers.insertsequentialnumbers(lines)

def DoChangeLines():
    ChangeLines().go()

if __name__ == '__main__':
    from ben_python_common import assertEq
    
    # unit tests
    obj = ChangeLines()
    silent = ' ' # print empty lines instead of warnings
    assertEq(None, obj.getLineCharacter(None, silent))
    assertEq(None, obj.getLineCharacter('', silent))
    assertEq(None, obj.getLineCharacter('abc', silent))
    assertEq('\n', obj.getLineCharacter('\n\na', silent))
    assertEq('\n', obj.getLineCharacter('a \n b', silent))
    assertEq('\n', obj.getLineCharacter('a \n\n\n b', silent))
    assertEq('\r', obj.getLineCharacter('\r\ra', silent))
    assertEq('\r', obj.getLineCharacter('a \r b', silent))
    assertEq('\r', obj.getLineCharacter('a \r\r\r b', silent))
    assertEq('\r\n', obj.getLineCharacter('\r\n\r\na', silent))
    assertEq('\r\n', obj.getLineCharacter('a \r\n b', silent))
    assertEq('\r\n', obj.getLineCharacter('a \r\n\r\n\r\n b', silent))
    assertEq(None, obj.getLineCharacter('a \n\r b', silent))
    assertEq(None, obj.getLineCharacter('a \r\n\n b', silent))
    assertEq(None, obj.getLineCharacter('a \n\r\n b', silent))
    assertEq(None, obj.getLineCharacter('a \n\n\r b', silent))
    assertEq(None, obj.getLineCharacter('a \n\r\r b', silent))
    assertEq(None, obj.getLineCharacter('a \r\n\r b', silent))
    assertEq(None, obj.getLineCharacter('a \r\r\n b', silent))
    assertEq(None, obj.getLineCharacter('a \r   \n\n b', silent))
    assertEq(None, obj.getLineCharacter('a \n   \r\n b', silent))
    assertEq(None, obj.getLineCharacter('a \n   \n\r b', silent))
    assertEq(None, obj.getLineCharacter('a \n\n   \r b', silent))
    assertEq(None, obj.getLineCharacter('a \n   \r\r b', silent))
    assertEq(None, obj.getLineCharacter('a \r   \n   \r b', silent))
    assertEq(None, obj.getLineCharacter('a \r\r   \n b', silent))
    
    # counter-intuitive, but not a common user scenario
    assertEq(None, obj.getLineCharacter('\na', silent))
    
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
    
    def testLines(expected, input, fn):
        arr = input.split('|')
        fn(arr)
        assertEq(expected, '|'.join(arr))
    
    # cases where the line has only one col, exactly two cols, or more than two cols
    # if it only has one col it should be sorted to the beginning
    testEmptyCases = 'a  z  1|b y|c  x|d  |e|f  a'
    expectedEmptyCases = 'd  |e|f  a|c  x|b y|a  z  1'
    testLines(expectedEmptyCases, testEmptyCases, obj.sortcol2)
    
    obj.newlineChar = '\n'
    testLines('a b c', 'a b c', obj.splitxml)
    testLines('<a>\n <b>\n <c>', '<a> <b> <c>', obj.splitxml) # final does not need a \n
    testLines('<a>|<b>|<c>', '<a>|<b>|<c>', obj.splitxml) # it already has a \n
    testLines('<a>\n |<b>| <c>', '<a> |<b>| <c>', obj.splitxml)
    testLines('a|b|c', 'a||b||c', obj.trimempty)
    testLines('a|b|c|d', 'a|  |b|\t\t|c|  \t|d', obj.trimempty)
    testLines('a|b|c', 'a||||||b||c', obj.trimempty)
    
    testLines('a', 'a', obj.splitwithindent)
    testLines('  a', '  a', obj.splitwithindent)
    testLines('a|b|c', 'a;b;c', obj.splitwithindent)
    testLines('a|b|c', 'a  ;  b  ;  c  ', obj.splitwithindent)
    testLines('\ta|\tb|\tc', '\ta;b;c', obj.splitwithindent)
    testLines('\ta|\tb|\tc', '\ta  ;  b  ;  c  ', obj.splitwithindent)
    testLines('\ta|\tb|\tc|a|b|c|', '\ta;b;c|a;b;c|', obj.splitwithindent)
    
    testLines('a', 'a', obj.joinwithoutindentadddelim)
    testLines('  a', '  a', obj.joinwithoutindentadddelim)
    testLines('a; b; c', 'a|b|c', obj.joinwithoutindentadddelim)
    testLines('  a; b; c', '  a|b|c', obj.joinwithoutindentadddelim)
    testLines('  a; b; c', '  a|  b|  c', obj.joinwithoutindentadddelim)
    testLines('  a; b; c', '  a  |  b  |  c  ', obj.joinwithoutindentadddelim)
    
    
