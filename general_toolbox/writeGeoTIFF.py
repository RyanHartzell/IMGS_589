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


def writeGeoTIFF(image, metadata, fileName):
	from os.path import basename, dirname
	from osgeo import gdal
	from osgeo import osr
	import os

	geoTiffDir = dirname(fileName) + "/geoTiff"
	#Creates a geotiff directory
	if not os.path.exists(geoTiffDir):
		#If the geoTiff directory does not exist it makes the directory
		os.makedirs(geoTiffDir)

	fileNumber = basename(fileName)[:-6]
	geoTiff = geoTiffDir + '/' + fileNumber + '.tiff'
	height, width, channels = image.shape
	driver = gdal.GetDriverByName( 'GTiff' )
	ds = driver.Create( geoTiff, width, height, channels, gdal.GDT_Float64)
	geoTransform = ([0,1,0,0,0,1])
	ds.SetGeoTransform(geoTransform)
	srs = osr.SpatialReference(wkt = "")
	ds.SetProjection(srs.ExportToWkt())
	for band in range(1, image.shape[2]+1):
		ds.GetRasterBand(band).WriteArray(image[:,:,band-1])
		ds.GetRasterBand(band).FlushCache()
	ds = None

	return geoTiff

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
	cv2.waitKey(0)


if __name__ == "__main__":
	if __package__ is None:
		import sys
		from os import path
		sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
		from ImageRegistration.correlateImages import OrderImagePairs
		from ImageRegistration.registerMultiSpectral import stackImages
	else:
		from ..ImageRegistration.correlateImages import OrderImagePairs
		from ..ImageRegistration.registerMultiSpectral import stackImages
	from metadataReader import metadataGrabber



	images = '/cis/otherstu/gvs6104/DIRS/20170928/150flight/000/'

	im1 = images + 'IMG_0058_1.tif'
	im2 = images + 'IMG_0058_2.tif'
	im3 = images + 'IMG_0058_3.tif'
	im4 = images + 'IMG_0058_4.tif'
	im5 = images + 'IMG_0058_5.tif'

	imageList = [im1, im2, im3, im4, im5]
	matchOrder = OrderImagePairs(imageList, addOne=True)
	imageStack = stackImages(imageList, matchOrder)
	metadataDict = metadataGrabber(im1)

	geoTiff = writeGeoTIFF(imageStack, metadataDict, im1)

	showGeoTIFF(geoTiff)


