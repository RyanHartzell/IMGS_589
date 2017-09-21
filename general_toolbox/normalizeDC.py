from metadataReader import metadataGrabber

def normalizeIntegrationTime(im, filename):

    #gets the metadata for the given filename/image
    metadataDictionary = metadataGrabber(filename)
    #pulls the EXIF:ExposureTime from the metadata dictionary
    exposureTime = metadataDictionary['Exif.Photo.ExposureTime']
    #pulls the EXIF:ISO from the metadata dictionary
    iso = metadataDictionary['Exif.Photo.ISOSpeed']
    #normalizes the image by the exposuretime and the ISO
    normalizedImage = im/float(exposureTime*iso)

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
    
    cv2.imshow('sampleImage', displaySampleImage)
	
    startTime = time.time()
    normalizedImage = normalizeIntegrationTime(sampleImage, sampleFileName)
    print("Elapsed Time = {0} [s]".format(time.time()-startTime))
    print("The image's integration time was {0} [s]".format(sampleImage[0][0]/
		    					normalizedImage[0][0]))
	
    displayNormalizedImage = cv2.resize(normalizedImage, None, 
				    fx=.5, fy=.5,interpolation=cv2.INTER_AREA)
    cv2.imshow('normalizedImage', 
                displayNormalizedImage.astype(sampleImage.dtype))

    action = ipcv.flush()
