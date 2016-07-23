#print_error_context.py - Quick and dirty debugging. Usage: print_error_context.py {nameofscript}
#Runs a Python script, displaying local variables on error. 
#Intended for SciTE code editor. (Looks better in Python 2.4 and above)
#Inspired by http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52215 (pydebug.py)
#Made hacktastic by Ben Fisher in 2007

#To set a debug breakpoint, put the statement DEBUG in your code
#This will trigger an error, and print_error_context will recognize it.
#By default, this script displays results **IN OPPOSITE ORDER** from the typical traceback.
#This is because, when debugging, it is more useful to see the locals of the inner function,
#and so I display them first. This can be changed by altering the revstack variable.

#Parameters:
#revstack - reverse order so that inner function is shown first
#ignoreduplicates -  Showing duplicates is useful when you are using recursion, but not useful when you have many global variables
#ignorelist - things that will not be shown
#By default, modules and functions are ignored. This can be changed easily by modifying the line at "if key not in ignorelist ... "


#Note: Placing objects in global scope here will appear in the printout

import sys, traceback

def print_exc_vars():
    ignorelist = ['__name__','__doc__','__file__']
    revstack = False
    ignoreduplicates = True
    
    
    tb = sys.exc_info()[2]
    stack = []
    
    while tb:
        stack.append(tb.tb_frame)
        tb = tb.tb_next
    
    try:
        #Python 2.4 or above
        atrace = traceback.format_exc().split('\n  File')
        if atrace[-1].find('DEBUG')==-1:
            print "Error on line:", atrace[-1], '\n'
        else:
            print "Debugger on:", atrace[-1].split(',')[1], '\n'
    except:
        print "This looks better in Python 2.4 or above."
        traceback.print_exc() #ironically, also prints error from above :)
    
    
    if revstack:
        stack.reverse()
        print "Ignoring duplicates=",ignoreduplicates,", innermost first:"
    else:
        print "Ignoring duplicates=",ignoreduplicates,", innermost last:"
    
    for frame in stack:
        
        #Skip the frame that is print_error_context.py itself - we don't need to show that
        if frame.f_code.co_filename.find("print_error_context.py")!=-1:
            continue
        
        print " %s in %s at line %s" % (frame.f_code.co_name,  frame.f_code.co_filename, frame.f_lineno)
        for key, value in frame.f_locals.items():
            #We have to be careful not to cause a new error in our error printer! Calling str() on an unknown object could cause an error we don't want.
            #Infinite loop == bad
            try:
                if key not in ignorelist and str(value).find("<module")==-1 and str(value).find("<function")==-1:
                    print "%s = " % key,value
                    if ignoreduplicates:
                        ignorelist.append(key)
            except:
                print "<ERROR WHILE PRINTING VALUE>"

if len(sys.argv)>1:
    if sys.argv[1].find('print_error_context.py')!=-1:
        print "Cannot use print_error_context on itself :)"
    else:
        try:
            execfile(sys.argv[1])
        except:
            print_exc_vars()
else:
    print "Usage: print_error_context.py nameofscript.py"