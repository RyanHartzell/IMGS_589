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
	maxCount = float(2**bitDepth)-1

	minShutter = 1/(10**6) #1 Microsecond
	minISO = 100

	normalizedImage = image/(exposureTime*iso)
	maxPossibleDC = maxCount/(minISO*minShutter)

	uint16Max = float(2**16)-1

	scalar = uint16Max/maxPossibleDC

	normalizedImage *= scalar

	return normalizedImage

if __name__ == '__main__':
	import ipcv
	import time
	import cv2
	import numpy

	sampleFileDirectory = 	'/dirs/home/faculty/cnspci/micasense/' + \
				'rededge/20170726/0005SET/raw/000'
	sampleFileName = sampleFileDirectory + '/IMG_0000_1.tif'

	sampleImage = cv2.imread(sampleFileName, cv2.IMREAD_UNCHANGED)
	displaySampleImage = cv2.resize(sampleImage, None, fx=.5, fy=.5, 
					interpolation=cv2.INTER_AREA)

	cv2.imshow('sampleImage', ((displaySampleImage/65535)*255).astype('uint8'))
	
	#maxShutter, minShutter, maxISO, minISO = findMaxMinISOShutter(sampleFileDirectory)

	normalizedImage = normalizeISOShutter(sampleImage, sampleFileName)

	displayNormalizedImage = cv2.resize(normalizedImage, None, 
					fx=.5, fy=.5,interpolation=cv2.INTER_AREA)
	cv2.imshow('normalizedImage', 
				((displayNormalizedImage/numpy.max(normalizedImage))*255).astype('uint8'))

	action = ipcv.flush()
