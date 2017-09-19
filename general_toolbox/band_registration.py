'''
This file should contain various functions for registration of multiple bands
of the same frame #. Try multiple registration methods, starting with SIFT.


'''

import cv2
import numpy as np

	sift = cv2.xfeatures2d.SIFT_create(nfeatures=0, nOctaveLayers=4,
										contrastThreshold=.04,
										edgeThreshold=10, sigma=5)
		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
	kp, desc = sift.detectAndCompute(gray, None)

	bruteForce = cv2.BFMatcher()
	matches = bruteForce.knnMatch(desc1, desc2, k=2)

#Lowe Ratio Test Matches 
	good = []
	for m,n in matches:
		if m.distance < .8*n.distance:
			good.append(m)

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

	panorama = cv2.warpPerspective(im2, Homography, offset)
