
from SciTEModule import ScConst, ScApp

def OnKey(*args):
    # stop the key f from being seen
    if args[0] == 70:
        print 'swallowed'
        return ScConst.StopEventPropagation()
    elif args[0]==71:
        ScApp.UserStripShow("!'Explanation:'{}(Go)\n'Name:'[Name](OK)(Cancel)")
        ScApp.UserStripSet(4, 'a longer name')
        ScApp.UserStripSetList(1, 'banana\nlemon\norange')
        return ScConst.StopEventPropagation()
    elif args[0]==72:
        ScApp.UserStripShow('')
        return ScConst.StopEventPropagation()

def OnUserStrip(control, event):
    if control == 2 and event == ScConst.stripActionClicked:
        print 'user clicked Go for '
        print ScApp.UserStripGetValue(1)
    #~ else:
        #~ print 'Onstrip %s %d'%(control, event)