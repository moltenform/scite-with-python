# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import os
import sys
import codecs

def getRawInput(prompt):
    print(prompt)
    sys.stdout.flush()
    if sys.version_info[0] <= 2:
        return raw_input('')
    else:
        return input('')

def askForCodec(prompt, defaultCodec):
    while True:
        scodec = getRawInput('\n' + prompt).strip()
        if scodec == 'q':
            return None

        try:
            scodec = scodec or defaultCodec
            codecs.lookup(scodec)
            return scodec
        except LookupError:
            print('Could not find this codec (' + scodec + ')')
    
def go(path):
    print('Change encoding.\nChanges the current file,\nit might make sense to keep a backup copy.')
    source = askForCodec('Please type the current encoding and press Enter \n(default=cp1252, q to exit):', 'cp1252')
    if source is None:
        return
        
    dest = askForCodec('Please type the destination encoding and press Enter \n(default=utf-8, q to exit):', 'utf-8')
    if dest is None:
        return
        
    with codecs.open(path, 'rb', source) as fin:
        alltxt = fin.read()
    
    with codecs.open(path, 'wb', dest) as fout:
        fout.write(alltxt)

if __name__ == '__main__':
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        go(sys.argv[1])
