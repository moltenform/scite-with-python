
import os,sys,shutil,subprocess
import exceptions
join = os.path.join
os.chdir(join('..', 'release'))
g_sExe = 'simple_source_indexing.exe'
sfile1  = join('..','test','testdata','folder1','temp.cpp')
sfile2  = join('..','test','testdata','folder1','contrived.cpp')


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
    if os.path.exists(sfile1): os.unlink(sfile1)
    if os.path.exists(sfile1): raise 'need to delete tempfile'
    
    #create a new cfg.
    target = 'ssip.cfg'
    stestdata = os.path.abspath(join('..','test','testdata'))
    fnew = open(target, 'w')
    fnew.write('\n[main]\n')
    fnew.write('\nsrcdir1=%s'%stestdata)
    fnew.write('\nsrcdir2=')
    fnew.close()
    tests()

def tests():
    # simple test
    bk = runandprocessresults(['-start'])
    bk = runandprocessresults(['-s', 'extern'])
    assertEqual(bk.countResults, 1)
    assertContains(bk.txt, 'src2.h:23:extern "C" {')
    
    # search only source files.
    bk = runandprocessresults(['-s', 'notsourcesearch'])
    assertEqual(bk.countResults, 1)
    assertContains(bk.txt, 'src1.c:16: notsourcesearch')
    assert 'notsour.ce' not in bk.txt
    assert 'notsource.c.not' not in bk.txt
    
    # verify results
    bk = runandprocessresults(['-s', 'CAudioData'])
    assertEqual(bk.countResults, 17)
    sresexp=r'folder1\effects.cpp:4:bool effect_checksame(CAudioData* w1, C|folder1\effects.cpp:38:errormsg effect_mix(CAudioData**out, CA|folder1\effects.cpp:40: CAudioData* audio;|folder1\effects.cpp:63:errormsg effect_modulate(CAudioData**ou|folder1\effects.cpp:65: CAudioData* audio;|folder1\effects.cpp:78:errormsg effect_append(CAudioData**out,|folder1\effects.cpp:80: CAudioData* audio;|folder1\effects.cpp:109:errormsg effect_scale_pitch_duration(CAu|folder1\effects.cpp:111: CAudioData* audio;|folder1\effects.cpp:138:errormsg effect_vibrato(CAudioData**out|folder1\effects.cpp:140: CAudioData* audio;|folder1\src1.c:46:errormsg caudiodata_savewavestream(CAudioDa|folder1\src1.c:148:errormsg caudiodata_savewave(CAudioData* t|folder1\src1.c:161:errormsg caudiodata_savewavemem(char** o|folder1\src1.c:193:errormsg caudiodata_loadwavestream(CAudioD|folder1\src1.c:195: CAudioData* audio;|folder1\src1.c:303:errormsg caudiodata_loadwave(CAudioData** '
    sresexp=sresexp.split('|')
    assertEqual(len(sresexp),17)
    for line in sresexp:
        assertContains(bk.txt, line)
    
    bk = runandprocessresults(['-s', 'CAuDioDaTa'])
    assertEqual(bk.countResults, 0)
    
    #only find in files
    bk = runandprocessresults(['-noindex', 'CAudioData'])
    assertEqual(bk.countResults, 17)
    for line in sresexp:
        assertContains(bk.txt, line)
    
    # test blacklisted terms
    bk = runandprocessresults(['-s', 'void'])
    assertEqual(bk.countResults, 0)
    bk = runandprocessresults(['-s', ''])
    assertEqual(bk.countResults, 0)
    bk = runandprocessresults(['-s', 'include'])
    assertEqual(bk.countResults, 0)
    
    # test find-in-files
    bk = runandprocessresults(['-s', 'wantstring'])
    assertEqual(bk.countResults, 6)
    assertContains(bk.txt, 'contrived.cpp:1:') #start of file
    assertContains(bk.txt, 'contrived.cpp:3: bool isFile') #end of line
    assertContains(bk.txt, 'contrived.cpp:12:wantstring') #start of line
    assertContains(bk.txt, 'contrived.cpp:13:wantstring') #don't show same line twice
    assertContains(bk.txt, 'contrived.cpp:16: a wantstring { also twice w') #don't show same line x3
    assertContains(bk.txt, 'contrived.cpp:21:} wantstring') #end of file
    assertEqual( len(bk.txt.split('wantstring'))-1, 9)
    
    # test add new file
    import time; time.sleep(2)
    shutil.copyfile(sfile2, sfile1)
    bk = runandprocessresults(['-s', 'wantstring'])
    assertEqual(bk.countResults, 12)
    assertEqual( len(bk.txt.split('wantstring'))-1, 18)
    
    # test modify file
    os.unlink(sfile1)
    fin = open(sfile2, 'r')
    alltxt = fin.read()
    fin.close()
    ftemp = open(sfile1, 'w')
    ftemp.write(alltxt)
    ftemp.close() #this should update the last mod time
    bk = runandprocessresults(['-s', 'wantstring'])

    assertEqual(bk.countResults, 12)
    assertEqual( len(bk.txt.split('wantstring'))-1, 18)
    bk = runandprocessresults(['-s', 'temp5323'])
    
    # test modify file
    os.unlink(sfile1)
    alltxt = alltxt.replace('wantstring', 'wantstringchanged')
    ftemp = open(sfile1, 'w')
    ftemp.write(alltxt)
    ftemp.close() #this should update the last mod time
    bk = runandprocessresults(['-s', 'wantstring'])
    assertEqual(bk.countResults, 6)
    bk = runandprocessresults(['-s', 'wantstringchanged'])
    assertEqual(bk.countResults, 6)
    bk = runandprocessresults(['-s', 'temp5323'])
    
    # test delete file
    os.unlink(sfile1)
    bk = runandprocessresults(['-s', 'wantstringchanged'])
    assertEqual(bk.countResults, 0 )
    bk = runandprocessresults(['-s', 'wantstring'])
    assertEqual(bk.countResults, 6 )
    

def runandprocessresults(listArgs):
    txt, ret = _runReturnStdout(listArgs)
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
