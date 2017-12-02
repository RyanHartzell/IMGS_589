
def getDisplayImage(geotiffFilename):
	import numpy as np
	import cv2
	from osgeo import gdal

	#Get GEOTIFF
	imageStack = gdal.Open(geotiffFilename).ReadAsArray()
	imageStack = np.moveaxis(imageStack, 0, -1)
	#print(imageStack.dtype)

	#crop
	#width = imageStack.shape[1]
	#radius = width // 4
	focalLen, focalRes, angle = 5.5, 266.66667, 10
	radius = int(focalLen*focalRes*np.tan(np.deg2rad(angle/2)))
	imageCenter = (imageStack.shape[0]//2, imageStack.shape[1]//2)

	circleMask = np.full(imageStack.shape[0:2], 0,  dtype=imageStack.dtype)
	cv2.circle(circleMask, (imageCenter[1],imageCenter[0]), int(radius), (1,1,1), -1)
	circleMask = np.repeat(circleMask[:,:,np.newaxis], imageStack.shape[2])
	circleMask = circleMask.reshape(imageStack.shape)
	imageStackMasked = imageStack*circleMask

	imageStack_crop = imageStackMasked[imageCenter[0]-radius:imageCenter[0]+radius,imageCenter[1]-radius:imageCenter[1]+radius, :]

	#band1 = imageStack_crop[:,:,0]
	#band2 = imageStack_crop[:,:,1]
	#band3 = imageStack_crop[:,:,2]
	#band4 = imageStack_crop[:,:,3]
	#band5 = imageStack_crop[:,:,4]


	#displayImage = np.dstack((band1,band2,band3)).astype(np.uint8)
	displayImage = imageStack_crop[:,:,0:3].astype(np.uint8) #RGB
	return imageStack_crop, displayImage


def selectROI(mapName, im):
	#mapName, (str)
	import numpy as np
	import cv2
	#import ipcv
	import PointsSelected
	#utilize 'PointsSelected' to get the search window, manual input
	p = PointsSelected.PointsSelected(mapName, verbose=False)
	p.clearPoints()

	while p.number() < 4:
		# if p.number() > 1:
		# 	points = np.asarray(list(zip(p.x(), p.y())), np.int32)
		# 	points = points.reshape((-1,1,2))
		# 	im = cv2.polylines(im.copy(), [points], True, (0,0,255))
		# 	cv2.imshow(mapName, im)
		# elif p.number == 1:
		if p.number() == 1:
			im = cv2.circle(im.copy(),(p.x()[-1],p.y()[-1]), 2, (0,0,255), -1)
			cv2.imshow(mapName, im)

		if p.number() >= 2:
			im = cv2.circle(im.copy(),(p.x()[-1],p.y()[-1]), 2, (0,0,255), -1)
			im = cv2.line(im.copy(),(p.x()[-2],p.y()[-2]),(p.x()[-1],p.y()[-1]),(255,0,0),1)
			cv2.imshow(mapName, im)

		cv2.waitKey(100)

	# draw final point
	im = cv2.circle(im.copy(),(p.x()[-1],p.y()[-1]), 2, (0,0,255), -1)
	points = np.asarray(list(zip(p.x(), p.y())), np.int32)
	points = points.reshape((-1,1,2))
	im = cv2.polylines(im.copy(), [points], True, (255,0,0))
	cv2.imshow(mapName, im)
	cv2.waitKey(100)

	return p.x(), p.y()

def selectZoomWindow(mapName, zoomName):
	#mapName, (str)
	import numpy as np
	import cv2

	# draw zoom region on RIGHT MOUSE CLICK (make separate class for this)

	pass

def assignTargetNumber():
	#no input required
	currentTargetNumber = input("Enter Target Number. Then press 'enter'.\n")
	return currentTargetNumber



def computeStats(currentCroppedIm, geotiffFilename, pointsX, pointsY):
	#currentCroppedIm, (array)
	#geotiffFilename, (str)

	import numpy as np
	import cv2
	from osgeo import gdal

	#Create poly mask
	mask = np.zeros((currentCroppedIm.shape[0], currentCroppedIm.shape[1]))
	polyMaskCoords = np.asarray(list(zip(pointsX, pointsY)))
	cv2.fillConvexPoly(mask, polyMaskCoords, 1.0)

	#apply the single channel mask to each of the five bands in 'currentCroppedIm'
	mask[np.where(mask == 0)] = np.nan
	mask = mask.astype(currentCroppedIm.dtype)

	#print(currentCroppedIm[:,:,0])
	#print(currentCroppedIm.dtype)

	#ROI_image = mask * currentCroppedIm.T
	ROI_image = np.dstack(((mask * currentCroppedIm[:,:,0]), (mask * currentCroppedIm[:,:,1]), (mask * currentCroppedIm[:,:,2]), (mask * currentCroppedIm[:,:,3]), (mask * currentCroppedIm[:,:,4])))

	#calculate statistics
	mean = []
	stdev = []
	for i in [0, 1, 2, 3, 4]:
		mean.append(np.nanmean(ROI_image[:,:,i]))
		stdev.append(np.nanstd(ROI_image[:,:,i]))

	#calculate centroid
	orignalImage = gdal.Open(geotiffFilename).ReadAsArray()
	orignalImage = np.moveaxis(orignalImage, 0, -1)
	print(pointsX, orignalImage.shape[1], currentCroppedIm.shape[1])
	print(pointsY, orignalImage.shape[0], currentCroppedIm.shape[0])
	pointsX = np.array(pointsX)+orignalImage.shape[1]//2-currentCroppedIm.shape[1]//2
	pointsY = np.array(pointsY)+orignalImage.shape[0]//2-currentCroppedIm.shape[0]//2
	centroid = [int(np.around(np.mean(pointsX))) ,int(np.around(np.mean(pointsY)))]

	return mask, ROI_image, mean, stdev, centroid

def micasenseRawData(geotiffFilename):
	from geoTIFF import metadataReader
	import time

	irradianceDict = {}
	#For each band we are going to record a value for irradiance
	for band in np.arange(1,6):
		rawextension = '_{}.tif'.format(str(band))
		rawFilename = geotiffFilename[:-21] + 'processed/' + geotiffFilename[-13:-5] + rawextension
		#print('rawFilename',rawFilename)
		metadatadict = metadataReader.metadataGrabber(rawFilename)
		irradianceDict[band] = float(metadatadict['Xmp.DLS.SpectralIrradiance'])

	#For a single image we record the time in which the frame was captured
	t = time.strptime(metadatadict['timeStamp'].split('T')[-1].split('.')[0],'%H:%M:%S')
	frametime = (t.tm_hour - 5) * 60 + t.tm_min

	return irradianceDict, frametime

def fieldData(tsvFilename):
	import numpy as np

	fulltext = np.loadtxt(tsvFilename,skiprows = 4, dtype = str, delimiter = '\t')

	times = fulltext[:,0]
	times = times[1:]
	for index in np.arange(np.size(times)):
		timestring =  times[index]
		hours = int(timestring[0:2])
		minutes = int(timestring[2:4])
		totalmin = hours * 60 + minutes
		times[index] = totalmin
	times = times.astype(int)

	filenumbers = fulltext[:,2]
	filenumbers = filenumbers[1:]

	targetdescriptor = fulltext[:,1]
	targetdescriptor = targetdescriptor[1:]

	return times, filenumbers, targetdescriptor

def targetNumtoStr(targetnumber):
	if targetnumber == '1':
		targetstring = 'White Tri'
	elif targetnumber == '2':
		targetstring = 'Medium Gray Tri'
	elif targetnumber == '3':
		targetstring = 'Dark Gray Tri'
	elif targetnumber == '4':
		targetstring = 'Black Cal Panel'
	elif targetnumber == '5':
		targetstring = 'White Cal Panel'
	elif targetnumber == '6':
		targetstring = 'Asphalt'
	elif targetnumber == '7':
		targetstring = 'Grass'
	elif targetnumber == '8':
		targetstring = 'Concrete'
	elif targetnumber == '9':
		targetstring = 'Red Felt (Sun)'
	elif targetnumber == '10':
		targetstring = 'Blue Felt (Sun)'
	elif targetnumber == '11':
		targetstring = 'Green Felt (Sun)'
	elif targetnumber == '12':
		targetstring = 'Brown Felt (Sun)'
	elif targetnumber == '13':
		targetstring = 'White Cal Panel (Shadow)'
	elif targetnumber == '14':
		targetstring = 'Black Cal Panel (Shadow)'
	elif targetnumber == '15':
		targetstring = 'Red Felt (Shadow)'
	elif targetnumber == '16':
		targetstring = 'Blue Felt (Shadow)'
	elif targetnumber == '17':
		targetstring = 'Green Felt (Shadow)'
	elif targetnumber == '18':
		targetstring = 'Brown Felt (Shadow)'
	else:
		print('Invalid Target Number')

	return targetstring


def bestSVC(frametime,targetnumber,times,filenumbers,targetdescriptor):
	targetstring = targetNumtoStr(targetnumber)
	possibleSVC = np.where(targetdescriptor == targetstring)[0]
	test = np.abs(times[possibleSVC]-frametime)
	tset = test[::-1]
	bestindex = len(tset) - np.argmin(tset) - 1
	filenumberindex = possibleSVC[bestindex]
	filenumber = filenumbers[filenumberindex]
	return filenumber

	return irradianceDict, frametime

def fieldData(tsvFilename):
	import numpy as np

	fulltext = np.loadtxt(tsvFilename,skiprows = 4, dtype = str, delimiter = '\t')

	times = fulltext[:,0]
	times = times[1:]
	for index in np.arange(np.size(times)):
		timestring =  times[index]
		hours = int(timestring[0:2])
		minutes = int(timestring[2:4])
		totalmin = hours * 60 + minutes
		times[index] = totalmin
	times = times.astype(int)

	filenumbers = fulltext[:,2]
	filenumbers = filenumbers[1:]

	targetdescriptor = fulltext[:,1]
	targetdescriptor = targetdescriptor[1:]

	return times, filenumbers, targetdescriptor

def bestSVC(frametime,targetnumber,times,filenumbers,targetdescriptor):
	targetstring = targetNumtoStr(targetnumber)
	possibleSVC = np.where(targetdescriptor == targetstring)[0]
	test = np.abs(times[possibleSVC]-frametime)
	tset = test[::-1]
	bestindex = len(tset) - np.argmin(tset) - 1
	filenumberindex = possibleSVC[bestindex]
	filenumber = filenumbers[filenumberindex]
	return filenumber

#PYTHON TEST HARNESS
if __name__ == '__main__':

	import cv2
	import os
	import time
	import numpy as np
	import scipy
	import scipy.misc
	from osgeo import gdal

	import sys
	sys.path.append("..")
	#os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir)))
	import geoTIFF

	geotiffFilename = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/IMG_0181.tiff'
	#geotiffFilename = '/cis/otherstu/gvs6104/DIRS/20171108/Missions/1300_225ft/micasense/geoTiff/IMG_0188.tiff'

	#get the geotiff image (5 band) and color (3 band)
	geoTiffImage, displayImage = getDisplayImage(geotiffFilename)
	#print(geoTiffImage.dtype)
	#print(np.max(geoTiffImage))

	mapName = 'Select corners for the target area.'
	cv2.namedWindow(mapName, cv2.WINDOW_AUTOSIZE)
	cv2.imshow(mapName, (displayImage/np.max(displayImage)*255).astype(np.uint8))

	zoomName = 'Zoomed region for easier point selection.'
	cv2.namedWindow(zoomName, cv2.WINDOW_AUTOSIZE)
	zoom = cv2.imshow(zoomName, np.zeros((200,200)))

	#select the points for a target in the scene
	pointsX, pointsY = selectROI(mapName, displayImage)
	# call updater for zoomed function each time in the while loop (and in selectROI!!!)

	#ask user for input of the current target
	currentTargetNumber = assignTargetNumber()

	maskedIm, ROI_image, mean, stdev, centroid = computeStats(geoTiffImage, geotiffFilename, pointsX, pointsY)

	cv2.destroyWindow(mapName)

	tsvFilename = '/cis/otherstu/gvs6104/DIRS/20171109/GroundDocumentation/datasheets/Flight_Notes.tsv'
	times,targets,targetdescriptor = fieldData(tsvFilename)

	irradianceDict, frametime = micasenseRawData(geotiffFilename)
	print(irradianceDict[1],irradianceDict[2],irradianceDict[3],irradianceDict[4],irradianceDict[5])
	filenumber = bestSVC(frametime,currentTargetNumber,times,targets,targetdescriptor)
	print(filenumber)
	print(mean)

	with open('Target_Data_Test.txt', 'w') as stuff:
		stuff.write('here\'s our stuff:   {0}   {1}   {2}'.format(filenumber,mean,stdev,centroid,frametime,irradianceDict[1]))
