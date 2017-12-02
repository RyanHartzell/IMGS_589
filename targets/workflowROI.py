def switchFrame(imagePath):
	#imagePath, (str) leads to directory where the imagery is stored
	import numpy as np
	import cv2
	import os
	import sys
	from osgeo import gdal

	fileNames = sorted(os.listdir(imagePath))
	imageCount = len(fileNames)

	#initialize
	currentIm = imagePath + fileNames[0]

	mapName = 'Select the first image with the calibration panels.'

	print('Use "d" to advance the images, and "a" to go back.')
	print('Find the image where you can find the target panel.')
	print('Use "esc" key once you are on that image.')

	index = 0
	while True:
		currentIm = imagePath + fileNames[index] #read in the image 
		displayImage = mica2BGR(currentIm)

		cv2.namedWindow(mapName, cv2.WINDOW_AUTOSIZE) #resize and display the image
		im = cv2.imshow(mapName, cv2.resize(displayImage, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))

		response = cv2.waitKey(33) #utilize user responses to move forward or backwards in sequence of imagery
		if response == ord('d'):
			index += 1
		elif response == ord('a'):
			index += -1
		elif response == 27:
			break

	cv2.destroyWindow(mapName)
	return imagePath + fileNames[index], index



#PYTHON TEST HARNESS
if __name__ == '__main__':

	import cv2
	import os
	import time
	import numpy as np
	import scipy
	import scipy.misc
	from osgeo import gdal
	from ROIExtraction import *
	import sys
	sys.path.append("..")
	import geoTIFF

	## USER INPUTS
	geotiffFolderName = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/'
	tsvFilename = '/cis/otherstu/gvs6104/DIRS/20171102/GroundDocumentation/datasheets/Flight_Notes.tsv'
	txtDestination = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/Flight1445.csv'
	##


	# Get all filenames within this flight directory
	fileNames = sorted(os.listdir(geotiffFolderName))
	imageCount = len(fileNames)

	##Create windows outside of loop so they aren't constantly being deleted/created
	currentIm_tag = 'Current Geotiff'
	cv2.namedWindow(currentIm_tag, cv2.WINDOW_AUTOSIZE) #resize and display the image

	zoomName = 'Zoomed region for easier point selection.'
	cv2.namedWindow(zoomName, cv2.WINDOW_AUTOSIZE)
	zoom = cv2.imshow(zoomName, np.zeros((200,200)))

	## Data to be read in once-per-flight
	times,targets,targetdescriptor = fieldData(tsvFilename)

	##Create the textfile that the data will be written out to
	with open(txtDestination, 'w') as currentTextFile:



	##START MAIN LOOP
	currentImIndex = 0
	while True:
		currentFilename = geotiffFolderName + fileNames[currentImIndex]
		currentGeotiff, displayImage = getDisplayImage(currentFilename)
		im = cv2.imshow(currentIm_tag, displayImage)

		while True:
			#get the coordinates of the ROI from the user
			pointsX, pointsY = selectROI(currentIm_tag, displayImage)

			#ask user for input of the current target
			currentTargetNumber = assignTargetNumber()

			#compute the statistics that will be written out, from the ROI coords
			maskedIm, ROI_image, mean, stdev, centroid = computeStats(currentGeotiff, currentFilename, pointsX, pointsY)

			#get metadata
			irradianceDict, frametime = micasenseRawData(currentFilename)
			filenumber = bestSVC(frametime,currentTargetNumber,times,targets,targetdescriptor)


			currentTextFile.write('here\'s our stuff:   {0}   {1}   {2}'.format(filenumber,mean,stdev,centroid,frametime,irradianceDict[1]))




			#Commands corresponding to changing the current GEOTIFF that is being operated on
			response = cv2.waitKey(33) #utilize user responses to move forward or backwards in sequence of imagery
			if response == ord('d'):
				currentImIndex += 1
			elif response == ord('a'):
				currentImIndex += -1
			elif response == 27:
				break

	cv2.destroyWindow(currentIm_tag)


