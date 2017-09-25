"""
title::
	registrationTest.py
description::
	Image registration for drone imagery, using feature matching from Enhanced Correlation
	Coefficient (ECC) Maximization
attributes::
	database - directory name for the database of training images (contains '
	subdirectioies for each subject)
	image - input image to test face detection and recognition
	f_t - threshold for face detection (maximum face space distance)
	nf_t - threshold for face recognition (maximum weight distance)
author::
	Jackson Knappen
SOURCE::
  https://www.learnopencv.com/image-alignment-ecc-in-opencv-c-python/ 
copyright::
	Copyright (C) 2017, Rochetser Institute of Technology
"""

########################
# method definition
########################

def register(im1, im2):

	im_size = im1.shape

	# transformation motion type
	warp_mode = cv2.MOTION_HOMOGRAPHY


	if warp_mode == cv2.MOTION_HOMOGRAPHY:
		warp_mat = np.eye(3,3,dtype=np.float32)
	else:
		warp_mat = np.eye(2,3,dtype=np.float32)

	iterations = 5000
	termination_eps = 1e-10
	criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations, termination_eps-10)

	# find transform 
	(cc, warp_mat) = cv2.findTransformECC(im1, im2, warp_mat, warp_mode, criteria)
	if warp_mode == cv2.MOTION_HOMOGRAPHY:
		 # Use warpPerspective for Homography 
	    im2_aligned = cv2.warpPerspective (im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
	else:
	    # Use warpAffine for Translation, Euclidean and Affine
	    im2_aligned = cv2.warpAffine(im2, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
 
	cv2.imshow("Image 1", im1)
	cv2.imshow("Image 2", im2)
	cv2.imshow("Aligned Image 2", im2_aligned)
	cv2.waitKey(0)

	return cc, warp_mat

########################
# test harness
########################

if __name__ == '__main__':

	import os
	import sys
	import cv2
	import numpy as np


	home = os.path.expanduser('~')
	baseDirectory = 'src/python/modules/sUAS'
	images = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/'

	im1 = cv2.imread(images + 'IMG_0010_3.tif', cv2.IMREAD_GRAYSCALE)
	im2 = cv2.imread(images + 'IMG_0010_4.tif', cv2.IMREAD_GRAYSCALE)
	# im2 = 255-im2
	
	print(im1.shape, im1.dtype)
	print(im2.shape, im2.dtype)

	registration = register(im1=im1, im2=im2)
