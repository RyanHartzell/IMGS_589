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

		matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
		matches = matcher.match(des1, des2)
		#Calculates the distance between matches
		dist = [m.distance for m in matches]
		#Finds the threshold distance between matches
		thres_dist = (np.sum(dist)/len(dist))*.50
		#Puts the thresholded matches into the good matches
		goodMatches = [m for m in matches if m.distance < thres_dist]

	elif feature == "sift":
		#SIFT
		#nOctaveLayers = Lowe Uses 3, Auto computed from resolution
		#ContrastThreshold = filter out weak features, > Threshold < Features
		#Edge Threshold = Filter out edge like features, > Thresh > Features
		#Sigma = The sigma of the Gaussian applied to input image at 0 octave
		sift = cv2.xfeatures2d.SIFT_create(nfeatures=500, nOctaveLayers=3,
										contrastThreshold=.03,
										edgeThreshold=33, sigma=3)
		#Computes the Keypoints and Descriptors at the Same Time
		kp1, des1 = sift.detectAndCompute(im1.astype(np.uint8), None)
		kp2, des2 = sift.detectAndCompute(im2.astype(np.uint8), None)

		bruteForce = cv2.BFMatcher()
		matches = bruteForce.knnMatch(des1, des2, k=2)
		
		#Lowe Ratio Test Matches 
		goodMatches = []
		for m,n in matches:
			if m.distance < (.8 * n.distance):
				goodMatches.append(m)

	if len(matches) == 0:
		msg = "No matches were able to be found between the two images"
		raise ValueError(msg)

	return kp1, kp2, goodMatches

def register(im1, im2, corCoef):

	#im2 = cv2.imread(im2, 0)

	if corCoef < 0:
		#Can I base the polarity shfit on the correlation coefficent?
		im2 = cv2.bitwise_not(im2)

	if len(im1.shape) > 2:
		im1 = im1[:,:,0]

	im_size = (im1.shape[0], im1.shape[1])

	feature = "orb"
	kp1, kp2, goodMatches = computeMatches(im1, im2, feature)
	
	#Gets the matches out of the DMatch object into coordinates
	match1 = np.array([kp1[i.queryIdx].pt for i in goodMatches])
	match2 = np.array([kp2[i.trainIdx].pt for i in goodMatches])

	#Compute the homography of the matches
	homography, mask = cv2.findHomography(match2, match1, cv2.RANSAC)

	#Create an image that draws the matching points
	#matchIm = cv2.drawMatches(im1, kp1, im2, kp2, matches, None, 
	#							matchesMask=mask.ravel().tolist(),flags=2)
	#cv2.imshow('matchIm', cv2.resize(matchIm, None, fx=0.5, fy=0.5, 
	#								interpolation=cv2.INTER_AREA))
	#cv2.waitKey(0)

	#Warp the second image so that it registers with the first
	#registerIm = cv2.warpAffine(im2, homography[0:-1], (im1.shape[1], im1.shape[0]))
	registerIm = cv2.warpPerspective(im2, homography, (im_size[1],im_size[0]))


	return registerIm

if __name__ == '__main__':

	import os
	import ipcv
	import correlateImages
	import cv2
	import numpy as np



	#home = os.path.expanduser('~')
	#baseDirectory = 'src/python/modules/sUAS'
	#images = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/'
	images = '/cis/otherstu/gvs6104/DIRS/20170928/150flight/000/'

	im1 = cv2.imread(images + 'IMG_0058_1.tif', cv2.IMREAD_UNCHANGED)
	height, width, bands, dType = ipcv.dimensions(im1)

	im1 = images + 'IMG_0058_1.tif'
	im2 = images + 'IMG_0058_2.tif'
	im3 = images + 'IMG_0058_3.tif'
	im4 = images + 'IMG_0058_4.tif'
	im5 = images + 'IMG_0058_5.tif'

	imageList = [im1, im2, im3, im4, im5]

	matchOrder = correlateImages.OrderImagePairs(imageList, addOne=True)

	imageStack = np.zeros((height, width, len(imageList)))
	im1 = images + "IMG_0058_{0}.tif".format(int(matchOrder[0,0]))
	imageStack[:,:,0] = cv2.imread(im1, cv2.IMREAD_GRAYSCALE)
	for p in range(1, matchOrder.shape[1]):
		correlationCoef = matchOrder[p,2]
		im1 = imageStack[:,:,int(matchOrder[p,0])-1]
		im2 = images + "IMG_0058_{0}.tif".format(int(matchOrder[p,1]))
		im2 = cv2.imread(im2, cv2.IMREAD_GRAYSCALE)
		warped = register(im1, im2, correlationCoef)
		imageStack[:,:,int(matchOrder[p,1])-1] = warped

	fullStack = cv2.addWeighted(imageStack[:,:,0], .2, 
								imageStack[:,:,1], .2, 0, None)
	for ind in range(2,len(imageList)):
		fullStack = cv2.addWeighted(fullStack, 1, imageStack[:,:,ind], .2, 0, None)
	fullStack = ipcv.histogram_enhancement(fullStack.astype(np.uint8), etype='linear2')
	cv2.imshow('Stacked Image', cv2.resize(fullStack, None, fx=0.5, fy=0.5, 
							interpolation=cv2.INTER_AREA).astype(np.uint8))

	action = ipcv.flush()
