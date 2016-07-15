
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

def OnKey(*args):
    # stop the key f from being seen
    if args[0] == 70:
        print 'swallowed'
        return ScConst.StopEventPropagation()
    elif args[0]==71:
        toolui = ExampleUI()
        toolui.Show()
        return ScConst.StopEventPropagation()
    elif args[0]==72:
        return ScConst.StopEventPropagation()


