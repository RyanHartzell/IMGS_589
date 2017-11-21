"""
title::
	Using gradients to locate calibration panels

description::
	Tracks the shape of a calibration panel using gradients.
	Technique using 'cv2.findContours', based off of 'Topological structural analysis of digitized binary images by border following' paper.

	Suzuki, Satoshi. "Topological structural analysis of digitized binary images by border following." 
		Computer vision, graphics, and image processing 30.1 (1985): 32-46.

author::
	Ryan Connal

Reference::
	Geoffrey Sasaki - showGeoTIFF.py
	Kevin Kha - metadataReader.py

copyright::
	Copyright (C) 2017, Rochester Institute of Technology

"""



def mica2BGR(imagePath):
	#imagePath, (str) leads to directory where the imagery is stored
	#read in the image (registered, so 5 stacked images), then convert to BGR stack
	from osgeo import gdal
	import numpy as np

	ds = gdal.Open(imagePath).ReadAsArray()
	ds = np.moveaxis(ds, 0, -1)

	if len(ds.shape) == 2:
		displayImage = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)#.astype(np.uint8)
		#print(displayImage.shape)
	elif len(ds.shape) == 3:
		band1 = ds[:,:,0]
		band2 = ds[:,:,1]
		band3 = ds[:,:,2]
		band4 = ds[:,:,3]
		band5 = ds[:,:,4]
		displayImage = np.dstack((band1,band2,band3)).astype(np.uint8)
	return displayImage


def imageNadir(displayImage, cropProportion):
	#displayImage, (array), image containing the target
	#cropProportion, (float), decimal (percentage) of the image to utilize
	##obtain portion of image to crop for NADIR view
	import numpy as np
	import cv2

	##calculate midpoint in this image
	imShape = (displayImage).shape
	imHeight = int(imShape[0])
	imWidth = int(imShape[1])

	topLeft = np.array([0, 0])
	bottomRight = np.array([imHeight-1, imWidth-1])
	bottomLeft = np.array([imHeight-1, 0])
	topRight = np.array([0, imWidth-1])
	middleCoord = (topLeft + bottomRight) // 2

	## scale the image with respect to the center and 'cropProportion'
	scale_factor = 1.0 - cropProportion

	topLeft_enc = np.round((topLeft + (scale_factor*(middleCoord - topLeft)))).astype(np.int64)
	topRight_enc = np.round((topRight + (scale_factor*(middleCoord - topRight)))).astype(np.int64)
	bottomLeft_enc = np.round((bottomLeft + (scale_factor*(middleCoord - bottomLeft)))).astype(np.int64)
	bottomRight_enc = np.round((bottomRight + (scale_factor*(middleCoord - bottomRight)))).astype(np.int64)

	#use these coordinates to crop the image
	cropCoords = (bottomRight_enc, bottomLeft_enc, topLeft_enc, topRight_enc) #for each of these coordinate pairs, x, y is [1], [0]
	croppedIm = displayImage[(topLeft_enc[1]):(bottomRight_enc[1]), (topLeft_enc[0]):(bottomRight_enc[0])]

	return croppedIm





def metadataGrabber(filename):
	#sampleimage = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'
	import gi
	gi.require_version('GExiv2', '0.10')
	from gi.repository import GExiv2

	imagemetadata = GExiv2.Metadata(filename)

	taglist = imagemetadata.get_tags()
	#print(taglist[11])

	indexlist = (0,3,5,11,14,17,18,19,20,27,33,34,35,36,37,38,39,41,42,43,45,46,47,48,49,50,51,52,53,54,56,69)
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
		elif index in (14,19,20,33,34,35,45,46,69):
			pass

		#All other cases, no integers used for ease later
		else:
			entry = float(entry)

		metadatadict[specification] = entry
	return metadatadict





def locateContours(displayImage, threshold_value, maxVal):
	#displayImage, (array), image containing the target
	import numpy as np
	import cv2
	
	##convert to grayscale, which is required for thresholding
	if len(displayImage.shape) == 3:
		displayImage_G = cv2.cvtColor(displayImage, cv2.COLOR_BGR2GRAY) #grayscale copy
	elif len(displayImage.shape) == 2:
		displayImage_G = displayImage.astype(np.float32)

	##thresholding to indicate the edges in the scene
	ret, thresholdedIm = cv2.threshold(displayImage_G, threshold_value, maxVal, 0) #thresholded image of grayscale copy
	if len(displayImage.shape) == 2:
		thresholdedIm = thresholdedIm.astype(np.uint8)

	##find contours using the thresholded image
	im_c, contours_corners, hierarchy_c = cv2.findContours(thresholdedIm.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) #cv2.CHAIN_APPROX_NONE, cv2.CHAIN_APPROX_SIMPLE

	##organize these contours
	sortedContours = sorted(contours_corners, key = cv2.contourArea, reverse = True)
	drawnImage = cv2.drawContours(displayImage.copy(), contours_corners, -1, (255,255,0), 3)

	return drawnImage, sortedContours





def contourCountCheck(sortedContours, displayImage, contourMin):
	#sortedContours, (list), output from cv2.findContours function, found from locateGradients function
	#displayImage, (array), image containing the target
	#contourMin, (int), any contours with the number of points less than this Min value will be removed
	## to remove any contours that have a small amount of points. The average number of contour points for an object will reduce at higher altitudes, so this may not be a good method
	# we know that we can get rid of contour sets with 1-2 points, but after that the 'contourMin' selection becomes situational
	import numpy as np
	import cv2

	## Remove any small false artifacts that appear as contours (we are looking for large features with a large number of contour points)
	masterContourList = sortedContours
	removeContourIndices = []
	currentContourIndex = 0
	for currentContour in sortedContours:
		if len(currentContour) <= contourMin:
			removeContourIndices.append(currentContourIndex)
		currentContourIndex += 1

	removeContourIndices = sorted(removeContourIndices, reverse = True)
	for i in removeContourIndices:
		del masterContourList[i]

	drawnImage = cv2.drawContours(displayImage.copy(), masterContourList, -1, (255,255,0), 3)
	return masterContourList, drawnImage






def squareContourProportionCheck(sortedContours, displayImage, similarityThreshold):
	#sortedContours, (list), output from cv2.findContours function, found from locateGradients function
	#displayImage, (array), image containing the target	
	#similarityThreshold, (integer), amount in pixels for how similar in length the sides of an object are. If the difference between two sides exceeds this amount, then that set of contours is thrown out
	## create polygon that approximates a rectangle for the contour points, and check for proportionality for those sides if your desired target is a square
	#	'similarityThreshold' is used for comparison with the difference between each side in the object. For increasing altitude, the threshold may have to be reduced.
	import numpy as np
	import cv2

	masterContourList = []
	for currentContour in sortedContours:
		minRect = cv2.minAreaRect(currentContour)
		coordBox = cv2.boxPoints(minRect)
		coordBox = np.int0(coordBox)

		#calculate midpoint in this box
		topLeft = coordBox[2,:] #x, y
		bottomRight = coordBox[0,:]
		bottomLeft = coordBox[1,:]
		topRight = coordBox[3,:]
		middleCoord = (topLeft + bottomRight) // 2

		"""
		sideA_length = np.abs(topLeft[0] - topRight[0])
		sideB_length = np.abs(bottomLeft[0] - bottomRight[0])
		sideC_length = np.abs(topLeft[1] - bottomLeft[1])
		sideD_length = np.abs(topRight[1] - bottomRight[1])
		"""
		sideA_length = np.abs(topLeft[1] - topRight[1])
		sideB_length = np.abs(bottomLeft[1] - bottomRight[1])
		sideC_length = np.abs(topLeft[0] - bottomLeft[0])
		sideD_length = np.abs(topRight[0] - bottomRight[0])		

		A_B_diff = np.abs(sideA_length - sideB_length)
		C_D_diff = np.abs(sideC_length - sideD_length)
		A_C_diff = np.abs(sideA_length - sideC_length)
		A_D_diff = np.abs(sideA_length - sideD_length)
		B_C_diff = np.abs(sideB_length - sideC_length)
		B_D_diff = np.abs(sideB_length - sideD_length)

		#print(len(currentContour))
		#print(sideA_length, sideB_length, sideC_length, sideD_length)

		if A_B_diff in range(similarityThreshold) and C_D_diff in range(similarityThreshold):
			if A_C_diff in range(similarityThreshold) and A_D_diff in range(similarityThreshold):
				if B_C_diff in range(similarityThreshold) and B_D_diff in range(similarityThreshold):

					if sideA_length != 0 and sideB_length != 0 and sideC_length != 0 and sideD_length != 0:
						masterContourList.append(currentContour)

	drawnImage = cv2.drawContours(displayImage.copy(), masterContourList, -1, (255,255,0), 3)

	return masterContourList, drawnImage



def squareContourProportionCheckCenter(sortedContours, displayImage, similarityThreshold):
	#sortedContours, (list), output from cv2.findContours function, found from locateGradients function
	#displayImage, (array), image containing the target	
	#similarityThreshold, (integer), amount in pixels for how similar in length the sides of an object are. If the difference between two sides exceeds this amount, then that set of contours is thrown out
	## create polygon that approximates a rectangle for the contour points, and check for proportionality for those sides if your desired target is a square
	#	'similarityThreshold' is used for comparison with the difference between each side in the object. For increasing altitude, the threshold may have to be reduced.
	import numpy as np
	import cv2

	masterContourList = []
	for currentContour in sortedContours:
		minRect = cv2.minAreaRect(currentContour)
		coordBox = cv2.boxPoints(minRect)
		coordBox = np.int0(coordBox)

		#calculate midpoint in this box
		topLeft = coordBox[2,:] #x, y
		bottomRight = coordBox[0,:]
		bottomLeft = coordBox[1,:]
		topRight = coordBox[3,:]
		middleCoord = (topLeft + bottomRight) // 2

		##it is possible that the order of the coordinate system will not always be the same if the target is rotated. 
		#Therefore, this new version calculates the distance from each point to the center. For a square, this should be similar for each point regardless of order



		

		#print(len(currentContour))
		#print(sideA_length, sideB_length, sideC_length, sideD_length)

		if A_B_diff in range(similarityThreshold) and C_D_diff in range(similarityThreshold):
			if A_C_diff in range(similarityThreshold) and A_D_diff in range(similarityThreshold):
				if B_C_diff in range(similarityThreshold) and B_D_diff in range(similarityThreshold):

					if sideA_length != 0 and sideB_length != 0 and sideC_length != 0 and sideD_length != 0:
						masterContourList.append(currentContour)

	drawnImage = cv2.drawContours(displayImage.copy(), masterContourList, -1, (255,255,0), 3)

	return masterContourList, drawnImage




def cropPolyFromContour(displayImage, singleContour):
	#displayImage, (array), image containing the target
	#singleContour, (contour array), contains (x,y) coordinates of contour for single object. (just one contour, not all found in a scene).
	## Crop image as a polygon with masking. Returns average of masked image array.
	import numpy as np
	import cv2

	imageMask = zeros(displayImage.shape, dtype = np.uint8)




#PYTHON TEST HARNESS
if __name__ == '__main__':

	import cv2
	import os
	import time
	import numpy as np
	import scipy
	import scipy.misc
	from osgeo import gdal

	import gi
	gi.require_version('GExiv2', '0.10')
	from gi.repository import GExiv2



	
	### USER INPUTS

	# Determine frame to start selection for target"
	imagePath = '/cis/otherstu/gvs6104/DIRS/20170928/400flight/'
	#imagePath = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/'
	bandNumber = 2 #1 = blue, 2 = green, 3 = red, 4 = red edge, 5 = near infrared
	baseName = 'IMG_'

	###


	fileNames = sorted(os.listdir(imagePath))
	if ('geoTiff' in fileNames) == 1:
		fileNames.remove('geoTiff')
	if ('diag.dat' in fileNames) == 1:
		fileNames.remove('diag.dat')
	if ('GPSLog.csv' in fileNames) == 1:
		fileNames.remove('GPSLog.csv')
	if ('paramlog.dat' in fileNames) == 1:
		fileNames.remove('paramlog.dat')

	imageCount = len(fileNames)
	fileNameVector = np.linspace(1, (imageCount//5)-1, (imageCount//5)-1).astype(np.int32)
	altitudeVector = np.zeros((imageCount//5)-1)

	index = 0
	## iterate through all images after the selected scene with the target
	for imIndex in fileNameVector:
		currentImStr = imagePath + baseName + format(imIndex, '04') + '_' + str(bandNumber) + '.tif'

		## obtain the altitude [m] for the current frame
		currentImDict = metadataGrabber(currentImStr)
		currentAltitude = (currentImDict['Exif.GPSInfo.GPSAltitude']) - 165
		altitudeVector[index] = currentAltitude
		index += 1

		## read in the current image
		displayImage = mica2BGR(currentImStr) #bgr copy

		## get portion of image at NADIR
		displayImage = imageNadir(displayImage, cropProportion = 0.8)

		#obtain the contours in the image
		contouredImage, sortedContours = locateContours(displayImage, 32768, (2**16)-1)

		#contour correction
		sortedContours, contouredImage = contourCountCheck(sortedContours, displayImage, contourMin = 10) #eliminate objects with fewer than contourMin many contour points
		##display the image

		cv2.imshow('output', cv2.resize(contouredImage, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
		response = cv2.waitKey(0)	


		sortedContours, contouredImage = squareContourProportionCheck(sortedContours, displayImage, 5) #eliminate objects that do not have proportional sides, since we are looking for squares



		#display the number of found contours in the scene
		# print(' ')
		# for i in reducedContours:
		# 	print
		# 	print(i.shape, len(i))
		# print('----------')


		##display the image

		cv2.imshow('output', cv2.resize(contouredImage, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
		response = cv2.waitKey(0)			


		if response == 27:
			break
	cv2.destroyWindow('output')
