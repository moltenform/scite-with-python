# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from ben_python_common import files, assertEq

def escapeChar(c):
    return '&#x%x;' % ord(c)

def escapeAllText(s):
    # only escaping & < > " ' / would probably be sufficient, but let's escape everything.
    return ''.join((escapeChar(c) for c in s))

def getWritablePath():
    import tempfile
    return files.join(tempfile.gettempdir(), 'tools_spelling_in_web_browser.html')

def SpellingInWebBrowser():
    from scite_extend_ui import ScEditor, ScApp
    selected = ScEditor.GetSelectedText()
    if not selected:
        print('Nothing is selected.')
        return
    
    escaped = escapeAllText(selected)
    templateDir = files.join(ScApp.GetSciteDirectory(), 'tools_internal', 'tools_spelling_in_web_browser')
    templatePathIn = files.join(templateDir, 'template.html')
    templatePathOut = getWritablePath()
    
    if not files.exists(templatePathIn):
        print('Could not find template. Expected file at %s' % templateDir)
        return
    
    template = files.readall(templatePathIn)
    template = template.replace('%TEXT%', escaped)
    
    try:
        files.writeall(templatePathOut, template)
    except IOError:
        print('Could not write to file %s.' % templatePathOut)
        return
    
    import webbrowser
    webbrowser.open(templatePathOut, new=2)

if __name__ == '__main__':
    
    assertEq('', escapeAllText(''))
    assertEq('&#x27;', escapeAllText("'"))
    assertEq('&#xf0;', escapeAllText("\xf0"))
    assertEq('&#x27;&#x27;&#x27;&#x2f;&#x27;&#x27;&#x27;',
        escapeAllText("'''/'''"))
