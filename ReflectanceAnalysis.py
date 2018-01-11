from LUTgenerator import findReflectance
import numpy as np
from targets import svcReader
import cv2
import os.path
import os
import sys
import csv
import glob
from osgeo import gdal

def targetanalysis(csvfile,cameraResponseSR,svcdirectory,reflectanceimagedirectory):
	data = np.loadtxt(csvfile, dtype = str , delimiter = ',', skiprows = 1)

	svcfilename = data[0][31]
	SVCtargetSR = svcdirectory + '*' + 'T' + svcfilename.zfill(3) + '.sig'
	SVCtargetSR = glob.glob(SVCtargetSR)[0]
	print(SVCtargetSR)
	bands = ['Blue','Green','Red','Red Edge','NIR']
	BEreflect = {}
	for bandname in bands:
		BEreflect[bandname] = findReflectance(SVCtargetSR,cameraresponseSR,bandname)
		print(bandname,BEreflect[bandname])

	imagename = 'ref' + data[0][1]	
	#pointsX = np.asarray(data[0][22:26],dtype = int)
	#pointsX = list(map(int(data[0][22:26])))
	#pointsX = [int(numeric_string) for numeric_string in data[0][22:26]]
	#pointsX = list(data[0][22:26])
	pointsX = data[0][22:26]
	pointsX = [int(float(numeric_string)) for numeric_string in pointsX]
	#pointsX = map(int, data[0][22:26])
	print(type(pointsX))
	pointsY = data[0][26:30]
	pointsY = [int(float(numeric_string)) for numeric_string in pointsY]

	geoTiff = reflectanceimagedirectory + imagename
	imageStack = gdal.Open(geoTiff).ReadAsArray()
	imageStack = np.moveaxis(imageStack, 0 ,-1)
	dim = imageStack.shape
	mask = np.zeros((dim[0], dim[1]))
	polyMaskCoords = np.asarray(list(zip(pointsX, pointsY)),dtype=np.int32)
	print(polyMaskCoords)
	cv2.fillConvexPoly(mask, polyMaskCoords, 1.0)
	mask[np.where(mask == 0)] = np.nan
	ROI_image = np.dstack(((mask * imageStack[:,:,0]), (mask * imageStack[:,:,1]), (mask * imageStack[:,:,2]), (mask * imageStack[:,:,3]), (mask * imageStack[:,:,4])))
	mean = []
	stdev = []
	for i in [0, 1, 2, 3, 4]:
		mean.append(np.nanmean(ROI_image[:,:,i]))
		stdev.append(np.nanstd(ROI_image[:,:,i]))
	print(mean)
	print(stdev)

if __name__ == '__main__':
	csvfile = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1230_150ft/micasense/Flight_20171109T1230_150ft_kxk8298.csv'
	cameraresponseSR = '/research/imgs589/imageLibrary/DIRS/MonochrometerTiffs/Spectral_Response.csv'
	svcdirectory = '/research/imgs589/imageLibrary/DIRS/20171109/SVC/'
	reflectanceimagedirectory = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1230_150ft/micasense/reflectanceproduct/'
	targetanalysis(csvfile,cameraresponseSR,svcdirectory,reflectanceimagedirectory)