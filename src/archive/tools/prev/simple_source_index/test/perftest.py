
import os,sys,shutil,subprocess
import exceptions
join = os.path.join
os.chdir(join('..', 'release'))
g_sExe = 'simple_source_indexing.exe'

class Bucket():
    pass
    
def assertEqual(v, vExpected):
    if v != vExpected:
        print 'Fail: Expected '+str(vExpected) + ' but got '+str(v)
        raise exceptions.RuntimeError, 'stop'
def assertContains(s, subs):
    if subs not in s:
        print 'Fail: "'+str(subs) + '" not found in "'+str(s)+'"'
        raise exceptions.RuntimeError, 'stop'

def main():
    assert os.path.exists(g_sExe)
    if os.path.exists('ssip.db'): os.unlink('ssip.db')
    if os.path.exists('ssip.db'): raise 'need to delete db'
    
    #create a new cfg.
    target = 'ssip.cfg'
    stestdata = os.path.abspath(join('..','test','nocpy_audacity-src-1.2.6','audacity-src-1.2.6'))
    fnew = open(target, 'w')
    fnew.write('\n[main]\n')
    fnew.write('\nsrcdir1=%s'%stestdata)
    fnew.write('\nsrcdir2=')
    fnew.write('\nmin_word_len=5')
    fnew.close()
    tests()

def tests():
    # simple test
    bk = runandprocessresults(['-start'])
    print bk.txt
    

def runandprocessresults(listArgs):
    txt, ret = _runReturnStdout(listArgs)
    print txt
    assertEqual(ret, 0)
    bucket = Bucket()
    assert not txt.startswith('Error:')
    if ('C:\\' in txt):
        bucket.countResults = len(txt.split('C:\\')) - 1
        bucket.txt = txt
    else:
        bucket.countResults = 0
        bucket.txt = ''
    return bucket

def _runReturnStdout(listArgs):
    listArgs = list(listArgs) #copy the list, so we don't modify arg.
    listArgs.insert(0, g_sExe)
    sp = subprocess.Popen(listArgs, shell=False, stdout=subprocess.PIPE)
    text = sp.communicate()[0]
    return text.rstrip(), sp.returncode

main()
