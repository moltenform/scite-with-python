
useLexersParens = ['cpp', 'python']
useLexersXml = ['xml', 'hypertext']
singletonsXml = ('br', 'img', 'hr', 'meta')
openParen, closeParen = ord('('), ord(')')
openAngle, closeAngle = ord('<'), ord('>')
singleQuote, dblQuote = ord("'"), ord('"')
isRunning = False

stylesSingleQuoteStrings = dict(
    cpp=[7, 71],
    hypertext=[7, 25, 49, 64, 112, 97, 95, 110, 120],
    xml=[7, 25],
    css=[14],
    lua=[7],
    d=[12],
    octave=[5],
    matlab=[5],
    sql=[7],
    perl=[7, 26],
    bash=[6],
    python=[4, 6],
    ruby=[6])

stylesDblQuoteStrings = dict(
    cpp=[6, 13, 20, 21, 22, 70, 77, 84, 85, 86],
    hypertext=[6, 24, 48, 63, 75, 77, 85, 87, 98, 94, 113, 109, 119, 126],
    xml=[6, 24],
    css=[13],
    lisp=[6, 8],
    lua=[6],
    d=[10, 18, 19],
    octave=[8],
    matlab=[8],
    registry=[3, 8, 10],
    sql=[6],
    vb=[4],
    conf=[6],
    perl=[6, 27, 43, 64],
    bash=[5],
    python=[3, 7],
    ruby=[6, 24, 25, 26, 27, 28],
    rust=[13, 14, 21, 22])

stylesUnclosed = dict(cpp=[12, 76],
    lua=[12],
    d=[11],
    lisp=[8],
    python=[13],
    vb=[9])

stylesComments = dict(css=[9],
    cpp=[1, 2, 3, 15, 17, 18, 23, 24, 65, 66, 67, 79, 81, 82, 87, 88, 92, 107, 124],
    html=[9, 20, 29, 42, 43, 44, 57, 58, 59, 72, 82],
    xml=[9, 29],
    lua=[1, 2, 3],
    d=[1, 2, 3, 4, 15, 16, 17],
    octave=[1],
    matlab=[1],
    registry=[1],
    sql=[1, 2, 3, 13, 15, 17, 18],
    perl=[2],
    bash=[2],
    python=[1, 12],
    ruby=[2],
    rust=[1, 2, 3, 4])

def isPythonComment(language, style):
    if language == 'python' and style == 0:
        from scite_extend_ui import ScEditor
        lineText, linePos = ScEditor.GetCurLine()
        if '#' in lineText[0:linePos]:
            return True

def getQuoteReplacement(character, language, style):
    if language == 'null':
        return character if character == dblQuote else None
    
    languageSupportsDblStrings = language in stylesDblQuoteStrings
    languageSupportsSingleStrings = language in stylesSingleQuoteStrings
    isInSingleQuoteString = style in stylesSingleQuoteStrings.get(language, [])
    isInDblQuoteString = style in stylesDblQuoteStrings.get(language, [])
    isInUnclosed = style in stylesUnclosed.get(language, [])
    isInComment = style in stylesComments.get(language, [])
    
    if character == singleQuote:
        if languageSupportsSingleStrings:
            if not (isInSingleQuoteString or isInDblQuoteString or isInUnclosed or isInComment):
                if not isPythonComment(language, style):
                    return singleQuote
    else:
        if languageSupportsDblStrings and not (isInDblQuoteString or isInUnclosed):
            return dblQuote
        
def onTypeQuote(character):
    from scite_extend_ui import ScApp, ScEditor
    if ScApp.GetProperty('auto.close.quotes') == '1':
        style = ScEditor.GetStyleAt(ScEditor.GetCurrentPos())
        replacement = getQuoteReplacement(character, ScEditor.GetLexerLanguage(), style)
        if replacement:
            ScEditor.ReplaceSel(chr(replacement))
            ScEditor.GotoPos(ScEditor.GetCurrentPos() - 1)

def showStyles():
    from scite_extend_ui import ScEditor
    import sys
    currentStyle = -1
    print('\n')
    for i in range(ScEditor.GetLength() - 1):
        byte = ScEditor.GetCharAt(i)
        style = ScEditor.GetStyleAt(i)
        if style != currentStyle:
            sys.stdout.write('(style %d)' % style)
            currentStyle = style
        sys.stdout.write(chr(byte))

def getTextToInsertOnOpenParen(lexerLanguage):
    from scite_extend_ui import ScEditor
    lineText, linePos = ScEditor.GetCurLine()
    
    # if there is a subsequent character and it is not whitespace, do nothing.
    if linePos < len(lineText) and lineText[linePos].strip() and lineText[linePos] not in ',.{:[-*':
        return None
        
    if lexerLanguage == 'python':
        if lineText.startswith('    def ') and ')' not in lineText:
            # because it's indented, this looks like a class method, so let's add the self parameter
            return 'self)'
    
    # otherwise, add a closing paren. might not be needed, but the user can delete in that case.
    return ')'

def onOpenParen(character):
    from scite_extend_ui import ScEditor
    lexerLanguage = ScEditor.GetLexerLanguage()
    if lexerLanguage in useLexersParens:
        replacement = getTextToInsertOnOpenParen(lexerLanguage)
        if replacement:
            ScEditor.ReplaceSel(replacement)
            ScEditor.GotoPos(ScEditor.GetCurrentPos() - 1)

def onCloseTag(character):
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

mapCharToFunction = {closeAngle: onCloseTag, openParen: onOpenParen,
    singleQuote: onTypeQuote, dblQuote: onTypeQuote}

def OnChar(key):
    fn = mapCharToFunction.get(key, None)
    if fn:
        from scite_extend_ui import ScEditor
        global isRunning
        if isRunning:
            # prevent infinite recursion
            print 'stopping because isrunning'
            return
        
        isRunning = True
        try:
            # do not run if there are multiple selections
            if ScEditor.GetFocus() and ScEditor.GetSelections() <= 1:
                fn(key)
        finally:
            isRunning = False

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
    
    

