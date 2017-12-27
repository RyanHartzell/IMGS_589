"""
title::
	Write GeoTIFF

description::
	This funciton writes out a 5 band raster based GeoTIFF and associated
	csv with the geographic image metadata.
author::
	Geoffrey Sasaki

copyright::
	Copyright (C) 2017, Rochetser Institute of Technology
"""


def writeGeoTIFF(image, imageList, geoTiffDir=None):
	from os.path import basename, dirname
	from geoTIFF.metadataReader import metadataGrabber
	from osgeo import gdal
	from osgeo import osr
	import os

	if geoTiffDir is None:
		geoTiffDir = dirname(fileName) + "/geoTiff/"
		#Creates a geotiff directory

	if not os.path.exists(geoTiffDir):
		#If the geoTiff directory does not exist it makes the directory
		os.makedirs(geoTiffDir)

	fileNumber = basename(imageList[0])[:-6]
	geoTiff = geoTiffDir + fileNumber + '.tiff'
	height, width, channels = image.shape

	driver = gdal.GetDriverByName( 'GTiff' )
	if image.dtype == 'uint8':
		GDT = gdal.GDT_Byte
	elif image.dtype == 'uint16':
		GDT = gdal.GDT_UInt16
	elif image.dtype == 'float32':
		GDT = gdal.GDT_Float32
	elif image.dtype == 'float64':
		GDT = gdal.GDT_Float64

	ds = driver.Create( geoTiff, width, height, channels, GDT)
	pWidth, pHeight = 1.0, 1.0
	X, Y = 0.0, 0.0
	geoTransform = ([X,pWidth,0,Y,0,pHeight])
	ds.SetGeoTransform(geoTransform)
	wktProjection = ''
	#srs = osr.SpatialReference(wkt = "")
	ds.SetProjection(wktProjection)
	for band in range(1, image.shape[2]+1):
		bandNum = ds.GetRasterBand(band)
		#imageDict = metadataGrabber(imageList[band-1], RAW=True)
		#bandNum.SetMetadata(imageDict)
		#bandNum.SetMetadata({'TIFFTAG_DOCUMENTNAME':str(basename(imageList[band-1])),
		#				'TIFFTAG_IMAGEDESCRIPTION':str(imageDict['Xmp.Camera.BandName']),
		#				'TIFFTAG_DATETIME':str(imageDict['Exif.Photo.DateTimeOriginal']),
		#				'TIFFTAG_XRESOLUTION':str(imageDict['Exif.Photo.FocalPlaneXResolution']),
		#				'TIFFTAG_YRESOLUTION':str(imageDict['Exif.Photo.FocalPlaneYResolution']),
		#				'TIFFTAG_RESOLUTIONUNIT':str(imageDict['Exif.Photo.FocalPlaneResolutionUnit'])})
		bandNum.WriteArray(image[:,:,band-1])
	ds.FlushCache()
	ds = None

	return geoTiff

def writeGPSLog(rawImage, geoTiff):
	from geoTIFF.metadataReader import metadataGrabber
	from os.path import basename

	mDict = metadataGrabber(rawImage)
	gName = basename(geoTiff)
	longitude = mDict['Exif.GPSInfo.GPSLongitude']
	#longitude = longitude[0] + longitude[1]/60 + longitude[2]/3600
	strLong = '{0:.8f}'.format(longitude)
	latitude = mDict['Exif.GPSInfo.GPSLatitude']
	#latitude = latitude[0] + latitude[1]/60 + latitude[2]/3600
	strLat = '{0:.8f}'.format(latitude)
	altitude = float(mDict['Exif.GPSInfo.GPSAltitude'])
	strAlt = '{0:.2f}'.format(altitude)
	time = mDict['Exif.Photo.DateTimeOriginal']
	subSec = mDict['Exif.Photo.SubSecTime']
	zuluOffset = str(int(time[11:13])-5)
	#print(zuluOffset)
	time = time.replace(' ', 'T')
	time = time.replace(':','-',2)
	time = time[:11] + zuluOffset + time[13:]
	time = time + '.' + subSec[1:] + 'Z'
	logLine = [gName, strLong, strLat, strAlt, time]
	#logString = ','.join(logLine)
	return logLine

def showGeoTIFF(image):
	import cv2
	import numpy as np
	from osgeo import gdal


	ds = gdal.Open(image).ReadAsArray()
	ds = np.moveaxis(ds, 0, -1)
	band1 = ds[:,:,0]
	band2 = ds[:,:,1]
	band3 = ds[:,:,2]
	band4 = ds[:,:,3]
	band5 = ds[:,:,4]

	displayImage = np.dstack((band1,band2,band3)).astype(np.uint8)

	im = cv2.imshow("RGB GeoTiff", cv2.resize(displayImage, None, fx=0.5, fy=0.5,
											interpolation=cv2.INTER_AREA))
	#im = cv2.imshow("RGB GeoTiff", displayImage)

	cv2.waitKey(10)


if __name__ == "__main__":
	if __package__ is None:
		import sys
		from os import path
		sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
		from registration.correlateImages import OrderImagePairs
		from registration.createImageStack import stackImages
	else:
		from ..registration.correlateImages import OrderImagePairs
		from ..registration.createImageStack import stackImages
	from metadataReader import metadataGrabber

	images = '/cis/otherstu/gvs6104/DIRS/20170928/300flight/000/'

	im1 = images + 'IMG_0128_1.tif'
	im2 = images + 'IMG_0128_2.tif'
	im3 = images + 'IMG_0128_3.tif'
	im4 = images + 'IMG_0128_4.tif'
	im5 = images + 'IMG_0128_5.tif'

	imageList = [im1, im2, im3, im4, im5]
	matchOrder = OrderImagePairs(imageList, addOne=True)
	imageStack, goodCorr = stackImages(imageList, matchOrder, 'orb', crop=True)
	#metadataDict = metadataGrabber(im1)

	geoTiff = writeGeoTIFF(imageStack, im1)
	logLine = writeGPSLog(im1, geoTiff)
	print(logLine)

	#showGeoTIFF(geoTiff)
