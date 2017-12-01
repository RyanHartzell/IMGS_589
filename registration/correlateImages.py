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

def createCorrelation(images):
	import numpy as np
	import cv2

	flatImageList = []
	#Creates a flat image list to hold all of the images

	if type(images) == list and type(images[0]) == str:
		#If the input is a list and each element is a string
		for imStr in images:
			flatImArr = np.ravel(cv2.imread(imStr, cv2.IMREAD_UNCHANGED))
			#Reads in every image string as a flat image array
			flatImageList.append(flatImArr)
			#Adds the flat images to the flat image list
	elif type(images) == list and type(images[0]) == np.array:
		#If the input is a list and each element is an image array
		for imArr in images:
			flatImageList.append(np.ravel(imArr))
			#Adds the flat images to the flat image list
	elif type(images) is np.ndarray and images.shape[2] > 1:
		#If the type of the input is an array then it adds the images
		for i in range(images.shape[2]):
			flatImageList.append(np.ravel(images[:,:,i]))

	#Creates the correlation matrix of correlation coefficents
	correlationMatrix = np.corrcoef(flatImageList)
	#Creates an absolute value of the correlation matrix to find the maximum
	absoluteCorrelation = np.absolute(correlationMatrix)

	#iTril = np.tril_indices(correlationMatrix.shape[0], k=0)
	absoluteCorrelation[np.tril_indices(correlationMatrix.shape[0], k=0)] = 0
	numMax = int((correlationMatrix.shape[0]**2 -
									correlationMatrix.shape[0])/2)
	#Finds the number of values in the upper triangle of the correlation matrix
	#Since the lower triangle is duplicates and the diagonal is one we don't
	#use that when calculating the number of important correlation coefficents

	maxIndices = np.argpartition(absoluteCorrelation, range(-numMax,0),
												axis=None)[-numMax:][::-1]
	#Finds the indices of the top 10 maximum values of the flattened absolute
	#Correlation matrix array
	maxIndices = np.unravel_index(maxIndices, correlationMatrix.shape)
	#Finds the actual maximum (x,y) indices of the correlation matrix

	return maxIndices, correlationMatrix

def findPairs(maxIndices, correlationMatrix):
	import numpy as np

	max1, max2 = maxIndices[0], maxIndices[1]
	#Seperates the maximum indices into the respective x & y locations
	matchOrder = []
	matchOrder.append([max1[0], max2[0], correlationMatrix[max1[0],max2[0]]])
	#Adds the 2 highest maximums to the matched list
	for pair in range(1,len(maxIndices[0])):
		#Loops through every pair of images after the first one
		flatMatch = [i for tmp in matchOrder for i in tmp]
		#Flattens the already made matchorder list to do element comparison
		if max1[pair] in flatMatch and max2[pair] not in flatMatch:
			#Asks if the current x has already been matched and
			#that the current y has not been matched, if true adds the pair.
			matchOrder.append([max1[pair], max2[pair],
								correlationMatrix[max1[pair],max2[pair]]])
		elif max1[pair] not in flatMatch and max2[pair] in flatMatch:
			#Asks if the current y has already been matched and
			#that current x not matched if true, adds the pair.
			matchOrder.append([max2[pair], max1[pair],
								correlationMatrix[max1[pair],max2[pair]]])
	#Returns an array of matched images and their correlation coefficents
	#[ [ 0.0          2.0          0.8395225 ]
	#  [ 0.0          1.0          0.82916331]
	#  [ 0.0          3.0         -0.50211481]
	#  [ 3.0          4.0          0.44174728] ]
	return np.asarray(matchOrder)

def OrderImagePairs(imageList, addOne=True):
	#from correlateImages import createCorrelation
	#from correlateImages import findPairs
	import numpy as np

	#Combines the two above methods for easier calling
	maxIndices, correlationMatrix = createCorrelation(imageList)
	#Sample maxIndices return where the 1st is the x values any 2nd is y
	#[0, 0, 1, 0, 3, 2, 1, 1, 2, 0], [2, 1, 2, 3, 4, 3, 4, 3, 4, 4]

	#Sample Correlation Matrix Return
	#[[ 1.          0.82916331  0.8395225  -0.50211481  0.1391593 ]
 	# [ 0.82916331  1.          0.7491956  -0.25355265  0.3807286 ]
 	# [ 0.8395225   0.7491956   1.         -0.38993869  0.21488543]
 	# [-0.50211481 -0.25355265 -0.38993869  1.          0.44174728]
 	# [ 0.1391593   0.3807286   0.21488543  0.44174728  1.        ] ]
	#Creates the list of maxindices and the correlation
	matchOrder = findPairs(maxIndices, correlationMatrix)
	#Returns the ordered pairs of maximum correlation coefficents
	#Sample Matchorder Array Return Value
	#[ [ 0.0          2.0          0.8395225 ]
	#  [ 0.0          1.0          0.82916331]
	#  [ 0.0          3.0         -0.50211481]
	#  [ 3.0          4.0          0.44174728] ]
	if addOne:
		#Adds one to all of the image numbers for indexing purposes
		onesMatrix = np.ones(matchOrder.shape)
		#Creates a ones matrix the size of the matchOrder
		onesMatrix[:,-1] = 0
		#Sets the last column of the ones matrix to 0 to not modify correlation
		matchOrder += onesMatrix
		#Adds the ones matrix to the matchorder matrix
		#[ [ 1.0          3.0          0.8395225 ]
		#  [ 1.0          2.0          0.82916331]
		#  [ 1.0          4.0         -0.50211481]
		#  [ 4.0          5.0          0.44174728] ]
	return matchOrder

if __name__ == '__main__':

	imageDir = '/Users/Geoffrey/Desktop/UAS Class Data/150 ft flight/'

	im1 = imageDir + '/band1/IMG_0459_1.tif'
	im2 = imageDir + '/band2/IMG_0459_2.tif'
	im3 = imageDir + '/band3/IMG_0459_3.tif'
	im4 = imageDir + '/band4/IMG_0459_4.tif'
	im5 = imageDir + '/band5/IMG_0459_5.tif'

	imageList = [im1, im2, im3, im4, im5]
	matchOrder = OrderImagePairs(imageList, addOne=True)
	print(matchOrder)
