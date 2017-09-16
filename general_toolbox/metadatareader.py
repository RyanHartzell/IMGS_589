'https://git.gnome.org/browse/gexiv2/tree/GExiv2.py'

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

def metadatagrabber(filename):
    sampleimage = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'

    imagemetadata = GExiv2.Metadata(sampleimage)

    taglist = imagemetadata.get_tags()

    indexlist = (0,3,5,17,18,19,20,27,33,37,38,39,41,42,43,46,47,48,49,50,51,52,53,54,56)
    metadatadict = {}

    for index in indexlist:
        specification = taglist[index]
        entry = imagemetadata.get(specification)

        #Single Fractions to Float Case
        if index in ( 0,37,38,39,41,42):
            split = entry.index('/')
            entry = float(entry[:split])/float(entry[split+1:])

        #Three Fractions to Floats Case for GPS Coordinates
        elif index in (3,5):
            firstsplit = entry.index('/')
            secondsplit = entry.index('/',firstsplit+1)
            thirdsplit = entry.index('/',secondsplit+1)
            firstspace = entry.index(' ')
            secondspace = entry.index(' ',firstspace+1)

            divisor = float(entry[firstsplit+1:firstspace])
            degrees = float(entry[:firstsplit])/divisor
            minutes = float(entry[firstspace+1:secondsplit])/divisor
            seconds = float(entry[secondspace+1:thirdsplit])/divisor

            entry = (degrees,minutes,seconds)

        #String to string case for names,date,time
        elif index in (19,20,33,46):
            pass

        #All other cases, no integers used for ease later
        else:
            entry = float(entry)

        metadatadict[specification] = entry
    return(metadatadict)
    
if __name__ == '__main__':
    import metadatareader
    filename = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'
    metadatadict = metadatareader.metadatagrabber(filename)
    print(metadatadict)

