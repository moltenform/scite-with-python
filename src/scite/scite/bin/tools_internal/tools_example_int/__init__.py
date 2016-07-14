
class State(object):
    def __init__(self):
        print 'new State'
        self.currentFilename = 'not set'

def OnOpen(filename):
    print 'plugin saw OnOpen', filename
    state.currentFilename = filename

def OnSwitchFile(filename):
    print 'plugin saw OnSwitchFile', filename
    state.currentFilename = filename

def OnClose(filename):
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
