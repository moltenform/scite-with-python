
import SciTEModule

class ScToolUIManager(object):
    currentUserStrip = None
    
    def UserStripSet(self, toolUI, control, value):
        self.EnsureActive(toolUI)
        return SciTEModule.app_UserStripSet(control, value)
        
    def UserStripSetList(self, toolUI, control, value):
        self.EnsureActive(toolUI)
        return SciTEModule.app_UserStripSetList(control, value)
        
    def UserStripGetValue(self, toolUI, control):
        self.EnsureActive(toolUI)
        return SciTEModule.app_UserStripGetValue(control)
    
    def OnUserStrip(self, control, eventType):
        if self.currentUserStrip:
            self.currentUserStrip.OnRawEvent(control, eventType)
            
    def Show(self, toolUI):
        SciTEModule.app_UserStripShow(toolUI.spec if toolUI else '')
        self.currentUserStrip = toolUI
    
    def EnsureActive(self, toolUI):
        if self.currentUserStrip != toolUI:
            raise RuntimeError('the UI object %s is no longer active' % toolUI)

class ScToolUIBase(object):
    def __init__(self):
        self.spec = ''
        self.currentNumber = 0
        self.currentlyBuilding = True
        self.callbackOnClick = {}
        self.AddControls()
        self.currentlyBuilding = False
        
        # doesn't support adding a close icon in the corner
        # because we want to know when the user strip is active
        
    def Show(self):
        SciTEModule.ScToolUIManager.Show(self)
        self.OnOpen()
        
    def Close(self):
        SciTEModule.ScToolUIManager.Show(None)
        
    def AddLabel(self, text):
        return self._add(text, start="'", end="'")
        
    def AddButton(self, text, callback=None, closes=False, default=False):
        start = '((' if default else '('
        end = '))' if default else ')'
        return self._add(text, start=start, end=end, callback=callback, closes=closes)
        
    def AddCombo(self):
        return self._add('', start="{", end="}")
        
    def AddEntry(self, text):
        return self._add(text, start="[", end="]")
        
    def AddRow(self):
        return self._add('\n', start="", end="", noNumber=True)
        
    def _add(self, text, start, end, callback=None, closes=False, noNumber=False):
        assert self.currentlyBuilding, 'Controls can only be added within AddControls().'
        self.spec += start + text + end
        
        self.callbackOnClick[self.currentNumber] = (callback, closes)
        ret = self.currentNumber
        if not noNumber:
            self.currentNumber += 1
        return ret
    
    def OnRawEvent(self, control, eventType):
        # if the implementation class wants, it can see the raw event too
        res = self.OnEvent(control, eventType)
        if res == SciTEModule.ScConst.StopEventPropagation():
            return None
        
        if eventType == SciTEModule.ScConst.eventTypeClicked:
            callback, closes = self.callbackOnClick.get(control, (None, None))
            if callback:
                callback()
            if closes:
                self.Close()
    
    def Get(self, *args):
        return SciTEModule.ScToolUIManager.UserStripGetValue(self, *args)
    
    def Set(self, *args):
        return SciTEModule.ScToolUIManager.UserStripSet(self, *args)
        
    def SetList(self, *args):
        return SciTEModule.ScToolUIManager.UserStripSetList(self, *args)
    
    # for the implementation class to override
    def AddControls(self):
        raise NotImplementedError()
        
    def OnOpen(self):
        raise NotImplementedError()
        
    def OnEvent(self, control, eventType):
        pass

