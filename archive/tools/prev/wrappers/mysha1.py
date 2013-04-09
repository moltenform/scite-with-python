#Ben Fisher, GPL
#halfhourhacks.blogspot.com
#This program is distributed in the hope that it will be useful, 
#but without any warranty.

import hashlib

def gethash(file):
    if False:
        print('md5')
        objHash = hashlib.md5()
    else:
        print('sha1')
        objHash = hashlib.sha1()

    f=open(file,'rb')
    while 1:
        buf = f.read(4096)
        if not buf : break
        objHash.update(hashlib.sha1(buf).hexdigest())

    f.close()
    print(objHash.hexdigest())
    
if __name__=='__main__':
    import os, sys
    for arg in sys.argv[1:]:
        print(arg)
        gethash(arg)
    
    os.system('pause')
