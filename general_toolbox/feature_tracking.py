"""
title::
 	Video Object Detection & Tracking using ORB Features

description::
	This program will detect an object in a video sequence, calculate
	its features then track the object around the frame. 

attributes::
    video: The video with the objet that you wish to track
    speed: If you want to apply grayscale and resizeing
    background: "threshold" and "gaussian_mixture" segmentation

author::
    Geoffrey Sasaki

copyright::
 Copyright (C) 2017, Rochester Institute of Technology
"""

import cv2
import ipcv
import numpy as np

def feature_tracking(video, verbose=True, speed=False, 
										background="threshold"):

	#The first step is to check if the provided video was able to be opened
	if video.isOpened() == False:
		msg = "The provided video file was not opened."
		raise ValueError(msg)

	#Initalize the average frame and previous frame
	avgFrame = None
	prevMaskedFrame = None

	width, height, framerate, codec = int(video.get(3)), int(video.get(4)), \
										int(video.get(5)), int(video.get(6))
	if speed:
		longedge = np.max((width, height)) #Find the long side
		if longedge > 500:	
				scaleFactor = 500/longedge		#Calculate the scale factor
				frameSize = (int(width*scaleFactor), int(height*scaleFactor))
	else:
		scaleFactor = 1
		frameSize = (width, height)  						#Framesize

	codec = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D') 		#CODEC Define
	fps = framerate 												#FPS Define
	isColor = True 											#Is color true
	videoFilename = 'TrackedVideo.mp4'						#Filename
	writer = cv2.VideoWriter(videoFilename, codec, fps, frameSize, isColor)
	#Creates a writer for the video

	if background == "gaussian_mixture":
		#If using the gaussin mixture version for background segmentaiton
		fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
		morphKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

	orb = cv2.ORB_create(50,2)				#using the ORB feaure detector

	#Using the BruteForce Descriptor Matcher with Hamming
	matcher = cv2.DescriptorMatcher_create("BruteForce-Hamming")

	#If the video is able to be opened, we will continue to read each frame
	while(video.isOpened()):
		retrived, frame = video.read()		#Read in the video frame

		#Check if we reached the end of the video
		if retrived == False:
			print("You have reached the end of the video.")
			break
		
		frame = cv2.resize(frame, dsize=(0,0), 
							fx=scaleFactor, fy=scaleFactor) #Resize

		if verbose:
			cv2.imshow('Frame', frame)



		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)			#Greyscale
		gray = gray.astype(np.float64)

		#If the type of background segmentation is to simply threshold movement
		if background == "threshold":	
			gray = cv2.GaussianBlur(gray, (0,0), 10)			#Gaussian Blur

			#Sets the first frame to the first frame if initalized
			if avgFrame is None:
				avgFrame = gray.astype(np.float64)
				continue

			#Creates the weighted average background frame for the sum
			cv2.accumulateWeighted(gray, avgFrame, 0.001)
			#Finds the absolute difference between the average and the current
			difference = cv2.absdiff(src1=avgFrame, src2=gray)

			#Finds the threshold for the average and the object
			rect, threshold = cv2.threshold(difference.astype(np.uint8), 
								thresh=15, maxval=255,type=cv2.THRESH_BINARY)
			#Dilates and erodes the threshold bubbles to smooth out noise
			threshold = cv2.dilate(threshold, None, iterations=2)
			threshold = cv2.erode(threshold, None, iterations=2)

			if verbose:
				cv2.imshow("Average Frame", avgFrame.astype(np.uint8))
				cv2.imshow("Difference", difference.astype(np.uint8))
				cv2.imshow("Threshold", threshold)

		elif background == "gaussian_mixture":
			if speed:
				threshold = fgbg.apply(gray)	#Applies Gaussian Mix to Gray
			else:
				threshold = fgbg.apply(frame)  	#Applies Gaussian Mix to Color

			#Applies morphology to the gaussian mix threshold to filter noise
			threshold = cv2.morphologyEx(threshold, 
											cv2.MORPH_OPEN, morphKernel)

			threshold = cv2.dilate(threshold, None, iterations=3)

			if verbose:
				cv2.imshow("MOG Mask", threshold)
					
		threshold[threshold>0] = 1			#Subs the 255 Max Count for 1

		if speed:
			#Applies threshold mask to gray image
			maskedFrame = (threshold*gray).astype(np.uint8)

		else:
			#Creates a 3 Channel threshold mask
			threshold = np.repeat(threshold[:,:,np.newaxis],
										repeats=3, axis=2)		
			#Applies threshold mask to the full color frame
			maskedFrame = (threshold*frame).astype(np.uint8)

		if verbose:
			cv2.imshow("MaskedFrame", maskedFrame)


		if prevMaskedFrame is None:
			prevMaskedFrame = maskedFrame
			continue

		#Computes the features & descriptors for the maked images
		kp1, des1 = orb.detectAndCompute(prevMaskedFrame, None)
		kp2, des2 = orb.detectAndCompute(maskedFrame, None)

		if des1 is not None and des2 is not None:
			#Brute force matches the descriptors between frames
			matches = matcher.match(des1, des2)
			
			if len(matches) > 4:
				#Calculates the distance between matches
				dist = [m.distance for m in matches]
				#Finds the threshold distance between matches
				thres_dist = (np.sum(dist)/len(dist))*.65
				#Puts the thresholded matches into the good matches
				goodMatches = [m for m in matches if m.distance < thres_dist]
				
				#Gets the matches out of the DMatch object into coordinates
				match1 = np.array([kp1[i.queryIdx].pt for i in goodMatches])
				match2 = np.array([kp2[i.trainIdx].pt for i in goodMatches])

				if len(match1) > 2 and len(match2) > 2:
					#Calculates the RANSAC between matched points
					homography, mask = cv2.findHomography(	match2, match1, 
															cv2.RANSAC)
					
					if verbose and mask is not None:
						keypointIm = cv2.drawKeypoints(frame, kp2, None, 
														color=(127,255,0))

						RANSACmatches = cv2.drawMatches(prevMaskedFrame, kp1, 
											maskedFrame, kp2, 
											goodMatches, None,
											matchesMask=mask.ravel().tolist(), 
											flags=2 )
						cv2.imshow("Keypoint Image", keypointIm)
						cv2.imshow("RANSAC Matched Features", RANSACmatches)


					if mask is not None:
						inliners = match2*mask #Calculates the RANSAC inliners
						inliners = [pt for pt in inliners if np.sum(pt) != 0]
						
						xCoor = [] #Holds the inliner x coordinates
						yCoor = []	#Holds the coressponding y inliners

						for pt in inliners:
							x, y = pt[0], pt[1]
							xCoor.append(x)
							yCoor.append(y)

						#Finds the max and min of each of the inliners
						tlKp = (int(min(xCoor)), int(max(yCoor)))
						brKp = (int(max(xCoor)), int(min(yCoor)))
						size = (brKp[0]-tlKp[0], tlKp[1]-brKp[1])
						centroid = (int(np.average(xCoor)), int(np.average(yCoor)))
						tlKp = (centroid[0]-size[0]//2, centroid[1]+size[1]//2)
						brKp = (centroid[0]+size[0]//2, centroid[1]-size[1]//2)

						#Creates a crosshair on the centroid of the matched points
						trackedFrame = cv2.drawMarker(frame, centroid,
											color=(127,255,0), 
											markerType=cv2.MARKER_TILTED_CROSS,
											markerSize=15, thickness=2)

						#Creates a rectangle around the extrema matched points
						#rectangleFrame = cv2.rectangle(frame, tlKp, brKp, 
						#					color=(127,255,0), thickness=2)
						
						cv2.imshow("Tracked Frame", trackedFrame)
					
						#Writes the rectangle frame
						writer.write(trackedFrame)

		#Makes the current frame the previous frame to compare against
		prevMaskedFrame = maskedFrame
		
		k = cv2.waitKey(framerate) #Waits for key to be pressed
        
		if (k == 80) or (k == 112): #P or p
			if framerate == 0: #If the loop is stopped
				framerate = 24
				print("Resuming Code")
			else: #If the loop is running
				print("Pausing Code")
				framerate = 0 #Stopps loop until button is pressed
        
		if (k & 0xff) == 27 or (k & 0xff) == 81 or (k & 0xff) == 113:
			print("Quitting") #Esc, Q, or q
			break 

	#Cleanup for video writer
	writer.release()

	return writer

if __name__ == '__main__':

	import ipcv
	import cv2
	import os.path
	import time

	home = os.path.expanduser('~')
	fileFolder = home + os.path.sep + \
				'src/python/examples/data/LabFeatureTrack/'

	#videoFile = fileFolder + 'LabFullRes.mov'
	#videoFile = fileFolder + 'Lab720p.mov'
	videoFile = fileFolder + 'Lab480p.mov'

	video = cv2.VideoCapture(videoFile)
	verbose = False
	speed = True
	background = "gaussian_mixture"
	#background = "threshold"
	videoTime = video.get(7)/video.get(5) #Total number of frames/fps

	startTime= time.clock()
	trackedVideo = ipcv.feature_tracking(video, verbose, speed, background)
	elapsedTime= time.clock()-startTime

	print("It took {0}[s] to track a {1}[s] video".format(elapsedTime, videoTime))

	video.release()
	action = ipcv.flush()

