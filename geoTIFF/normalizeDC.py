
def normalizeISOShutter(image, filename):
    from metadataReader import metadataGrabber

    #gets the metadata for the given filename/image
    metadataDictionary = metadataGrabber(filename)
    #pulls the EXIF:ExposureTime from the metadata dictionary
    exposureTime = metadataDictionary['Exif.Photo.ExposureTime']
    #pulls the EXIF:ISO from the metadata dictionary
    iso = metadataDictionary['Exif.Photo.ISOSpeed']
    #normalizes the image by the exposuretime and the ISO
    bitDepth = metadataDictionary['Exif.Image.BitsPerSample']
    maxCount = float(2**bitDepth)

    #floatIm = image/maxCount
    #normalizedImage = floatIm/float(exposureTime*iso)
    #print(exposureTime)
    #print(iso)
    #print(exposureTime*iso)
    normalizedImage = image/float(exposureTime*iso*maxCount)
    #normalizedImage = normalizedImage/maxCount

    return normalizedImage

if __name__ == '__main__':
    import ipcv
    import time
    import cv2

    sampleFileDirectory = 	'/dirs/home/faculty/cnspci/micasense/' + \
				'rededge/20170726/0005SET/raw/000/'
    sampleFileName = sampleFileDirectory + 'IMG_0000_1.tif'

    sampleImage = cv2.imread(sampleFileName, cv2.IMREAD_UNCHANGED)
    displaySampleImage = cv2.resize(sampleImage, None, fx=.5, fy=.5, 
				    interpolation=cv2.INTER_AREA)

    cv2.imshow('sampleImage', ((displaySampleImage/65536)*255).astype('uint8'))
	
    normalizedImage = normalizeISOShutter(sampleImage, sampleFileName)
	
    displayNormalizedImage = cv2.resize(normalizedImage, None, 
				    fx=.5, fy=.5,interpolation=cv2.INTER_AREA)
    cv2.imshow('normalizedImage', 
                (displayNormalizedImage*255).astype('uint8'))

    action = ipcv.flush()
