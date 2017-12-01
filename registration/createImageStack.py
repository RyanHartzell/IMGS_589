"""
title::
	registerMultiSpectral.py
description::
	Registers two multispectral band images from sUAS drone
attributes::
	im1 - Image that is being registered to
	im2 - Image that is being registered
author::
	Jackson Knappen
copyright::
	Copyright (C) 2017, Rochetser Institute of Technology
"""

########################
# method definition
########################

def computeMatches(im1, im2, feature="orb"):
	import cv2
	import numpy as np

	if feature == "orb":
		#ORB
		#scaleFactor = Pyramid decimination ratio > 1
		#nLevels = Number of Pyramid Levels
		#Edge Threshold = Size of border were features not detected
		#FirstLevel/FastThreshold = N/A
		#WTA_K = Number of points to produce each element of BRIEF
		#ScoreType = HARRIS VS. FAST
		#PatchSize = Size of patch used by orientated BREIF Descriptor
		orb = cv2.ORB_create(nfeatures=500,scaleFactor=1.5, nlevels=10,
							edgeThreshold=33, firstLevel=0, WTA_K=3, 
							scoreType=cv2.ORB_HARRIS_SCORE, patchSize=31, 
							fastThreshold=20)
		#Computes the features & descriptors for the images
		kp1, des1 = orb.detectAndCompute(im1.astype(np.uint8), None)
		kp2, des2 = orb.detectAndCompute(im2.astype(np.uint8), None)
		dist = []
		matches = []
		if (des1 is not None) and (des2 is not None):
			#print(des1)
			#print(des2)

			matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
			matches = matcher.match(des1, des2)
			matches = sorted(matches, key = lambda x:x.distance)
			#Calculates the distance between matches
			dist = [m.distance for m in matches]
		goodMatches = []
		if len(dist) != 0:
			#Finds the threshold distance between matches
			thres_dist = (np.sum(dist)/len(dist))*.70
			#Puts the thresholded matches into the good matches
			goodMatches = [m for m in matches if m.distance < thres_dist]

	elif feature == "sift":
		#SIFT
		#nOctaveLayers = Lowe Uses 3, Auto computed from resolution
		#ContrastThreshold = filter out weak features, > Threshold < Features
		#Edge Threshold = Filter out edge like features, > Thresh > Features
		#Sigma = The sigma of the Gaussian applied to input image at 0 octave
		sift = cv2.xfeatures2d.SIFT_create(nfeatures=500, nOctaveLayers=3,
										contrastThreshold=.01,
										edgeThreshold=50, sigma=3)
		#Computes the Keypoints and Descriptors at the Same Time
		kp1, des1 = sift.detectAndCompute(im1.astype(np.uint8), None)
		kp2, des2 = sift.detectAndCompute(im2.astype(np.uint8), None)

		bruteForce = cv2.BFMatcher()
		matches = bruteForce.knnMatch(des1, des2, k=2)
		
		#Lowe Ratio Test Matches 
		goodMatches = []
		for m,n in matches:
			if m.distance < (.7 * n.distance):
				goodMatches.append(m)

	if len(matches) == 0 or len(goodMatches) == 0:
		#msg = "No matches were able to be found between the two images"
		#raise ValueError(msg)
		goodMatches = None


	return kp1, kp2, goodMatches

def register(im1, im2, corCoef, feature):
	import cv2
	import numpy as np

	#im2 = cv2.imread(im2, 0)

	if corCoef < 0:
		#Can I base the polarity shfit on the correlation coefficent?
		im2 = cv2.bitwise_not(im2)

	if len(im1.shape) > 2:
		im1 = im1[:,:,0]
	if len(im2.shape) > 2:
		im2 = im2[:,:,0]

	#im_size = (im1.shape[0], im1.shape[1])
	kp1, kp2, goodMatches = computeMatches(im1, im2, feature)

	registerIm = im2
	if goodMatches is not None:
		match1 = np.array([kp1[i.queryIdx].pt for i in goodMatches], dtype=np.float32)
		match2 = np.array([kp2[i.trainIdx].pt for i in goodMatches], dtype=np.float32)
		homography, mask = cv2.findHomography(match2, match1, cv2.RANSAC)
		#matchIm = cv2.drawMatches(im1.astype(np.uint8), kp1, im2, kp2, goodMatches, None, 
		#							matchesMask=mask.ravel().tolist(),flags=2)
		#cv2.imshow('matchIm', cv2.resize(matchIm, None, fx=0.5, fy=0.5, 
		#								interpolation=cv2.INTER_AREA))
		#cv2.waitKey(0)
		if homography is not None:
			warpedIm = cv2.warpPerspective(im2, homography, (im1.shape[1], im1.shape[0]))
		
			warpedCorCoef = np.absolute(np.corrcoef(np.ravel(im1), np.ravel(warpedIm)))[0,1]
			if warpedCorCoef > 0.2:
				registerIm = warpedIm

		#Gets the matches out of the DMatch object into coordinates
		#match1 = np.array([kp1[i.queryIdx].pt for i in goodMatches], dtype='float32')
		#match2 = np.array([kp2[i.trainIdx].pt for i in goodMatches], dtype='float32')
		

		#M = cv2.getAffineTransform(match2[:3], match1[:3])
		#match2 = match2[:]
		#match1 = match1[:]
		#M = cv2.estimateRigidTransform(((match2/match2.max())*255).astype(np.uint8), ((match1/match1.max())*255).astype(np.uint8), False).astype(np.float64)

		#Compute the homography of the matches
		#print(homography.shape)
		#Create an image that draws the matching points
		

		#Warp the second image so that it registers with the first
		#registerIm = cv2.warpAffine(im2, M, (im1.shape[1], im1.shape[0]))

	return np.reshape(registerIm, im1.shape)

def stackImages(imageList, matchOrder, feature='orb', crop=True):
	import cv2
	import numpy as np
	from registration.correlateImages import createCorrelation
	from registration.correlateImages import findPairs

	#print(matchOrder[0,0])
	#print(imageList)
	for image in imageList:

		#print(int(image[-5]))
		if int(image[-5]) == int(matchOrder[0,0]):
			im1 = cv2.imread(image, cv2.IMREAD_UNCHANGED)
	#height, width, bands, dType = dimensions.dimensions(im1)
	height, width = im1.shape
	imageStack = np.zeros((height, width, len(imageList)))
	imageStack[:,:,int(matchOrder[0,0])-1] = im1

	mask = np.ones((height, width), dtype=np.uint8)

	for pair in range(matchOrder.shape[0]):
		correlationCoef = matchOrder[pair,2]
		im1 = imageStack[:,:,int(matchOrder[pair,0])-1]
		im2 = image[:-5] + str(int(matchOrder[pair,1])) + image[-4:]
		im2 = cv2.imread(im2, cv2.IMREAD_UNCHANGED)
		warped = register(im1, im2, correlationCoef, feature)		

		mask[np.where(warped == 0)] = 0
		imageStack[:,:,int(matchOrder[pair,1])-1] = warped

	goodCorr = True
	maxIndices, correlationMatrix = createCorrelation(imageStack)
	matchOrder = findPairs(maxIndices, correlationMatrix)
	bestCorrelation = matchOrder[:,-1]

	if (bestCorrelation> .2).sum() != bestCorrelation.size:
		goodCorr = False

	if goodCorr is True and crop is True:
		borderPix = 0
		while True:
			possTotal = (height-2*borderPix)*(width-2*borderPix)
			curTot = np.sum(mask[borderPix:height-borderPix,
								borderPix:width-borderPix])
			if curTot == possTotal:
				break
			borderPix += 1
		imageStack = np.asarray([imageStack[borderPix:height-borderPix, 
										borderPix:width-borderPix, im]
									for im in range(len(imageStack[0,0,:]))])
		imageStack = np.moveaxis(imageStack, 0, -1)	

	#_, contours, _, = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
	#											cv2.CHAIN_APPROX_SIMPLE)
	#print(contours)
	#x, y, w, h = cv2.boundingRect(contours[0])

	#imageStack = np.asarray([imageStack[y:y+h, x:x+w, im] \
	#							for im in range(len(imageStack[0,0,:]))])
	#imageStack = np.moveaxis(imageStack, 0, -1)

	return imageStack, goodCorr

if __name__ == '__main__':

	import os
	import ipcv
	import correlateImages
	import cv2
	import numpy as np
	#import dimensions

	#home = os.path.expanduser('~')
	#baseDirectory = 'src/python/modules/sUAS'
	#images = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/'
	images = '/cis/otherstu/gvs6104/DIRS/20170928/300flight/'

	#im1 = cv2.imread(images + 'IMG_0058_1.tif', cv2.IMREAD_UNCHANGED)
	#height, width, bands, dType = dimensions.dimensions(im1)

	im1 = images + 'IMG_0128_1.tif'
	im2 = images + 'IMG_0128_2.tif'
	im3 = images + 'IMG_0128_3.tif'
	im4 = images + 'IMG_0128_4.tif'
	im5 = images + 'IMG_0128_5.tif'

	imageList = [im1, im2, im3, im4, im5]
	matchOrder = correlateImages.OrderImagePairs(imageList, addOne=True)
	imageStack, goodCorr = stackImages(imageList, matchOrder, 'orb', crop=True)
	#print(imageStack)
	fullStack = cv2.addWeighted(imageStack[:,:,0], .2, 
								imageStack[:,:,1], .2, 0, None)
	#print(fullStack.shape)
	#print(imageStack.shape)
	for ind in range(2,len(imageList)):
		fullStack = cv2.addWeighted(fullStack, 1, imageStack[:,:,ind], .2, 0, None)
	fullStack = ipcv.histogram_enhancement(fullStack.astype(np.uint8), etype='linear2')
	cv2.imshow('Stacked Image', cv2.resize(fullStack, None, fx=0.8, fy=0.8, 
							interpolation=cv2.INTER_AREA).astype(np.uint8))

	action = ipcv.flush()
