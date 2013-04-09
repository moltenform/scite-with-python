# Python printval, by Ben Fisher
# halfhourhacks.blogspot.com
import inspect, itertools
from filesystem import *
class PythonPrintVal(object):
    def _output(self, name, val):
        # expands a struct to one level.
        print('printval| '+name+' is '+repr(val))
        if name=='locals()':
            for key in val:
                if not key.startswith('_'):
                    self._output(key, val[key])
        elif ' object at 0x' in repr(val):
            for propname in dir(val):
                if not propname.startswith('_'):
                    sval = repr(val.__getattribute__(propname))
                    print(' \t\t.'+propname+'  =  '+sval)

    def __or__(self, val):
        # look in the source code for the text
        fback = inspect.currentframe().f_back
        try:
            with open(fback.f_code.co_filename, 'r') as srcfile:
                line = next(itertools.islice(srcfile, fback.f_lineno-1, fback.f_lineno))
                self._output(line.replace('printval|','',1).strip(), val)
        except (StopIteration, IOError):
            return self._output('?',val)

printval = PythonPrintVal()

if __name__=='__main__':
    def examples():
        print getClipboardText()
        a=4
        b=5
        printval| a
        printval| b
        printval| a*b
        printval| a*b + (a+b+6*a)
        
        class Foo(object):
            fld1='a'
            fld2=42
        obj = Foo()
        printval| obj
        
        class FooSub(Foo):
            fld3='at'
        obj = FooSub()
        printval| obj
        
        # we don't support looking up source here, but fail gracefully
        exec 'printval| 2*a*b'
        # prints "printval.? is 40"
                
        print '\n\n  now print all the locals:\n\n'
        printval| locals()
    
    examples()
    
    