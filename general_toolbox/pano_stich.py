"""
title::
 	Automated Image Stitching using SIFT Feature Detection

description::
	This Program will stitch two images together using
	Scale Invarient Feature Transform to identify Features.

attributes::
    Im1 - The first im that you are trying to stitch
    Im2 - The second im that you are trying to stitch

author::
    Geoffrey Sasaki

copyright::
 Copyright (C) 2016, Rochester Institute of Technology
"""

import numpy as np
import ipcv
import cv2

def sift_features(im):
	#Create the SIFT Member Function
	sift = cv2.xfeatures2d.SIFT_create(nfeatures=0, nOctaveLayers=4,
										contrastThreshold=.04,
										edgeThreshold=10, sigma=5)
	
	#Convert im to GreyScale to preform SIFT
	#Reduces computation time when working on singe channel
	gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

	#Computes the Keypoints and Descriptors at the Same Time
	kp, desc = sift.detectAndCompute(gray, None)

	return kp, desc

def find_matches(imageF1, imageF2, verbose=False):
	im1, kp1, desc1 = imageF1[:3]
	im2, kp2, desc2 = imageF2[:3]

	bruteForce = cv2.BFMatcher()
	
	#Compute the matches using brute force matcher
	matches = bruteForce.knnMatch(desc1, desc2, k=2)

	#Lowe Ratio Test Matches 
	good = []
	for m,n in matches:
		if m.distance < .8*n.distance:
			good.append(m)

	if verbose:
		#Prints out the number of matches that passed the ratio test
		print("The amount of matches that passed" +
				" the Lowe Ratio Test is {0}.".format(len(good)))
	
		#Draws matches between base base and the current im
		matchedim = cv2.drawMatches(im1, kp1,
									im2, kp2,
									good, None, flags=2 )
		cv2.imshow("Matched Features", matchedim)

	return good

def find_homography(imageF1, imageF2, matches, verbose=False,
					method=1, threshold=5):

	im1, kp1, desc1 = imageF1[:3]
	im2, kp2, desc2 = imageF2[:3]

	if len(matches) > 4:
		#Create set of point matches between base and im
		match1 = np.array([kp1[i.queryIdx].pt for i in matches])
		match2 = np.array([kp2[i.trainIdx].pt for i in matches])

		if method == 1:
			#Finds Homography between the 2 matched points using RANSAC
			homography, mask = cv2.findHomography(	match2, match1, 
													cv2.RANSAC, threshold)
		else:
			homography, mask = cv2.findHomography(	match2, match1, 
													cv2.LMEDS, threshold)

		if verbose:		
			#Draws the matches with the RANSAC Mask Applied
			if method == 1:
				matchedim = cv2.drawMatches(im1, kp1, 
											im2, kp2, 
											matches, None,
											matchesMask=mask.ravel().tolist(), 
											flags=2 )
				cv2.imshow("RANSAC Matched Features", matchedim)
			
			#Draws the matches with the LMEDS Mask Applied
			elif method == 2:
				matchedim = cv2.drawMatches(im1, kp1, 
											im2, kp2, 
											matches, None,
											matchesMask=mask.ravel().tolist(), 
											flags=2 )
				cv2.imshow("Least-Median Matched Features", matchedim)

			else:
				#Homography was found using all points no change in matches
				pass

	else:
		msg = "There are not enough matches between the two images " +\
				"to make a homography estimation."
		raise ValueError(msg)

	return homography

def find_dimensions(im1, im2, homography):

	#Gets the dimensions of the images to be stitched
	h1, w1 = im1.shape[0], im1.shape[1]
	h2, w2 = im2.shape[0], im2.shape[1]

	#Finds the corner coordinates based on the size of the images
	pts1 = np.float32([	[ 0, 0],
						[ 0, h1],
						[w1, h1],
						[w1, 0]]).reshape(-1,1,2)
	pts2 = np.float32([	[ 0,  0],
						[ 0, h2],
						[w2, h2],
						[w2, 0]]).reshape(-1,1,2)

	#Warps second image corner coordinates based on calculated Homography
	pts2_ = cv2.perspectiveTransform(pts2, homography)
	#Finds the dimensions of the final image by combining
	pts = np.concatenate((pts2_, pts1), axis=0)

	#Finds the corner coordinates of the transformed image
	[xmin, ymin] = np.int64(pts.min(axis=0).ravel() - 0.5)
	[xmax, ymax] = np.int64(pts.max(axis=0).ravel() + 0.5)
	#Holds the necessary translation
	translate = [-xmin,-ymin]

	#Computes the offset coordinates
	offset = (xmax-xmin, ymax-ymin)
	
 	#Create the translation matrix for homography
	homographyTranslate = np.matrix([	[1, 0, translate[0] ],
										[0, 1, translate[1] ],
										[0, 0,   		 1  ]	])

	#Applies translation matrix to original homography matrix
	Homography = homographyTranslate.dot(homography)

	return Homography, offset, translate
	
def stitcher(im1, im2, Homography, offset, translate):
	#Gets the dimensions of the images to be stitched
	h1, w1 = im1.shape[0], im1.shape[1]
	h2, w2 = im2.shape[0], im2.shape[1]

	#Applies the perspective transform to the second image
	panorama = cv2.warpPerspective(im2, Homography, offset)

	#Adds the second image to the correct location
	panorama[translate[1]:h1+translate[1],translate[0]:w1+translate[0]] = im1

	return panorama

def pano_stitch(images, verbose=False):
	
	im1 = images[0]
	
	while len(images) != 1:

		for i in range(len(images)-1):

			im2 = images[i+1]

			kp1, desc1 = sift_features(im1)
			kp2, desc2 = sift_features(im2)

			imageF1 = (im1, kp1, desc1)
			imageF2 = (im2, kp2, desc2)

			#Draws the kp With Gradient Orentations
			if verbose:
				keypointIm = cv2.drawKeypoints(im1, kp1, None,
					flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
				cv2.imshow("Keypoint Image1", keypointIm)

				keypointIm = cv2.drawKeypoints(im2, kp2, None,
					flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
				cv2.imshow("Keypoint Image2", keypointIm)

			good = find_matches(imageF1, imageF2, verbose )

			if len(good) > 50:

				homography = find_homography(imageF1, imageF2,
											good, verbose, method=1,
											threshold=5)

				Homography, offset, translate = find_dimensions(im1, im2, 
																homography)

				panorama = stitcher(im1, im2, Homography, offset, translate)
				panorama.astype(np.uint8)

				if verbose:
					cv2.imshow("Current Panorama Progress", panorama)
					cv2.waitKey(0)

				if i != len(images)-1:
					im1 = panorama	

				images.pop(i)

				break

	return panorama

if __name__ == '__main__':
	import cv2
	import time
	import os
	import os.path
	import ipcv

	home = os.path.expanduser('~')
	baseDirectory = home + os.path.sep + 'src/python/examples/data'


	#imLeft = baseDirectory + '/Lenna_Left.jpg'
	#imRight = baseDirectory + '/Lenna_Right.jpg'
	
	imLeft = baseDirectory + '/LabL.JPG'
	imRight = baseDirectory + '/LabR.JPG'
	
	im1 = cv2.imread(imLeft, cv2.IMREAD_UNCHANGED)
	im2 = cv2.imread(imRight, cv2.IMREAD_UNCHANGED)
	
	cv2.imshow('Image 1', im1)
	cv2.imshow('Image 2', im2)
	images = [im1,im2]
	
	verbose = True

	startTime = time.time()
	panorama = pano_stitch(images, verbose)
	print("Elapsed Time = {0} [s]".format(time.time()-startTime))

	cv2.imshow('SIFT Image Stitch', panorama)

	action = ipcv.flush()
