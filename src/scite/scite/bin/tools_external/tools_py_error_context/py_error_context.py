# print_error_context - Quick and dirty debugging. Usage: py_error_context.py {nameofscript}
# Runs a Python script, displaying local variables on error. 
# Intended for SciTE code editor. (Looks better in Python 2.4 and above)
# Inspired by http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52215 (pydebug.py)
# Made hacktastic by Ben Fisher in 2007

# To set a debug breakpoint, put the statement DEBUG in your code
# This will trigger an error, and py_error_context will recognize it.
# By default, this script displays results **IN OPPOSITE ORDER** from the typical traceback.
# This is because, when debugging, it is more useful to see the locals of the inner function,
# and so I display them first. This can be changed by altering the revstack variable.

# Parameters:
# revstack - reverse order so that inner function is shown first
# ignoreduplicates -  Showing duplicates is useful when you are using recursion, but not useful when you have many global variables
# ignorelist - things that will not be shown
# By default, modules and functions are ignored. This can be changed easily by modifying the line at "if key not in ignorelist ... "

import os
import sys
import traceback
import pprint
import runpy

revstack = True
ignoreduplicates = True
ignorelist = ['__name__', '__doc__', '__file__', '__package__']

def print_exc_vars():
    printer = pprint.PrettyPrinter()
    tb = sys.exc_info()[2]
    stack = []
    while tb:
        stack.append(tb.tb_frame)
        tb = tb.tb_next
    
    try:
        #Python 2.4 or above
        atrace = traceback.format_exc().split('\n  File')
        if atrace[-1].find('DEBUG') == -1:
            print("\n  File " + str(atrace[-1]).strip())
        else:
            print("\n  File " + str(atrace[-1].split(',')[1]) + ' Breakpoint')
    except:
        traceback.print_exc()
    
    if revstack:
        stack.reverse()
    
    for frame in stack:
        # skip the frame that is py_error_context.py itself, it's not useful to show
        if frame.f_code.co_filename.endswith("py_error_context.py"):
            continue
        
        # skip runpy, it's not useful to show
        if frame.f_code.co_filename.endswith('runpy.py'):
            continue
        
        # skip globals for now. possible future feature would be to show this frame and filter out the builtins.
        if frame.f_code.co_name == ('<module>'):
            continue
        
        print('\n  File "%s", line %s, in %s' % (frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name))
        for key, value in frame.f_locals.items():
            try:
                if key not in ignorelist and str(value).find("<module") == -1 and str(value).find("<function") == -1:
                    print("%s = %s" % (key, printer.pformat(value)))
                    if ignoreduplicates:
                        ignorelist.append(key)
            except:
                # We have to be careful not to cause a new error in our error printer.
                # Calling str() on an unknown object could cause an error we don't want.
                print "<ERROR WHILE PRINTING VALUE>"

def prepare_and_exec(filename):
     # add dir to sys.path
    sys.path.append(os.path.split(filename)[0])
    
    # change cwd
    os.chdir(os.path.split(filename)[0])
    
    # mock sys.argv to make it look like it was the first thing called.
    sys.argv.pop(0)
    
    try:
        runpy.run_path(filename, run_name='__main__')
    except:
        print_exc_vars()

if __name__ == '__main__':
    args = list(sys.argv)
    if len(args)>1:
        if args[1].find('py_error_context.py') != -1:
            print "Cannot use py_error_context on itself :)"
        else:
           prepare_and_exec(args[1])
    else:
        print "Usage: py_error_context.py nameofscript.py"
