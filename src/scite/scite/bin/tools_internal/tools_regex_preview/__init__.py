# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

from scite_extend_ui import ScToolUIBase, ScApp, ScEditor, ScConst
from ben_python_common import RecentlyUsedList, Bucket, truncateWithEllipsis
from collections import OrderedDict
import re

flagsList = OrderedDict()
flagsList['default'] = 0
flagsList['re.IGNORECASE'] = re.IGNORECASE
flagsList['re.MULTILINE'] = re.MULTILINE
flagsList['re.DOTALL'] = re.DOTALL
flagsList['re.MULTILINE | re.DOTALL'] = re.MULTILINE | re.DOTALL
flagsList['re.MULTILINE | re.IGNORECASE'] = re.MULTILINE | re.IGNORECASE
flagsList['re.DOTALL | re.IGNORECASE'] = re.DOTALL | re.IGNORECASE
flagsList['re.MULTILINE | re.DOTALL | re.IGNORECASE'] = re.MULTILINE | re.DOTALL | re.IGNORECASE

sessionHistoryQueries = RecentlyUsedList(maxSize=50)

class RegexPreviewTool(ScToolUIBase):
    currentlySettingList = False
    
    def AddControls(self):
        self.AddLabel('Query:')
        self.cmbQuery = self.AddCombo()
        self.AddRow()
        self.AddLabel('Flags:')
        self.cmbFlags = self.AddCombo()
        self.AddRow()
        self.AddLabel('Results:')
        self.lblResults = self.AddLabel('')
        self.AddRow()
        self.AddLabel('Reference:')
        self.AddLabel('re.match(exp, s), re.search(exp, s), ' + 
            're.finditer(exp, s), re.sub(exp, repl, s, count)' + ' ' * 50)
        self.AddButton('Search', callback=self.OnSearch, default=True)
        self.AddButton('Close', callback=self.OnClose, closes=True)
        
    def OnOpen(self):
        queries = sessionHistoryQueries.getList() or ['']
        self.SetList(self.cmbQuery, '\n'.join(queries))
        self.Set(self.cmbQuery, queries[0])
        
        flagsNames = (key for key in flagsList)
        self.SetList(self.cmbFlags, '\n'.join(flagsNames))
        self.Set(self.cmbFlags, 're.IGNORECASE')
        
    def OnSearch(self):
        self.Set(self.lblResults, '')
        sflags = self.Get(self.cmbFlags)
        nflags = flagsList.get(sflags, None)
        if nflags is None:
            print('unrecognized regexp flags, please choose from the list.')
            return
        
        regexString = self.Get(self.cmbQuery)
        if not regexString:
            clearAllHighlights()
            print('no query entered')
            return
        
        try:
            reObj = re.compile(regexString, nflags)
        except re.error:
            print('Could not parse regular expression.')
            return
        
        results = doSearch(reObj)
        self.Set(self.lblResults, results)
        
        # update history but don't update the combobox yet, see OnEvent
        sessionHistoryQueries.add(self.Get(self.cmbQuery))

    def OnClose(self):
        clearAllHighlights()
    
    def OnEvent(self, control, eventType):
        if not self.currentlySettingList and control == self.cmbQuery and \
            eventType == ScConst.eventTypeFocusOut:
            # we would update the combobox in OnSearch, 
            # but that was distracting while typing because it sets the caret position to 0
            # so instead, update the combobox when focus leaves it.
            
            # (use currentlySettingList flag to guard against infinite loop)
            self.currentlySettingList = True
            currentVal = self.Get(self.cmbQuery)
            self.SetList(self.cmbQuery, '\n'.join(sessionHistoryQueries.getList()))
            self.Set(self.cmbQuery, currentVal)
            self.currentlySettingList = False
            

def clearAllHighlights():
    ScEditor.SetIndicatorCurrent(ScConst.INDIC_CONTAINER)
    ScEditor.IndicatorClearRange(0, ScEditor.GetTextLength())

def setOneIndicator(pane, indicatorNumber, indicatorProperties):
    pane.SetIndicStyle(indicatorNumber, indicatorProperties.style)
    pane.SetIndicFore(indicatorNumber, indicatorProperties.colour)
    pane.SetIndicAlpha(indicatorNumber, indicatorProperties.fillAlpha)
    pane.SetIndicOutlineAlpha(indicatorNumber, indicatorProperties.outlineAlpha)
    pane.SetIndicUnder(indicatorNumber, indicatorProperties.under)

def highlightRange(pane, start, length):
    pane.IndicatorFillRange(start, length)

def doSearch(reObj):
    clearAllHighlights()
    
    # emulate logic in MarkAll() to describe the style
    findIndicator = Bucket()
    findIndicator.style = ScConst.INDIC_ROUNDBOX
    findIndicator.colour = 0
    findIndicator.fillAlpha = 30
    findIndicator.outlineAlpha = 50
    findIndicator.under = False
    setOneIndicator(ScEditor, ScConst.INDIC_CONTAINER, findIndicator)
    
    # highlight each match
    alltxt, length = ScEditor.GetText()
    ScEditor.SetIndicatorCurrent(ScConst.INDIC_CONTAINER)
    sfirstgroups = ''
    count = 0
    for match in reObj.finditer(alltxt):
        start, end = match.start(), match.end()
        highlightRange(ScEditor, start, end - start)
        count += 1
        if count == 1:
            # only for the first match, display captured groups (from parens in the expression)
            sfirstgroups = groupsToString(match)

    if sfirstgroups:
        sfirstgroups = 'Groups: '+ sfirstgroups
    return '%d found. %s'%(count, sfirstgroups)

def groupsToString(match):
    # for regular expression debugging it's useful to see the captured groups/submatches.
    # labels use a varying-width font, and window width varies, so this is a rough guess.
    maxlen = 150
    groups = match.groups()
    if len(groups):
        s = repr(list(groups))
        return truncateWithEllipsis(s, maxlen)
    else:
        return ''

def DoRegexPreviewTool():
    # corner cases that were tested: zero-width matches \b and (\b), empty query, invalid query
    toolstripui = RegexPreviewTool()
    toolstripui.Show()


