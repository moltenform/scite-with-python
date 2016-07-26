
useLexersParens = ['cpp', 'python']
useLexersXml = ['xml','hypertext']
singletonsXml = ('br', 'img', 'hr', 'meta')
openParen, closeParen = ord('('), ord(')')
openAngle, closeAngle = ord('<'), ord('>')

def onCloseTag():
    from scite_extend_ui import ScEditor, ScOutput, ScApp
    lexerLanguage = ScEditor.GetLexerLanguage()

def getTextToInsertOnOpenParen(lexerLanguage):
    from scite_extend_ui import ScEditor
    lineText, linePos = ScEditor.GetCurLine()
    
    # if there is a subsequent character and it is not whitespace, do nothing.
    if linePos < len(lineText) and lineText[linePos].strip():
        return None
        
    if lexerLanguage == 'python':
        if lineText.startswith('    def ') and not ')' in lineText:
            # because it's indented, this looks like a class method, so let's add the self parameter
            return 'self)'
    
    # otherwise, add a closing paren. might not be needed, but the user can delete in that case.
    return ')'

def onOpenParen():
    from scite_extend_ui import ScEditor
    lexerLanguage = ScEditor.GetLexerLanguage()
    if lexerLanguage in useLexersParens:
        replacement = getTextToInsertOnOpenParen(lexerLanguage)
        if replacement:
            ScEditor.ReplaceSel(replacement)
            ScEditor.GotoPos(ScEditor.GetCurrentPos() - 1)

def onCloseTag():
    from scite_extend_ui import ScEditor
    lexerLanguage = ScEditor.GetLexerLanguage()
    if lexerLanguage in useLexersXml:
        lineText, linePos = ScEditor.GetCurLine()
        insert = getTextToInsertOnCloseTag(lexerLanguage, lineText, linePos)
        if insert == '/>':
            prevpos = ScEditor.GetCurrentPos()
            ScEditor.PaneRemoveText(prevpos - 1, prevpos)
            ScEditor.ReplaceSel(' />')
        elif insert:
            prevpos = ScEditor.GetCurrentPos()
            ScEditor.ReplaceSel('</' + insert + '>')
            ScEditor.GotoPos(prevpos)
            
def getTextToInsertOnCloseTag(lexerLanguage, lineText, linePos):
    # go back to the nearest < character
    i = linePos - 1
    posAlphaSeen = 0
    while i >= 0 and lineText[i] != '<':
        if lineText[i] == '>' and i != linePos - 1:
            # there's already a closing tag and it's not the one we just typed... exit
            return None
        i -= 1

    if i == -1:
        # didn't find an opening tag name, not much we can do
        return None
    
    # now let's take the next sequence of alphabetical characters, i.e. the tag name
    tagName = ''
    while lineText[i + 1].isalpha():
        tagName += lineText[i + 1]
        i += 1
    
    if not tagName:
        # no tag name, could be a closing </element> that begins with no alpha chars.
        return None
    
    if tagName in singletonsXml:
        if lineText[linePos - 2] == '/':
            # it already has the /> ending.
            return None
        else:
            return '/>'
    else:
        return tagName

def OnChar(key):
    if key == closeAngle:
        return onCloseTag()
    elif key == openParen:
        return onOpenParen()

if __name__ == '__main__':
    from ben_python_common import assertEq
    
    # a helper so that you can use the | character to indicate caret position
    def testGetTextToInsertOnCloseTag(expected, input):
        before, after = input.split('|')
        lineText = before + after
        linePos = len(before)
        assertEq(expected,
            getTextToInsertOnCloseTag('', lineText, linePos))
        assertEq(expected,
            getTextToInsertOnCloseTag('', lineText + 'textafter', linePos))
        assertEq(expected,
            getTextToInsertOnCloseTag('', 'textbefore' + lineText, linePos + len('textbefore')))
        
    testGetTextToInsertOnCloseTag('html', '<html>|')
    testGetTextToInsertOnCloseTag('html', 'abc<html>|')
    testGetTextToInsertOnCloseTag('html', '<tag></tag><html>|')
    testGetTextToInsertOnCloseTag('html', '<br /><html>|')
    testGetTextToInsertOnCloseTag('a', 'b<a href>|')
    testGetTextToInsertOnCloseTag('a', 'b<a href="text">|')
    testGetTextToInsertOnCloseTag('a', 'b<a href="text" foo="bar">|')
    testGetTextToInsertOnCloseTag(None, 'a>|')
    testGetTextToInsertOnCloseTag(None, 'a href>|')
    testGetTextToInsertOnCloseTag(None, 'a href="text">|')
    testGetTextToInsertOnCloseTag(None, '<html>a href="text">|')
    testGetTextToInsertOnCloseTag(None, '>a href="text">|')
    testGetTextToInsertOnCloseTag(None, '>a>|')
    testGetTextToInsertOnCloseTag(None, '>>|')
    testGetTextToInsertOnCloseTag(None, '<>|')
    testGetTextToInsertOnCloseTag(None, '<4>|')
    testGetTextToInsertOnCloseTag(None, '< tag>|')
    testGetTextToInsertOnCloseTag(None, '<4tag>|')
    testGetTextToInsertOnCloseTag(None, '<? tag>|')
    testGetTextToInsertOnCloseTag(None, '<% tag>|')
    testGetTextToInsertOnCloseTag(None, '<//tag>|')
    testGetTextToInsertOnCloseTag(None, '</tag>|')
    testGetTextToInsertOnCloseTag('/>', '<br>|')
    testGetTextToInsertOnCloseTag('/>', '<img src>|')
    testGetTextToInsertOnCloseTag('/>', '<img src="test">|')
    testGetTextToInsertOnCloseTag('/>', '<br >|')
    testGetTextToInsertOnCloseTag('/>', '<br  >|')
    testGetTextToInsertOnCloseTag('brr', '<brr >|')
    testGetTextToInsertOnCloseTag('b', '<b >|')
    testGetTextToInsertOnCloseTag('b', '<b / >|')
    testGetTextToInsertOnCloseTag(None, '<br/>|')
    testGetTextToInsertOnCloseTag(None, '<br />|')
    testGetTextToInsertOnCloseTag(None, '<img src />|')
    testGetTextToInsertOnCloseTag(None, '<img src="test" />|')
    
    

