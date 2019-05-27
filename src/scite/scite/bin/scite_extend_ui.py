# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3
# See documentation at https://moltenform.com/page/scite-with-python/doc/writingplugin.html

import SciTEModule
from scite_extend import ScEditor, ScOutput, ScApp, ScConst, OnEvent, findCallbackModule, RequestThatEventContinuesToPropagate

class ScToolUIManagerClass(object):
    '''
    This class manages the current user strip, and also guards calls to UserStripSet
    so that only the active UI object can get/set data from the UI.
    '''
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
        # ensure that OnUserStrip events are passed to us
        if toolUI:
            ScApp.EnableNotification('OnUserStrip')
        
        # show the ui
        SciTEModule.app_UserStripShow(toolUI.spec if toolUI else '')
        self.currentUserStrip = toolUI
    
    def EnsureActive(self, toolUI):
        if self.currentUserStrip != toolUI:
            raise RuntimeError('the UI object %s is no longer active' % toolUI)

class ScToolUIBase(object):
    '''
    A class to help build a UserStrip user interface and conveniently invoke callbacks.
    Inherit from this class to use it, see ScAskUserChoiceClass for an example.
    '''
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
        ScToolUIManager.Show(self)
        self.OnOpen()
        
    def Close(self):
        ScToolUIManager.Show(None)
        
    def AddLabel(self, text):
        return self._add(text, start="'", end="'")
        
    def AddButton(self, text, callback=None, closes=False, default=False):
        start = '((' if default else '('
        end = '))' if default else ')'
        return self._add(text, start=start, end=end, callback=callback, closes=closes)
        
    def AddCombo(self):
        return self._add('', start='{', end='}')
        
    def AddEntry(self, text):
        return self._add(text, start='[', end=']')
        
    def AddRow(self):
        return self._add('\n', start='', end='', noNumber=True)
        
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
        if res == ScConst.StopEventPropagation:
            return None
        
        if eventType == ScConst.eventTypeClicked:
            callback, closes = self.callbackOnClick.get(control, (None, None))
            if callback:
                callback()
            if closes:
                self.Close()
    
    def Get(self, *args, **kwargs):
        return ScToolUIManager.UserStripGetValue(self, *args, **kwargs)
    
    def Set(self, *args, **kwargs):
        return ScToolUIManager.UserStripSet(self, *args, **kwargs)
        
    def SetList(self, *args, **kwargs):
        return ScToolUIManager.UserStripSetList(self, *args, **kwargs)
    
    # for the implementation class to override
    def AddControls(self):
        raise NotImplementedError()
        
    def OnOpen(self):
        raise NotImplementedError()
        
    def OnEvent(self, control, eventType):
        pass

class ScAskUserInputBase(ScToolUIBase):
    '''
    Asks the user to enter some text.
    '''
    def __init__(self, callback, label, default='', leaveOpen=False):
        self.callback = callback
        self.label = label
        self.default = default
        self.leaveOpen = leaveOpen
        super(ScAskUserInputBase, self).__init__()
    
    def AddControls(self):
        self.AddLabel(self.label)
        self.cmb = self.AddCombo()
        if self.leaveOpen:
            self.AddButton('Run', self.OnRun, closes=False, default=True)
            self.AddButton('Close', closes=True)
        else:
            self.AddButton('OK', self.OnRun, closes=True, default=True)
            self.AddButton('Cancel', closes=True)

    def OnOpen(self):
        self.Set(self.cmb, self.default)
    
    def OnRun(self):
        textEntered = self.Get(self.cmb)
        self.callback(textEntered)

class ScAskUserInputClass(ScAskUserInputBase):
    '''Currently has identical behavior as ScAskUserInputBase'''
    pass

class ScAskUserChoiceClass(ScAskUserInputBase):
    '''
    Asks the user to choose between some options, using a combo box.
    Provide a list in the form 'choiceID|Shown In UI', and a callback which will be sent choiceID.
    '''
    def __init__(self, choices, callback, label='Please choose:', leaveOpen=False):
        if len(choices) == 0 or '|' not in choices[0]:
            raise ValueError('choices must be a non-empty list of strings')

        self.choiceIDs = [s.split('|')[0] for s in choices]
        self.choiceShown = [s.split('|')[1] for s in choices]
        super(ScAskUserChoiceClass, self).__init__(callback=callback, label=label, leaveOpen=leaveOpen)

    def OnOpen(self):
        # overrides ScAskUserInputBase.OnOpen
        textToSet = '\n'.join(self.choiceShown)
        self.SetList(self.cmb, textToSet)
        self.Set(self.cmb, self.choiceShown[0])
    
    def OnRun(self):
        # overrides ScAskUserInputBase.OnRun
        chosen = self.Get(self.cmb)
        
        try:
            index = self.choiceShown.index(chosen)
        except ValueError:
            print('Not a valid choice, please choose from the list.')
            return
        else:
            self.callback(self.choiceIDs[index])

class ScMultiKeyManagerClass(object):
    activeKeyListener = None
    
    def SetActiveKeyListener(self, listener):
        # ensure that OnKey events are passed to us
        if listener:
            ScApp.EnableNotification('OnKey')
        
        self.activeKeyListener = listener
        
    def OnKey(self, args):
        if self.activeKeyListener:
            return self.activeKeyListener.OnKey(*args)
    
class ScMultiKeyChoiceClass(object):
    '''
    Asks the user to choose between some options, by pressing a key
    (part of a multi-key keyboard shortcut).
    Provide a list in the form 'C|choiceID|Shown In UI', where C is a capitol alphanumeric char,
    and a callback which will be sent choiceID.
    '''
    def __init__(self, choices, callback, showPerforming=True, label='Please choose:'):
        if len(choices) == 0 or '|' not in choices[0]:
            raise ValueError('choices must be a non-empty list of strings')

        self.callback = callback
        self.label = label
        self.showPerforming = showPerforming
        self.choiceKeys = []
        self.choiceIDs = []
        self.choiceShown = []
        self.ValidateAndSetKeys(choices)

    def ValidateAndSetKeys(self, choices):
        assert len(choices) > 0
        seen = dict()
        for choice in choices:
            ch, id, shown = choice.split('|')
            assert len(ch) == 1, 'key must be one character'
            isAlpha = ord('A') <= ord(ch) <= ord('Z')
            isNumeral = ord('0') <= ord(ch) <= ord('9')
            assert isAlpha or isNumeral, 'key must be 0-9 or A-Z'
            assert ch not in seen, 'duplicate character ' + ch
            self.choiceKeys.append(ord(ch))
            self.choiceIDs.append(id)
            self.choiceShown.append(shown)
            
    def Show(self):
        self.linesCountInOutput = ScOutput.GetLineCount()
        self.PrintInstructions()
        ScMultiKeyManager.SetActiveKeyListener(self)
        ScToolUIManager.Show(None) # close any toolui as well
    
    def PrintInstructions(self):
        print('\n\nThis is part of a multi-key combination')
        print(self.label)
        print('Press Esc to cancel')
        for key, text in zip(self.choiceKeys, self.choiceShown):
            print('Press %s to %s' % (chr(key).lower(), text))
    
    def EraseInstructions(self):
        start = ScOutput.PositionFromLine(self.linesCountInOutput)
        end = ScOutput.PositionFromLine(ScOutput.GetLineCount())
        ScOutput.SetSel(start - 1, end)
        ScOutput.ReplaceSel('')
        
    def GetChoiceIDFromKey(self, key):
        import sys
        if not sys.platform.startswith('win'):
            if ord('a') <= key <= ord('z'):
                key = ord(chr(key).upper())
        
        try:
            index = self.choiceKeys.index(key)
        except ValueError:
            return None
        return index
    
    def OnKey(self, key, shift, ctrl, alt):
        escapeKeyCode = 27
        modifierKeys = (16, 17, 18)
        if key and key not in modifierKeys:
            # exit the key-swallowing mode, even if an exception is thrown later
            ScMultiKeyManager.SetActiveKeyListener(None)
            
            try:
                self.EraseInstructions()
                index = None
                
                if not shift and not ctrl and not alt:
                    index = self.GetChoiceIDFromKey(key)
                    
                if index is not None:
                    if self.showPerforming:
                        print('Performing ' + self.choiceShown[index] + '...')
                    self.callback(self.choiceIDs[index])
                    print('Done')
                elif key == escapeKeyCode:
                    print('Canceled.')
                else:
                    print('Not a choice, canceled.')
                    
            except:
                import traceback
                print('Exception thrown in OnKey, %s' % traceback.format_exc())
        
        return ScConst.StopEventPropagation


def ScAskUserInput(*args, **kwargs):
    toolUI = ScAskUserInputClass(*args, **kwargs)
    toolUI.Show()
    
def ScAskUserChoice(*args, **kwargs):
    toolUI = ScAskUserChoiceClass(*args, **kwargs)
    toolUI.Show()

def ScAskUserChoiceByPressingKey(*args, **kwargs):
    multikey = ScMultiKeyChoiceClass(*args, **kwargs)
    multikey.Show()


# create singleton instances
ScToolUIManager = ScToolUIManagerClass()
ScMultiKeyManager = ScMultiKeyManagerClass()
