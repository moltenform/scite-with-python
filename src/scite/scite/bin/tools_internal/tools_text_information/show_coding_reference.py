# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

class ShowCodingReference(object):
    def go(self):
        from scite_extend_ui import ScAskUserChoiceByPressingKey
        self.choices = ['G|searchweb|Google selection',
            'C|colorpicker|Show rgb color picker',
            'A|ascii|Show table of ascii codes',
            'H|hexeditor|Edit this file in hex editor']
        label = 'Please choose:'
        ScAskUserChoiceByPressingKey(
            choices=self.choices, label=label, callback=self.onChoiceMade)
    
    def onChoiceMade(self, choice):
        # look for a method named choice, and call it
        assert choice in [s.split('|')[1] for s in self.choices]
        method = self.__getattribute__(choice)
        method()

    def searchweb(self):
        from scite_extend_ui import ScApp
        from ben_python_common import files
        selected = ScApp.GetProperty('CurrentSelection')
        if selected:
            files.openUrl('http://google.com/search?q=' + selected)
        else:
            print('Nothing is selected.')
            
    def colorpicker(self):
        import sys
        if sys.platform.startswith('win'):
            import wincommondialog
            color = wincommondialog.askColor()
            if color:
                print('RGB')
                print(color)
                print(getHexColor(color[0], color[1], color[2]))
        else:
            print('Currently only supported on windows')
    
    def ascii(self):
        specialChars = {0: "(Nul)", 9: "(Tab)", 10: "(\\n Newline)",
            13: "(\\r Return)", 32: "(Space)"}
            
        for i in range(128):
            c = specialChars.get(i, chr(i))
            print('0x%02x\t%d\t%s' % (i, i, c))
    
    def hexeditor(self):
        from scite_extend_ui import ScApp
        from ben_python_common import files
        currentFile = ScApp.GetFilePath()
        propname = 'customcommand.open_in_hex_editor.binary'
        binaryPath = ScApp.GetProperty(propname)
        if not files.isfile(binaryPath):
            doc = '''Could not find the hex editor at
%s,
Please open
%s/tools_internal/tools_text_information/register.properties

and edit the line
%s
to point to the right path.'''
            print(doc % (binaryPath, ScApp.GetSciteDirectory(), propname))
        else:
            args = [binaryPath, currentFile]
            files.run(args, createNoWindow=False, captureoutput=False,
                wait=False, throwOnFailure=None)
    
    
def getHexColor(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)

def DoShowCodingReference():
    ShowCodingReference().go()
                
if __name__ == '__main__':
    from ben_python_common import assertEq
    
    assertEq('#ff0102', getHexColor(255, 1, 2))
    assertEq('#0102ff', getHexColor(1, 2, 255))
