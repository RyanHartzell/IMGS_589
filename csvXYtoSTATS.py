import numpy as np
import cv2
from osgeo import gdal

'''
Name:
   csvXYtoSTATS

Description::
   Code for recreating statistical data for an image provided that the image is on hand, and the 
   ROI's defined by 4 (X,Y) points is known

   readCSV - Retrieves the parameters from an old csv
   imgXYtoData - Recalculates statistics given image and points

Inputs::


Version History::
   Started                                                                                  2/05/2018
   Wrote readCSV and imgXYtoData

Current Bugs::
   1) Should include a looping iteration for entire csv's, need to decide if test harness or function
   implementation

Author::
   Kevin Kha
'''

def readCSV(csvfile,row):
	#Read in of necessary parameters from a csv
	data = np.loadtxt(csvfile, dtype = str , delimiter = ',', skiprows = 1)

	target = data[row][0]
	imagename = data[row][1]

	pointsX = data[row][22:26]
	pointsX = [int(float(numeric_string)) for numeric_string in pointsX]
	pointsY = data[row][26:30]
	pointsY = [int(float(numeric_string)) for numeric_string in pointsY]

	return target,imagename,pointsX,pointsY

def imgXYtoData(imagedirectory,geotiff,pointsX,pointsY):
	#Read in of a geotiff, band order correction
	geotiff = imagedirectory + geotiff
	imageStack = gdal.Open(geotiff).ReadAsArray()
	imageStack = np.moveaxis(imageStack, 0 ,-1)
	dim = imageStack.shape
	#Usage of points to create a mask before making statistics
	mask = np.zeros((dim[0], dim[1]))
	polyMaskCoords = np.asarray(list(zip(pointsX, pointsY)),dtype=np.int32)
	cv2.fillConvexPoly(mask, polyMaskCoords, 1.0)
	mask[np.where(mask == 0)] = np.nan
	ROI_image = np.dstack(((mask * imageStack[:,:,0]), (mask * imageStack[:,:,1]), (mask * imageStack[:,:,2]), (mask * imageStack[:,:,3]), (mask * imageStack[:,:,4])))
	mean = []
	stdev = []
	#Data listed by wavelength order, blue,green,red,rededge,infrared
	for i in [0, 1, 2, 3, 4]:
		#Statistics!
		mean.append(np.nanmean(ROI_image[:,:,i]))
		stdev.append(np.nanstd(ROI_image[:,:,i]))

	return mean,stdev

if __name__ == '__main__':
	#Sample Directory Space and CSV
	directory = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/'
	csvfile = directory + 'Flight_20171109T1345_375ft_kxk8298.csv'
	imagedirectory = directory + 'geoTiff/'

	#Call in for parameters to recreate statistics
	target,imagename,pointsX,pointsY = readCSV(csvfile,0)

	print('target {}'.format(target))
	print('imagename {}'.format(imagename))
	print('X values {}'.format(pointsX))
	print('Y values {}'.format(pointsY))

	#Creation of statistics
	mean,stdev = imgXYtoData(imagedirectory,imagename,pointsX,pointsY)
	print('mean values {}'.format(mean))
	print('stdev values {}'.format(stdev))

