
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
	displayImage = imageStack_crop[:,:,0:3].astype(np.uint8) #RGB
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
	mask = np.zeros((currentCroppedIm.shape[0], currentCroppedIm.shape[1]))
	polyMaskCoords = np.asarray(list(zip(pointsX, pointsY)))
	cv2.fillConvexPoly(mask, polyMaskCoords, 1.0)

	#apply the single channel mask to each of the five bands in 'currentCroppedIm'
	mask[np.where(mask == 0)] = np.nan 
	mask = mask.astype(currentCroppedIm.dtype)

	print(currentCroppedIm[:,:,0])
	print(currentCroppedIm.dtype)

	#ROI_image = mask * currentCroppedIm.T
	ROI_image = np.dstack(((mask * currentCroppedIm[:,:,0]), (mask * currentCroppedIm[:,:,1]), (mask * currentCroppedIm[:,:,2]), (mask * currentCroppedIm[:,:,3]), (mask * currentCroppedIm[:,:,4])))





	#calculate statistics
	mean = []
	stdev = []
	for i in [0, 1, 2, 3, 4]:
		mean.append(np.nanmean(ROI_image[:,:,i]))
		stdev.append(np.nanstd(ROI_image[:,:,i]))

	#calculate centroid
	centroid = [np.mean(np.asarray(pointsX)) ,np.mean(np.asarray(pointsY))]
	print(mean)
	print(stdev)
	print(centroid)

	cv2.imshow('a', (ROI_image[:,:,0]).astype(np.uint8))
	cv2.waitKey(0)


	return mask, ROI_image








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


	geotiffFilename = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/IMG_0181.tiff'

	#get the geotiff image (5 band) and color (3 band)
	geoTiffImage, displayImage = getDisplayImage(geotiffFilename)
	print(geoTiffImage.dtype)
	print(np.max(geoTiffImage))


	# mapName = 'Select corners for the target area.'
	# cv2.namedWindow(mapName, cv2.WINDOW_AUTOSIZE)
	# im = cv2.imshow(mapName, displayImage)
	

	# #select the points for a target in the scene
	# pointsX, pointsY = selectROI(mapName)
	# cv2.destroyWindow(mapName)

	# #ask user for input of the current target
	# currentTargetNumber = assignTargetNumber()

	# maskedIm, ROI_image = computeStats(geoTiffImage, geotiffFilename, pointsX, pointsY)


