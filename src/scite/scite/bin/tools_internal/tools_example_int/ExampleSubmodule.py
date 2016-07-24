
from scite_extend_ui import *

class ExampleUI(ScToolUIBase):
    def AddControls(self):
        self.AddLabel('Explanation')
        self.cmb = self.AddCombo()
        self.btnGo = self.AddButton('Go', callback=self.OnGo)
        self.AddRow()
        self.AddLabel('Name:')
        self.entry = self.AddEntry('default name')
        self.AddButton('OK', callback=self.OnOK, default=True, closes=True)
        self.AddButton('Cancel', closes=True)
        
    def OnOpen(self):
        self.Set(self.entry, 'different default name')
        self.SetList(self.cmb, 'banana\nlemon\norange')
        
    def OnGo(self):
        print 'clicked Go with value %s and %s'%(self.Get(self.cmb), self.Get(self.entry))
        
    def OnOK(self):
        print 'clicked OK with value %s and %s'%(self.Get(self.cmb), self.Get(self.entry))
        
    def OnEvent(self, control, eventType):
        # we wouldn't usually need this method, but just a demo
        if control == self.entry and eventType == ScConst.eventTypeChange:
            print 'entry changed'

def OnKey(key, shift, ctrl, alt):
    # stop the ctrl-w shortcut
    if key == ord('W') and not shift and ctrl and not alt:
        print 'swallowed'
        return ScConst.StopEventPropagation
        
    # have ctrl-alt-shift-w open an example tool ui
    if key == ord('W') and shift and ctrl and alt:
        print 'opening tool ui'
        toolui = ExampleUI()
        toolui.Show()

