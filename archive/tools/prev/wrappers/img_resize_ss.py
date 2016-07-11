#resize_ss
#Ben Fisher, GPL
#halfhourhacks.blogspot.com
#This program is distributed in the hope that it will be useful, 
#but without any warranty.

# Say you have a directory of photos that you'd like to be resized.
# if you want photo1.jpg to be resized by 50%, rename it to photo1_ss50.jpg
# if you want photo2.jpg to be resized by 35%, rename it to photo2_ss35.jpg
# then, set strDir below to point at the directory and run this script.


import Image
import os

strDir = r"\path\to\pictures"

outf = '.'
informat = 'jpg'
outformat = 'jpg'
jpgQuality=90
delOriginals = False
astrFiles = os.listdir(strDir)


def main():
    stroutdir = os.path.join(strDir, outf)
    for strFilename in astrFiles:
        if not strFilename.lower().endswith(informat):
            continue
        if not strFilename.lower().endswith(informat): 
            print 'no point here'
            continue
        
        type = None
        if '__ss80.' in strFilename: type='__ss80.'; resizeFactor=0.8
        if '__ss70.' in strFilename: type='__ss70.'; resizeFactor=0.7
        if '__ss60.' in strFilename: type='__ss60.'; resizeFactor=0.6
        if '__ss50.' in strFilename: type='__ss50.'; resizeFactor=0.5
        if '__ss40.' in strFilename: type='__ss40.'; resizeFactor=0.4
        if '__ss35.' in strFilename: type='__ss35.'; resizeFactor=0.35
        if '__ss30.' in strFilename: type='__ss30.'; resizeFactor=0.3
        if '__ss25.' in strFilename: type='__ss25.'; resizeFactor=0.25
        if '__ss20.' in strFilename: type='__ss20.'; resizeFactor=0.2
        if '__ss15.' in strFilename: type='__ss15.'; resizeFactor=0.15
        if type==None: continue
        outname = strDir+'\\'+(strFilename.replace(type,'.'))
        assert not os.path.exists(outname)
        
        try:
            img = Image.open(strDir + '\\' + strFilename)
        except:
            print 'Not an image ',strFilename
            continue
        name, ext = strFilename.rsplit('.',1)
        newname = name + '.' + outformat
        img = resizeTheImg(img, resizeFactor)
        
        if outformat=='jpg':
            img.save(os.path.join(stroutdir, outname), quality=jpgQuality)
        else:
            img.save(os.path.join(stroutdir, outname), optimize=1)
        print newname
        

def resizeTheImg(img, resizeFactor):
    if resizeFactor==None:
        return img
    
    width, height = img.size[0], img.size[1]
    newWidth = int(width*resizeFactor)
    newHeight = int(height*resizeFactor)

    return img.resize((newWidth,newHeight), Image.ANTIALIAS)
    

def getfilesize(fname):
    st = os.stat(fname)
    assert st.st_size > 0
    return st.st_size
    

if __name__=='__main__':
    main()

