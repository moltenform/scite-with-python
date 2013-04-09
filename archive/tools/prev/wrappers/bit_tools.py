#Bit tools
#Ben Fisher, GPL
#halfhourhacks.blogspot.com
#This program is distributed in the hope that it will be useful, 
#but without any warranty.

import math
def necessarybits(n):
    pw = int( math.log(n)/math.log(2)) + 1
    print ('%d bits are required to store values up to %d'%(pw, n))
    print ('2 ** %d = %d' %( pw, 2**pw))
def tobinary(n, length=8):
    bstr_pos = lambda n: n>0 and bstr_pos(n>>1)+str(n&1) or ''
    s = bstr_pos(n) #source: http://markmail.org/message/caydzqlw7fz22hwe
    while len(s)<length: s= '0'+s
    return s
def frombinary(s):
    return int(s.replace('_',''),2) #allows you to space numbers, like 0011_1100
def pattern(s, asserts=False):
    '''Pass in string like 000rrr00''' #Don't send strings like 00rr00rr, those are incorrect.
    s=s.replace('_','')
    types={8:'unsigned char',16:'unsigned short',32:'unsigned int'}
    type = types.get(len(s),'unknown_int')
    
    seenchars={}
    for chr in s: seenchars[chr]=True
    if len(seenchars)!=2 or '0' not in seenchars: raise 'String must consist of 0s and one other char'
    otherchar = [key for key in seenchars if key!='0'][0]
    start=s.index(otherchar); end=s.rindex(otherchar)
    
    print ('%s is a %dbit number packed into bits %d to %d'%(otherchar,1+end-start,start,end))
    if asserts: print ('assert(%s < %d);'%(otherchar, 2**(len(s.replace('0','')))))
    if start==0: #all we need to do is shift it
        print ('Packing:\n %s packed |= %s<<%d;' %(type,otherchar,len(s)-end - 1))
        print ('Unpacking:\n %s %s = packed>>%d;' %(type,otherchar,len(s)-end - 1))
    elif end==len(s)-1: #all we need to do is mask it
        print ('Packing:\n %s packed |= %s;' %(type,otherchar))
        mask = '0'*start + '1'*(len(s)-start)
        print ('Unpacking:\n %s %s = packed & 0x%x; //packed & 0b%s' %(type,otherchar,int(mask,2),mask))
    else: #need to shift and mask
        print ('Packing:\n %s packed |= %s<<%d;' %(type,otherchar,len(s)-end - 1))
        mask = '0'*start + '1'*(len(s)-start)
        print ('Unpacking:\n %s %s = (packed & 0x%x)>>%d; //packed & 0b%s' %(type,otherchar,int(mask,2),len(s)-end - 1,mask))
        
    

if __name__=='__main__':
    #a few examples:
    necessarybits(640)
    print
    print tobinary(46)
    print
    print frombinary('1100_1100')
    print
    pattern('00rrr000', True)
    print
    pattern('00000bbb')
    