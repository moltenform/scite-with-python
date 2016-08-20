# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

def insertsequentialnumbershelp():
    docs = '''Let's say you want to write the sequence
data1 = getData1();
data2 = getData2();
data3 = getData3();

First, write
data@ = getData@();
data@ = getData@();
data@ = getData@();

Then select the text and run insertsequentialnumbers.

Let's say you want to write the sequence
dataRed = getDataRed();
dataGreen = getDataGreen();
dataBlue = getDataBlue();

First, write
data@Red@ = getData@@();
data@Green@ = getData@@();
data@Blue@ = getData@@();
Then select the text and run insertsequentialnumbers.'''
    print(docs)

def insertsequentialnumbers(lines):
    isReplaceWords = any('@@' in line for line in lines)
    if isReplaceWords:
        return atreplacewords(lines)
    else:
        return atreplacenumbers(lines)
            
def atreplacenumbers(lines):
    import sys
    if sys.platform.startswith('win'):
        import wincommondialog
        leadingZeros = wincommondialog.askYesNo('Add leading zeros?')
        
        firstNumber = wincommondialog.askInput(
            'What should the first number in the sequence be?', default='1')
        if not firstNumber:
            return
            
        firstNumber = int(firstNumber)
    else:
        firstNumber = 1
        leadingZeros = False
    return atreplacenumbers_impl(lines, firstNumber, leadingZeros)
    
def atreplacenumbers_impl(lines, firstNumber, leadingZeros):
    currentNumber = firstNumber
    largestNumber = firstNumber + sum(bool('@' in line) for line in lines) - 1
    for i in range(len(lines)):
        if '@' in lines[i]:
            numberAsString = str(currentNumber)
            if leadingZeros:
                numberAsString = numberAsString.zfill(len(str(largestNumber)))
            
            lines[i] = lines[i].replace('@', numberAsString)
            currentNumber += 1

def atreplacewords(lines, silent=False):
    for i in range(len(lines)):
        if '@' in lines[i]:
            ret = atreplacewords_impl(lines[i], silent=silent)
            if ret is None:
                break
            else:
                lines[i] = ret

def atreplacewords_impl(lineOrig, silent):
    # let's say the string is in the form before@value@after
    uniqueMarker = '\x01\x01\x01marker\x01\x01\x01'
    assert uniqueMarker not in lineOrig
    line = lineOrig.replace('@@', uniqueMarker)
    parts = line.split('@')
    if len(parts) != 3:
        if not silent:
            print('Not the right number of @ characters on this line: \n' + lineOrig)
            insertsequentialnumbershelp()
            
        return None
    else:
        before, value, after = parts
        before = before.replace(uniqueMarker, value)
        after = after.replace(uniqueMarker, value)
        return before + value + after
        
if __name__ == '__main__':
    from ben_python_common import assertEq
    
    def testLines(expected, input, fn):
        arr = input.split('|')
        fn(arr)
        assertEq(expected, '|'.join(arr))
    
    # leading zeros disabled and not needed
    input = 'data@ = getData@();|data@ = getData@();|data@ = getData@();'
    expected = 'data1 = getData1();|data2 = getData2();|data3 = getData3();'
    testLines(expected, input, lambda s: atreplacenumbers_impl(s, 1, False))
    
    # leading zeros enabled and not needed
    input = 'data@ = getData@();|data@ = getData@();|data@ = getData@();'
    expected = 'data1 = getData1();|data2 = getData2();|data3 = getData3();'
    testLines(expected, input, lambda s: atreplacenumbers_impl(s, 1, True))
    
    # leading zeros disabled and are needed
    input = 'data@ = getData@();|data@ = getData@();|data@ = getData@();'
    expected = 'data8 = getData8();|data9 = getData9();|data10 = getData10();'
    testLines(expected, input, lambda s: atreplacenumbers_impl(s, 8, False))
    
    # leading zeros enabled and are needed
    input = 'data@ = getData@();|data@ = getData@();|data@ = getData@();'
    expected = 'data08 = getData08();|data09 = getData09();|data10 = getData10();'
    testLines(expected, input, lambda s: atreplacenumbers_impl(s, 8, True))
    
    # leading zeros enabled and, becauase of blank lines, not needed
    input = 'data@ = getData@();|data@ = getData@();|line with no replacements'
    expected = 'data8 = getData8();|data9 = getData9();|line with no replacements'
    testLines(expected, input, lambda s: atreplacenumbers_impl(s, 8, True))
    
    # basic usage
    input = 'data@Red@ = getData@@();|data@G@ = getData@@();|data@Blue@ = getData@@();|n'
    expected = 'dataRed = getDataRed();|dataG = getDataG();|dataBlue = getDataBlue();|n'
    testLines(expected, input, lambda s: atreplacewords(s))
    
    # not enough @ symbols
    input = 'data@Red@ = getData@@();|bad = getData@@();|data@Blue@ = getData@@();'
    expected = 'dataRed = getDataRed();|bad = getData@@();|data@Blue@ = getData@@();'
    testLines(expected, input, lambda s: atreplacewords(s, silent=True))
    
    # not enough @ symbols
    input = 'data@Red@ = getData@@();|bad@ = getData@@();|data@Blue@ = getData@@();'
    expected = 'dataRed = getDataRed();|bad@ = getData@@();|data@Blue@ = getData@@();'
    testLines(expected, input, lambda s: atreplacewords(s, silent=True))
    
    # too many @ symbols
    input = 'data@Red@ = getData@@();|b@a@d@ = getData@@();|data@Blue@ = getData@@();'
    expected = 'dataRed = getDataRed();|b@a@d@ = getData@@();|data@Blue@ = getData@@();'
    testLines(expected, input, lambda s: atreplacewords(s, silent=True))
    
   
    
    
