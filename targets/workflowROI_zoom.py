


import cv2
import os
import numpy as np
from osgeo import gdal
from ROIExtraction import *
import sys
sys.path.append("..")
import geoTIFF
import glob
import csv
import argparse
import getpass
import tkinter
from tkinter import filedialog, ttk
root = tkinter.Tk()
root.withdraw()
root.update()
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
#print(screenWidth, screenHeight)
userName = getpass.getuser()



#example:
#python3 workflowROI.py -g /cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/ -t /cis/otherstu/gvs6104/DIRS/20171102/GroundDocumentation/datasheets/Flight_Notes.tsv -s 2 -f IMG_0180.tiff


# individual example inputs
# geotiffFolderName = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/'
# tsvFilename = '/cis/otherstu/gvs6104/DIRS/20171102/GroundDocumentation/datasheets/Flight_Notes.tsv'
# #txtDestination = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/Flight1445_' + userName + '.csv'
# stepNumber = 2 #do every other image, or every image, ...

# startFrameNumber = 0 #can equal int or filename as string
# startFrameNumber = 'IMG_0000.tiff'
# ##


parser = argparse.ArgumentParser(description='Collect user inputs for ROI extraction process')
parser.add_argument('-g', '--geotiffFolderName', type=str, help='The geotiff image directory')
parser.add_argument('-t', '--tsvFilename', type=str, help='The filename with the .tsv')
parser.add_argument('-s', '--stepNumber', type=int, help='How many images you want to skip')
parser.add_argument('-r', '--scaleFactor', type=float, help='How much would you like to resize the images by for viewing default: 2')
parser.add_argument('-a', '--angle', type=float, help='The angle away from nadir to crop the images to')
parser.add_argument('-f', '--startFrameNumber', help='Image to start at, can be string or index (int)')

args = parser.parse_args()
geotiffFolderName = args.geotiffFolderName
tsvFilename = args.tsvFilename
stepNumber = args.stepNumber
startFrameNumber = args.startFrameNumber
scaleFactor = args.scaleFactor
angle = args.angle

if geotiffFolderName is None:
	geotiffFolderName = filedialog.askdirectory(initialdir = "/cis/otherstu/gvs6104/DIRS/",
											title="Choose the geotiff image directory")
	if geotiffFolderName == "":
		sys.exit()
	else:
		geotiffFolderName = geotiffFolderName + os.path.sep
if tsvFilename is None:
	splitted = geotiffFolderName.split('/')
	tsvDirectory = '/'.join(splitted[:6]) + os.path.sep + 'GroundDocumentation/datasheets/'
	if os.path.isfile(tsvDirectory + 'Flight_Notes.tsv'):
		tsvFilename = tsvDirectory + 'Flight_Notes.tsv'
	else:
		tsvFilename = filedialog.askopenfilename(initialdir = tsvDirectory, title="Choose the Flight Notes [.tsv]",
			filetypes=[("Tab Seperated Values", "*.tsv"), ("Comma Seperated Values", "*.csv"),("Excel Files", "*.xlsx *.xls")])
		if tsvFilename == "":
			sys.exit()

if stepNumber is None:
	stepNumber = 2
	#stepNumber = int(input('Type number for how many images you want to skip \n'))
if scaleFactor is None:
	scaleFactor = 2
if angle is None:
	angle = 10

if startFrameNumber is None:
	startFrameNumber = input('Type number (index) or filename (string) for which image to start at \n')
	try:
		startFrameNumber = int(startFrameNumber) #this will only work (convert to int) if it is an index
	except Exception:
		pass

flightNumber = os.path.basename(os.path.abspath(os.path.join(geotiffFolderName, '../..')))
flightDate = os.path.basename(os.path.abspath(os.path.join(geotiffFolderName, '../../../..')))
flightInfo = 'Flight_' + flightDate + 'T' + flightNumber + '_'
txtDestination = os.path.abspath(os.path.join(geotiffFolderName, os.pardir)) + os.path.sep + flightInfo + userName + '.csv'

# Get all filenames within this fliinterght directory
#fileNames = sorted(os.listdir(geotiffFolderName)) #Does not handle files that arn't *.tiff
listofFiles = sorted(glob.glob(geotiffFolderName + "*.tiff"))
fileNames = []
for name in listofFiles:
	fileNames.append(os.path.basename(name))

imageCount = len(fileNames)
imageNameDict = dict(enumerate(fileNames))
imageNameDict = {v:k for k,v in imageNameDict.items()}

try:
	startFrameNumber= int(startFrameNumber)
	if startFrameNumber > imageCount:
		startFrameNumber = 0
except Exception as e:
	pass

if type(startFrameNumber) == str:
	try:
		startFrameNumber = int(imageNameDict[startFrameNumber])
	except:
		startFrameNumber = 0

##Create windows outside of loop so they aren't constantly being deleted/created
currentIm_tag = 'Current Geotiff'
cv2.namedWindow(currentIm_tag, cv2.WINDOW_AUTOSIZE) #resize and display the image

#zoomName = 'Zoomed region for easier point selection.'
#cv2.namedWindow(zoomName, cv2.WINDOW_AUTOSIZE)
#zoom = cv2.imshow(zoomName, np.zeros((200,200)))

## Data to be read in once-per-flight
times,targets,targetdescriptor = fieldData(tsvFilename)

##Create the textfile that the data will be written out to
if os.path.isfile(txtDestination) == True:
	writeMode = 'a'
else:
	writeMode = 'w'

with open(txtDestination, writeMode) as currentTextFile:
	writer = csv.writer(currentTextFile, delimiter = ',')
	if writeMode == 'w':
		writer.writerow(['Target Number', 'Frame Number(s) [geoTiff]', 'ELM/Profile',
		'Pixel Resolution', 'Flight Altitude', 'Mean B', 'Mean G', 'Mean R', 'Mean RE',
		 'Mean IR', 'Std B', 'Std G', 'Std R', 'Std RE', 'Std IR', 'Irradiance B',
		 'Irradiance G', 'Irradiance R','Irradiance RE', 'Irradiance IR',
		 'Centroid Coord X', 'Centroid Coord Y','Point X1','Point X2','Point X3','Point X4',
		 'Point Y1','Point Y2','Point Y3', 'Points Y4', 'Nadir Angle','SVC filenumber'])

	##START MAIN LOOP
	currentImIndex = startFrameNumber
	while True:

		if currentImIndex == imageCount:
			print('You have reached the end of the imagery. Nice job.')
			print('You can find the csv file at:' + txtDestination)
			break

		currentFilename = geotiffFolderName + fileNames[currentImIndex]
		currentCroppedIm, displayImage = getDisplayImage(currentFilename, angle, scaleFactor)

		splitIm = np.dsplit(currentCroppedIm, 5)
		falseRE = np.dstack((splitIm[1], splitIm[2], splitIm[3]))
		falseIR = np.dstack((splitIm[1], splitIm[2], splitIm[4]))
		weighted = cv2.addWeighted(splitIm[0],0.2,splitIm[1],0.2,0)
		weighted = cv2.addWeighted(weighted,0,splitIm[2],0.2,0)
		weighted = cv2.addWeighted(weighted,0,splitIm[3],0.2,0)
		weighted = cv2.addWeighted(weighted,0,splitIm[4],0.2,0)

		cv2.imshow(currentIm_tag, displayImage)

		cv2.imshow("False Color [Red Edge]", falseRE/np.max(falseRE))
		cv2.imshow("False Color [Near IR]", falseIR/np.max(falseIR))
		cv2.imshow("Blended", weighted/np.max(weighted))

		print("Do you want to get ROIs in this frame? 'w' for yes, 'a' for back, 'd' for forward.")
		print(fileNames[currentImIndex], 'Index = ', currentImIndex,'/', imageCount)
		userInput = cv2.waitKey(0)
		if userInput == ord('w'):
			print('Ready to accept points.')
			print("Once you are done, enter target number with 2 digits [04], 'n' to redo.")

			#get the coordinates of the ROI from the user
			##RESIZE DISPLAY
			pointsX, pointsY, currentTargetNumber = selectROI(currentIm_tag, displayImage)
			if pointsX is None or pointsY is None or currentTargetNumber is None:
				continue
			#pointsX, pointsY, currentTargetNumber = selectROI(currentIm_tag,
			#		cv2.resize(displayImage, None, fx=scaleFactor, fy=scaleFactor,
			#		interpolation=cv2.INTER_LANCZOS4))

			#RESIZE DISPLAY
			pointsX_resize = []
			pointsY_resize = []
			for i in pointsX:
				newX = i/scaleFactor
				pointsX_resize.append(newX)
			for i in pointsY:
				newY = i/scaleFactor
				pointsY_resize.append(newY)
			pointsX = pointsX_resize
			pointsY = pointsY_resize

			#diffX = (currentGeotiff.shape[1]-displayImage.shape[1])
			#diffY = (currentGeotiff.shape[0]-displayImage.shape[0])

			#currentCroppedIm = currentGeotiff[diffY//2:(diffY//2)+diffY, diffX//2:(diffX//2)+diffX]
			#compute the statistics that will be written out, from the ROI coords
			maskedIm, ROI_image, mean, stdev, centroid = computeStats(currentCroppedIm,
												currentFilename, pointsX, pointsY)

			#get metadata
			irradianceDict, frametime, altitude, resolution= micasenseRawData(currentFilename)
			filenumber = bestSVC(frametime,currentTargetNumber,times,targets,targetdescriptor)
			#writer.writerow([currentTargetNumber, fileNames[currentImIndex], '', 'Pixel Resolution', 'Flight Altitude', str(mean[0]), str(mean[1]), str(mean[2]), str(mean[3]), str(mean[4]), str(stdev[0]), str(stdev[1]), str(stdev[2]), str(stdev[3]), str(stdev[4]), str(centroid), 'Nadir Angle'])

			#'Target Number', 'Frame Number(s) [geoTiff]',
			#'ELM/Profile', 'Pixel Resolution', 'Flight Altitude', 'Mean B', 'Mean G', 'Mean R',
			#'Mean RE', 'Mean IR', 'Std B', 'Std G', 'Std R',
			#'Std RE', 'Std IR', 'Irradiance B','Irradiance G',
			#'Irradiance R','Irradiance RE', 'Irradiance IR',
			#'Centroid Coord X', 'Centroid Coord Y','Point X1','Point X2',
			#'Point X3','Point X4','Point Y1','Point Y2',
			#'Point Y3', 'Points Y4', 'Nadir Angle','SVC filenumber'

			writer.writerow([currentTargetNumber, fileNames[currentImIndex],
			'', resolution, altitude, str(mean[0]), str(mean[1]), str(mean[2]),
			str(mean[3]), str(mean[4]), str(stdev[0]), str(stdev[1]), str(stdev[2]),
			str(stdev[3]), str(stdev[4]), str(irradianceDict[1]), str(irradianceDict[2]),
			str(irradianceDict[3]), str(irradianceDict[4]), str(irradianceDict[5]),
			str(centroid[0]), str(centroid[1]), str(pointsX[0]), str(pointsX[1]),
			str(pointsX[2]), str(pointsX[3]), str(pointsY[0]), str(pointsY[1]),
			str(pointsY[2]), str(pointsY[3]), '', str(filenumber)])

			print('Line has been written to file.')

		elif userInput == ord('d'):
			currentImIndex += stepNumber
		elif userInput == ord('a'):
			currentImIndex += -stepNumber
		elif userInput == ord('t'):
			newAngle = input("What is the new angle?")
			try:
				angle = float(newAngle)
			except:
				pass
		elif userInput == ord('r'):
			newScaleFactor = input("What is the new scale factor?")
			try:
				scaleFactor = float(newScaleFactor)
			except:
				pass
		elif userInput == 27:
			break
		else:
			continue






	cv2.destroyWindow(currentIm_tag)
	currentTextFile.close()
	print('You can find the csv file at:' + txtDestination)
