
debugTracing = False

def OnOpen(filename):
    if debugTracing:
        print 'plugin saw OnOpen', filename

def OnFileChange():
    if debugTracing:
        print('plugin saw OnFileChange')

def OnClose(filename):
    if debugTracing:
        print('plugin saw OnClose' + filename)

def CallSubmodule():
    import ExampleSubmodule
    ExampleSubmodule.CallSubmodule()

def OnKey(*args):
    import ExampleSubmodule
    return ExampleSubmodule.OnKey(*args)

def OnUserStrip(*args):
    import ExampleSubmodule
    return ExampleSubmodule.OnUserStrip(*args)

print('Loading the module. Expect to see this message only once.')
