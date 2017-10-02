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

def register(im1, im2):

	im_size = im1.shape

	#ORB 
	orb = cv2.ORB_create(200,2)
	#Computes the features & descriptors for the images
	kp1, des1 = orb.detectAndCompute(im1, None)
	kp2, des2 = orb.detectAndCompute(im2, None)

	keypointIm = cv2.drawKeypoints(im1, kp1, None, color=(127,255,0))
	# cv2.imshow('k',keypointIm)

	# find matching points from the descriptors
	matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")
	matches = matcher.match(des1, des2)

	'''
	# check if need reversal of polarity
	# note: call a function that recursively checks need for reversal (under the if statement)
	if len(matches) > 4:
		#Calculates the distance between matches
		dist = [m.distance for m in matches]
		#Finds the threshold distance between matches
		thres_dist = (np.sum(dist)/len(dist))*.65
		#Puts the thresholded matches into the good matches
		goodMatches = [m for m in matches if m.distance < thres_dist]
	'''

	#Gets the matches out of the DMatch object into coordinates
	match1 = np.array([kp1[i.queryIdx].pt for i in matches])
	match2 = np.array([kp2[i.trainIdx].pt for i in matches])

	#Compute the homography of the matches
	homography, mask = cv2.findHomography(match2, match1, cv2.RANSAC)

	#Create an image that draws the matching points
	matchIm = cv2.drawMatches(im1, kp1, im2, kp2, matches, None, matchesMask=mask.ravel().tolist(),flags=2)
	cv2.imshow('matchIm', cv2.resize(matchIm, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))

	#Warp the second image so that it registers with the first
	registerIm = cv2.warpPerspective(im2, homography, (im_size[1],im_size[0]))
	#Show the images stacked ontop of each other with 0.5 opacity
	blendIm = cv2.addWeighted(registerIm, 0.5, im1, 0.5, 0, None)
	cv2.imshow('blendIm', cv2.resize(blendIm, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))

	return registerIm

########################
# test harness
########################

if __name__ == '__main__':

	import os
	import sys
	import ipcv
	import cv2
	import numpy as np
	import matplotlib.pyplot as plt
	import matplotlib.image as mpimg


	home = os.path.expanduser('~')
	baseDirectory = 'src/python/modules/sUAS'
	images = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/'

	im1 = cv2.imread(images + 'IMG_0010_1.tif', cv2.IMREAD_GRAYSCALE)
	im2 = cv2.imread(images + 'IMG_0010_3.tif', cv2.IMREAD_GRAYSCALE)

	registration = register(im1=im1, im2=im2)

	action = ipcv.flush()
