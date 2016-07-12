
#Ben Fisher, GPL
#halfhourhacks.blogspot.com
#This program is distributed in the hope that it will be useful, 
#but without any warranty.

import os,sys
import subprocess

def go(webppath, file):
    newname = file.rsplit('.',1)[0]+'.webp'
    assert file!=newname
    s2 = '"%s" -lossless "%s" -o "%s"'%(webppath, file, newname)
    subprocess.call(s2)
    assert os.path.exists(newname)

if __name__=='__main__':
    webppath = r'C:\Users\diamond\Documents\fisherapps\Imaging\webp\cwebp.exe'
    import os, sys
    for arg in sys.argv[1:]:
        print(arg)
        go(webppath, arg)
    
    os.system('pause')

