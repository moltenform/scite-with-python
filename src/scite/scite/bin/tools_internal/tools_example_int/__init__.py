
debugTracing = False

class State(object):
    def __init__(self):
        if debugTracing:
            print 'new State'
        self.currentFilename = 'not set'

def OnOpen(filename):
    if debugTracing:
        print 'plugin saw OnOpen', filename
    state.currentFilename = filename

def OnSwitchFile(filename):
    if debugTracing:
        print 'plugin saw OnSwitchFile', filename
    state.currentFilename = filename

def OnClose(filename):
    if debugTracing:
        print 'plugin saw OnClose', filename

def PrintCurrent():
    print 'plugin says that the current filename is %s' % (state.currentFilename)

def OnKey(*args):
    import ExampleSubmodule
    return ExampleSubmodule.OnKey(*args)

def OnUserStrip(*args):
    import ExampleSubmodule
    return ExampleSubmodule.OnUserStrip(*args)

state = State()
