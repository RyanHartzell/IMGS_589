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
		kp1, des1 = orb.detectAndCompute(im1, None)
		kp2, des2 = orb.detectAndCompute(im2, None)
		
		matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
		matches = matcher.match(des1, des2)
		
		#Calculates the distance between matches
		dist = [m.distance for m in matches]
		#Finds the threshold distance between matches
		thres_dist = (np.sum(dist)/len(dist))*.65
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
		kp1, des1 = sift.detectAndCompute(im1, None)
		kp2, des2 = sift.detectAndCompute(im2, None)

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

def reversePolarityCheck(im1, im2, matches):
	#reverse the polarity of a function

	if len(matches) < 50:
		reverseIm1 = cv2.bitwise_not(im1)
		matches = computeMatches(reverseIm1, im2)

		if len(matches) < 50:
			reverseIm2 = cv2.bitwise_not(im2)
			matches = computeMatches(im1, reverseIm2)

			if len(matches) < 50:
				msg = "Not enouch matches could be found between \
				the two images"
				raise ValueError(msg)

	return matches

def register(im1, im2):

	if len(im1.shape) > 2:
		im1 = im1[:,:,0]

	im_size = (im1.shape[0],im1.shape[1])

	#ORB 
	#orb = cv2.ORB_create(200,2)
	#Computes the features & descriptors for the images
	#kp1, des1 = orb.detectAndCompute(im1, None)
	#kp2, des2 = orb.detectAndCompute(im2, None)

	#keypointIm = cv2.drawKeypoints(im1, kp1, None, color=(127,255,0))
	# cv2.imshow('k',keypointIm)

	# find matching points from the descriptors
	#matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
	#matches = matcher.match(des1, des2)

	
	# check if need reversal of polarity
	# note: call a function that recursively checks need for reversal (under the if statement)
	#if len(matches) > 4:
		#Calculates the distance between matches
		#dist = [m.distance for m in matches]
		#Finds the threshold distance between matches
		#thres_dist = (np.sum(dist)/len(dist))*.65
		#Puts the thresholded matches into the good matches
		#goodMatches = [m for m in matches if m.distance < thres_dist]

	feature = "sift"
	startTime = time.time()
	kp1, kp2, matches = computeMatches(im1, im2, feature)
	print("The matches were computed using the {0} feature detector".format(feature) + 
		" and were completed in {0:4f} [sec].".format(time.time()-startTime))
	goodMatches = reversePolarityCheck(im1, im2, matches)

	#Gets the matches out of the DMatch object into coordinates
	match1 = np.array([kp1[i.queryIdx].pt for i in goodMatches])
	match2 = np.array([kp2[i.trainIdx].pt for i in goodMatches])

	#Compute the homography of the matches
	homography, mask = cv2.findHomography(match2, match1, cv2.RANSAC)

	#Create an image that draws the matching points
	matchIm = cv2.drawMatches(im1, kp1, im2, kp2, matches, None, 
								matchesMask=mask.ravel().tolist(),flags=2)
	cv2.imshow('matchIm', cv2.resize(matchIm, None, fx=0.5, fy=0.5, 
									interpolation=cv2.INTER_AREA))

	#Warp the second image so that it registers with the first
	registerIm = cv2.warpPerspective(im2, homography, (im_size[1],im_size[0]))
	#Show the images stacked ontop of each other with 0.5 opacity
	#blendIm = cv2.addWeighted(registerIm, 0.5, im1, 0.5, 0, None)
	#cv2.imshow('blendIm', cv2.resize(blendIm, None, fx=0.5, fy=0.5, 
	#									interpolation=cv2.INTER_AREA))

	return registerIm

########################
# test harness
########################

if __name__ == '__main__':

	import os
	import sys
	import ipcv
	import time
	import cv2
	import numpy as np
	import matplotlib.pyplot as plt
	import matplotlib.image as mpimg


	home = os.path.expanduser('~')
	baseDirectory = 'src/python/modules/sUAS'
	images = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/'
	images = '/cis/otherstu/gvs6104/DIRS/20170928/150flight/000/'

	im1 = cv2.imread(images + 'IMG_0058_1.tif', cv2.IMREAD_GRAYSCALE)
	im2 = cv2.imread(images + 'IMG_0058_2.tif', cv2.IMREAD_GRAYSCALE)
	im3 = cv2.imread(images + 'IMG_0058_3.tif', cv2.IMREAD_GRAYSCALE)
	im4 = cv2.imread(images + 'IMG_0058_4.tif', cv2.IMREAD_GRAYSCALE)
	im5 = cv2.imread(images + 'IMG_0058_5.tif', cv2.IMREAD_GRAYSCALE)

	warped2 = register(im1=im1, im2=im2)
	warped3 = register(im1=im1, im2=im3)
	warped4 = register(im1=im1, im2=im4)
	warped5 = register(im1=im1, im2=im5)

	#Show the images stacked ontop of each other with 0.5 opacity
	stacked12 = cv2.addWeighted(warped2, 0.5, im1, 0.5, 0, None)
	stacked13 = cv2.addWeighted(warped3, 0.5, im1, 0.5, 0, None)
	stacked14 = cv2.addWeighted(warped4, 0.5, im1, 0.5, 0, None)
	stacked15 = cv2.addWeighted(warped5, 0.5, im1, 0.5, 0, None)
	cv2.imshow('Stacked 1 & 2', cv2.resize(stacked12, None, fx=0.5, fy=0.5, 
							interpolation=cv2.INTER_AREA).astype(im1.dtype))
	cv2.imshow('Stacked 1 & 3', cv2.resize(stacked13, None, fx=0.5, fy=0.5, 
							interpolation=cv2.INTER_AREA).astype(im1.dtype))
	cv2.imshow('Stacked 1 & 4', cv2.resize(stacked14, None, fx=0.5, fy=0.5, 
							interpolation=cv2.INTER_AREA).astype(im1.dtype))
	cv2.imshow('Stacked 1 & 5', cv2.resize(stacked15, None, fx=0.5, fy=0.5, 
							interpolation=cv2.INTER_AREA).astype(im1.dtype))
	
	#Show the images stacked ontop of each other with 0.2 opacity
	fullStack = cv2.addWeighted(im1, 0.20, warped2, 0.2, 0, None)
	fullStack = cv2.addWeighted(fullStack, 1.0, warped3, 0.2, 0, None)
	fullStack = cv2.addWeighted(fullStack, 1.0, warped4, 0.2, 0, None)
	fullStack = cv2.addWeighted(fullStack, 1.0, warped5, 0.2, 0, None)
	cv2.imshow('Stacked Image', cv2.resize(fullStack, None, fx=0.5, fy=0.5, 
							interpolation=cv2.INTER_AREA).astype(im1.dtype))

	stackedImage = np.dstack((im1, warped2, warped3, warped4, warped5))

	action = ipcv.flush()
