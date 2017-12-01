
def getDisplayImage(geotiffFilename):
	import numpy as np
	import cv2
	from osgeo import gdal	

	#Get GEOTIFF
	imageStack = gdal.Open(geotiffFilename).ReadAsArray()
	imageStack = np.moveaxis(imageStack, 0, -1)


	#crop
	width = imageStack.shape[1]
	radius = width // 4
	imageCenter = (imageStack.shape[0]//2, imageStack.shape[1]//2)

	#circleMask = numpy.full(imageStack.shape[0:2], 0,  dtype=imageStack.dtype)
	#cv2.circle(circleMask, (imageCenter[1],imageCenter[0]), int(radius), (1,1,1), -1)
	#circleMask = numpy.repeat(circleMask[:,:,np.newaxis], imageStack.shape[2])
	#circleMask = circleMask.reshape(imageStack.shape)
	#imageStackMasked = imageStack*circleMask

	imageStack_crop = imageStack[imageCenter[0]-radius:imageCenter[0]+radius,imageCenter[1]-radius:imageCenter[1]+radius, :]



	band1 = imageStack_crop[:,:,0]
	band2 = imageStack_crop[:,:,1]
	band3 = imageStack_crop[:,:,2]
	band4 = imageStack_crop[:,:,3]
	band5 = imageStack_crop[:,:,4]	


	#displayImage = np.dstack((band1,band2,band3)).astype(np.uint8)
	displayImage = imageStack_crop[:,:,0:3].astype(imageStack.dtype) #RGB
	return imageStack_crop, displayImage


def selectROI(mapName):
	#mapName, (str)
	import numpy as np
	import cv2
	import ipcv

	#utilize 'PointsSelected' to get the search window, manual input
	p = ipcv.PointsSelected(mapName, verbose=False)
	p.clearPoints()
	while p.number() < 4:
		cv2.waitKey(100)

	return p.x(), p.y() 



def assignTargetNumber():
	#no input required
	currentTargetNumber = input("Enter Target Number. Then press 'enter'.\n")
	return currentTargetNumber



def computeStats(currentCroppedIm, geotiffFilename, pointsX, pointsY):
	#currentCroppedIm, (array)
	#geotiffFilename, (str)

	import numpy as np
	import cv2
	from osgeo import gdal

	#Create poly mask
	#mask = np.zeros_like(currentCroppedIm)
	mask = np.zeros((currentCroppedIm.shape[0], currentCroppedIm.shape[1]))
	polyMaskCoords = np.asarray(list(zip(pointsX, pointsY)))
	cv2.fillConvexPoly(mask, polyMaskCoords, 1)

	x_coords = np.where(np.any(mask==1, axis=1))
	y_coords = np.where(np.any(mask==1, axis=0))

	print(len(x_coords[0]), len(y_coords[0]))
	#apply the single channel mask to each of the five bands in 'currentCroppedIm'
	#maskedGeotiff = mask 


	return mask








#PYTHON TEST HARNESS
if __name__ == '__main__':

	import cv2
	import numpy
	import os
	import time
	import numpy as np
	import scipy
	import scipy.misc
	from osgeo import gdal


	geotiffFilename = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/IMG_0183.tiff'

	#get the geotiff image (5 band) and color (3 band)
	geoTiffImage, displayImage = getDisplayImage(geotiffFilename)


	mapName = 'Select corners for the target area.'
	cv2.namedWindow(mapName, cv2.WINDOW_AUTOSIZE)
	im = cv2.imshow(mapName, displayImage)

	#the image will be cropped...
	currentCroppedIm = geoTiffImage
	

	#select the points for a target in the scene
	pointsX, pointsY = selectROI(mapName)

	#ask user for input of the current target
	currentTargetNumber = assignTargetNumber()

	maskedIm = computeStats(currentCroppedIm, geotiffFilename, pointsX, pointsY)



	cv2.destroyWindow(mapName)


	cv2.namedWindow(mapName, cv2.WINDOW_AUTOSIZE)
	im = cv2.imshow(mapName, maskedIm)	

	cv2.waitKey(0)
	cv2.destroyWindow(mapName)
