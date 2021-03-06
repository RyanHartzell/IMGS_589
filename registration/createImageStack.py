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

	eightIm1 = (im1/256).astype(np.uint8)
	eightIm2 = (im2/256).astype(np.uint8)

	if feature == "orb":
		#ORB
		#scaleFactor = Pyramid decimination ratio > 1
		#nLevels = Number of Pyramid Levels
		#Edge Threshold = Size of border were features not detected
		#FirstLevel/FastThreshold = N/A
		#WTA_K = Number of points to produce each element of BRIEF
		#ScoreType = HARRIS VS. FAST
		#PatchSize = Size of patch used by orientated BREIF Descriptor
		#Default:500, 1.2, 8, 31, 0, 2, cv2.ORB_HARRIS_SCORE, 31, 20
		orb = cv2.ORB_create(nfeatures=500,scaleFactor=1.2, nlevels=8,
							edgeThreshold=31, firstLevel=0, WTA_K=3,
							scoreType=cv2.ORB_FAST_SCORE, patchSize=31,
							fastThreshold=20)

		#Computes the features & descriptors for the images
		kp1, des1 = orb.detectAndCompute(eightIm1, None)
		kp2, des2 = orb.detectAndCompute(eightIm2, None)
		#The ORB detect and compute function only takes 8 bit images

		#kp1Image = cv2.drawKeypoints((im1/256).astype(np.uint8),
		#		kp1,None,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		#kp1Image = cv2.drawKeypoints((im1/256).astype(np.uint8),
		#		kp1,None,flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
		#kp2Image = cv2.drawKeypoints((im2/256).astype(np.uint8),
		#		kp2,None,flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		#kp2Image = cv2.drawKeypoints((im2/256).astype(np.uint8),
		#		kp2,None,flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
		#cv2.imshow("RAW Keypoint 1 Image", cv2.resize(kp1Image, None,
		#			fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA))
		#cv2.imshow("RAW Keypoint 2 Image", cv2.resize(kp2Image, None,
		#			fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA))
		#cv2.waitKey(0)

		dist = []
		matches, goodMatches = [], []
		#m1, m2 =[], []
		if (des1 is not None) and (des2 is not None):
			#Makes sure the descriptors are not empty or none
			#matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
			matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
			matches = matcher.match(des1, des2)
			#print(matches)
			#matches = matcher.knnMatch(des1, des2, k=2)
			#for i in range(len(matches)):
				#print(matches[i])
			#	m1.append(matches[i][0])
			#	m2.append(matches[i][1])

			#matches = sorted(matches, key = lambda x:x.distance)
			matches = sorted(matches, key = lambda x:x.distance)

			#matchIm = cv2.drawMatches((im1/256).astype(np.uint8),kp1,
			#	(im2/256).astype(np.uint8),kp2,matches, None, flags=2)
			#cv2.imshow("RAW Match Image", cv2.resize(matchIm, None,
			#			fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA))
			#top50matchIm = cv2.drawMatches((im1/256).astype(np.uint8),kp1,
			#	(im2/256).astype(np.uint8),kp2,matches[:len(matches)//2], None, flags=2)
			#cv2.imshow("Top 50 Match Image", cv2.resize(top50matchIm, None,
			#			fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA))
			#Calculates the distance between matches
			dist = [m.distance for m in matches]

		if len(dist) != 0:
			#Finds the threshold distance between matches
			thres_dist = (np.sum(dist)/len(dist))*.7
			#Puts the thresholded matches into the good matches
			goodMatches = [m for m in matches if m.distance <= thres_dist]
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
		kp1, des1 = sift.detectAndCompute(eightIm1, None)
		kp2, des2 = sift.detectAndCompute(eightIm2, None)

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

def register(fixedIm, movingIm, corCoef, feature, bandQC=False):
	import cv2
	import sys
	import os
	import numpy as np
	from registration import userMove

	featureMovingIm = np.copy(movingIm)
	#Creates a copy of the image to account for a polarity switch
	if corCoef < 0:
		print("Bitwise Switch")
		featureMovingIm = cv2.bitwise_not(featureMovingIm)
	if len(fixedIm.shape) > 2:
		fixedIm = fixedIm[:,:,0]
	if len(movingIm.shape) > 2:
		featureMovingIm = featureMovingIm[:,:,0]

	warpedIm, registerIm = movingIm, movingIm
	warpMatrix = np.eye(2,3, dtype=np.float32)
	warpedCorCoef = 0
	perfect = np.matrix([[1,0],[0,1]])

	try:
		cc, warpMatrix = cv2.findTransformECC(fixedIm.astype(np.float32),
                featureMovingIm.astype(np.float32), warpMatrix, cv2.MOTION_EUCLIDEAN)

		translate = np.around(warpMatrix[:2,2]).astype(int)
		small = True
		for t in translate:
			if np.absolute(t) > 5:
				small = False

		scaleRotate = np.around(warpMatrix[:2,:2]).astype(int)
		if np.sum(scaleRotate==perfect) == 4 and small is True:
			warpedIm = cv2.warpAffine(movingIm, warpMatrix, (fixedIm.shape[1],
			    fixedIm.shape[0]),flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
	except:
		kp1, kp2, goodMatches = computeMatches(fixedIm, featureMovingIm, feature="orb")
		if goodMatches is not None:
			match1 = np.array([kp1[i.queryIdx].pt for i in goodMatches], dtype=np.float32)
			match2 = np.array([kp2[i.trainIdx].pt for i in goodMatches], dtype=np.float32)

			#So according to the documentation, this funtion uses RANSAC to filter
			M = cv2.estimateRigidTransform(match2, match1, False)
			if M is not None:
				scaleRotate = np.around(M[:2,:2]).astype(int)
				if np.sum(scaleRotate==perfect) == 4:
					warpedIm = cv2.warpAffine(movingIm, M, (fixedIm.shape[1], fixedIm.shape[0]))

	warpedCorCoef = np.absolute(np.corrcoef(np.ravel(fixedIm), np.ravel(warpedIm)))[0,1]
	if warpedCorCoef > 0.2:
		registerIm = np.reshape(warpedIm, fixedIm.shape).astype(fixedIm.dtype)

	if bandQC:
		imageStack = cv2.addWeighted(fixedIm, .5, registerIm, .5, 0)
		#imageStack = cv2.resize(imageStack, None, fx=.5, fy=.5,
		#					interpolation=cv2.INTER_AREA)
		while True:
			cv2.imshow("Quality Control: Press 'n' to reject | 'r' to reset | ' ' to accept", imageStack)
			approve = cv2.waitKey(0)
			wasdList = [ord('w'), ord('W'), ord('a'), ord('A'), ord('s'), ord('S'),
						ord('d'), ord('D')]
			if approve == ord(' '):
				break
			elif approve == ord('n') or approve in wasdList:
				registerIm = userMove(fixedIm, registerIm)
				break
			elif approve == ord('r'):
				registerIm = userMove(fixedIm, movingIm)
				break
		cv2.destroyWindow("Quality Control: Press 'n' to reject | 'r' to reset | ' ' to accept")

	return registerIm

def stackImages(imageList, matchOrder, preRegisterDict, feature='orb', crop=True, bandQC=False):
	import cv2
	import numpy as np
	from registration.correlateImages import createCorrelation
	from registration.correlateImages import findPairs
	#import context
	#from context import geoTIFF
	import geoTIFF
	#from correlateImages import createCorrelation
	#from correlateImages import findPairs
	#print(matchOrder)
	firstImage = imageList[0][:-5] + str(int(matchOrder[0,0])) + imageList[0][-4:]
	im1 = cv2.imread(firstImage, cv2.IMREAD_UNCHANGED)
	height, width = im1.shape
	im1Metadata = geoTIFF.metadataGrabber(firstImage)
	im1band = im1Metadata['Xmp.Camera.BandName']
	imageStack = np.zeros((height, width, len(imageList)), dtype=im1.dtype)
	imageStack[:,:,int(matchOrder[0,0])-1] = im1
	#Puts the first image into the respective place in the image stack.
	#IE. IMG_0128_2 goes into ImageStack[:,:,1] due to python indexing

	mask = np.ones((height, width), dtype=im1.dtype)
	for pair in range(matchOrder.shape[0]):
		correlationCoef = matchOrder[pair,2] #Extracts pair correlation coefficent
		#print(correlationCoef, matchOrder[pair])
		fixed = imageStack[:,:,int(matchOrder[pair,0])-1]
		#Defines the variable fixed as the image at the index of the imagestack
		#This variable will be stored as an array since it's already read in
		moving = imageList[pair][:-5] + str(int(matchOrder[pair,1])) \
				+ imageList[pair][-4:]
		movingMetadata = geoTIFF.metadataGrabber(moving)
		movingBand = movingMetadata['Xmp.Camera.BandName']
		affineMatrix = preRegisterDict[(im1band+'/'+movingBand)]
		#Defines the variable moving as the name of the image to be matched against
		moving = cv2.imread(moving, cv2.IMREAD_UNCHANGED)
		moving = cv2.warpAffine(moving, affineMatrix, (fixed.shape[1], fixed.shape[0]))
		#Then reads in the image as an array
		warped = register(fixed, moving, correlationCoef, feature, bandQC)
		#Registers the image and returns a warped version of the moving image
		#Typically this will be used using an ORB Feature detector
		#If the correlation coefficent is negative it will switch the polarity
		#of the image being used only for the matching purpose.

		mask[np.where(warped == 0)] = 0
		imageStack[:,:,int(matchOrder[pair,1])-1] = warped
		#Places the warped image into the image stack

	goodCorr = True
	maxIndices, correlationMatrix = createCorrelation(imageStack)
	matchOrder = findPairs(maxIndices, correlationMatrix)
	bestCorrelation = matchOrder[:,-1]

	#if sum(bestCorrelation>.2) != bestCorrelation.size:
		#Are all the correlation's greater than .2?
		#print(bestCorrelation.size)
		#print(bestCorrelation)
		#goodCorr = False

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

	return imageStack, goodCorr

if __name__ == '__main__':

	import os
	import ipcv
	import correlateImages
	import cv2
	import numpy as np

	#home = os.path.expanduser('~')
	#baseDirectory = 'src/python/modules/sUAS'
	#images = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/'
	images = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1400/micasense/processed/'

	im1 = images + 'IMG_0110_1.tif'
	im2 = images + 'IMG_0110_2.tif'
	im3 = images + 'IMG_0110_3.tif'
	im4 = images + 'IMG_0110_4.tif'
	im5 = images + 'IMG_0110_5.tif'
	imageList = [im1, im2, im3, im4, im5]
	matchOrder = correlateImages.OrderImagePairs(imageList, addOne=True)
	imageStack, goodCorr = stackImages(imageList, matchOrder, 'orb', crop=False)

	dispImageStack = (imageStack/256).astype(np.uint8)
	bgrDisplay = dispImageStack[:,:,0:3]
	cv2.imshow('RGB Register', cv2.resize(bgrDisplay, None, fx=0.8,fy=0.8,
				interpolation=cv2.INTER_AREA))

	action = ipcv.flush()
