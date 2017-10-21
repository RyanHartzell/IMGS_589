"""
title::
	Correlate Multispectral Images
description::
	Finds the images that are most correlated to create the image stack.
attributes::
	im1 - First image of the multispectral camera
	im2 - Second image of the multispectral camera
	im3 - Third image of the multispectral camera
	im4 - Fourth image of the multispectral camera
	im5 - Fifth image of the multispectral camera

author::
	Geoffrey Sasaki
copyright::
	Copyright (C) 2017, Rochetser Institute of Technology
"""

import numpy as np

def createCorrelation(images):
	flatImageList = []
	if type(images) == list:
		for image in images:
			flatImageList.append(np.ravel(image))
	elif type(images) is np.ndarray and images.shape[2] > 1:
		for i in range(images.shape[2]):
			flatImageList.append(np.ravel(images[:,:,i]))

	correlationMatrix = np.corrcoef(flatImageList)
	absoluteCorrelation = np.absolute(correlationMatrix)

	iTril = np.tril_indices(correlationMatrix.shape[0], k=0)
	correlationMatrix[iTril] = 0
	absoluteCorrelation[iTril] = 0
	iTriu = np.triu_indices(correlationMatrix.shape[0], k=1)
	numMax = len(correlationMatrix[iTriu])
	
	maxIndices = np.argpartition(absoluteCorrelation, range(-numMax,0), axis=None)[-numMax:][::-1]
	maxIndices = np.unravel_index(maxIndices, correlationMatrix.shape)
	maxValues = correlationMatrix[maxIndices]

	return maxIndices, correlationMatrix

def findPairs(correlationMatrix, maxIndices):
	max1, max2 = maxIndices[0], maxIndices[1]
	matchOrder = []
	matchOrder.append([max1[0], max2[0], correlationMatrix[max1[0],max2[0]]])
	for pair in range(1,len(maxIndices[0])):
		flatMatch = [i for tmp in matchOrder for i in tmp]
		if max1[pair] in flatMatch and max2[pair] not in flatMatch:
			matchOrder.append([max1[pair], max2[pair], correlationMatrix[max1[pair],max2[pair]]])
		elif max1[pair] not in flatMatch and max2[pair] in flatMatch:
			matchOrder.append([max1[pair], max2[pair], correlationMatrix[max1[pair],max2[pair]]])
	return np.asarray(matchOrder)

if __name__ == '__main__':

	import os
	import cv2

	imageDir = '/Users/Geoffrey/Desktop/UAS Class Data/150 ft flight/'
	im0 = cv2.imread(imageDir + '/band1/IMG_0459_1.tif', cv2.IMREAD_UNCHANGED)
	im1 = cv2.imread(imageDir + '/band2/IMG_0459_2.tif', cv2.IMREAD_UNCHANGED)
	im2 = cv2.imread(imageDir + '/band3/IMG_0459_3.tif', cv2.IMREAD_UNCHANGED)
	im3 = cv2.imread(imageDir + '/band4/IMG_0459_4.tif', cv2.IMREAD_UNCHANGED)
	im4 = cv2.imread(imageDir + '/band5/IMG_0459_5.tif', cv2.IMREAD_UNCHANGED)

	imageArray = np.dstack((im0, im1, im2, im3, im4))
	imageArray = [im0, im1, im2, im3, im4]
	maxIndices, correlationMatrix = createCorrelation(imageArray)
	matchOrder = findPairs(correlationMatrix, maxIndices)
	onesMatrix = np.ones(matchOrder.shape)
	onesMatrix[:,-1] = 0
	matchOrder += onesMatrix
	print(matchOrder)