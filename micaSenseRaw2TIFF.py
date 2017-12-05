"""
title::
	MicaSense Image Registration Workflow Main File
description::
	Creates a GeoTiff from the given MicaSense Files
attributes::
	TBD
author::
	Geoffrey Sasaki
copyright::
	Copyright (C) 2017, Rochetser Institute of Technology
"""

import sys
import argparse
import os
import glob
import numpy as np
import time
import csv
import sys
from fileStructure.fixMicaSenseStructure import fixNamingStructure
from geoTIFF.createGeoTIFF import writeGeoTIFF, showGeoTIFF, writeGPSLog
from geoTIFF.normalizeDC import normalizeISOShutter
from geoTIFF.metadataReader import metadataGrabber
from registration.correlateImages import OrderImagePairs
from registration.createImageStack import stackImages

if sys.version_info[0] == 2:
	import Tkinter as tkinter
	import ttk
	import tkFileDialog as filedialog
else:
	import tkinter
	from tkinter import filedialog, ttk

root = tkinter.Tk()
root.withdraw()
root.update()

parser = argparse.ArgumentParser(description='Create geotiff files for micasense')
parser.add_argument('-i', '--input', type=str, help="An iput directory with RAW Tiffs")
parser.add_argument('-o', '--output',type=str, help="An output directory to put GeoTiffs")
args = parser.parse_args()
flightDirectory = args.input
geoTiffDir = args.output

if flightDirectory is None:
	#IF MULTIPLE DIRECTORIES ARE SELECTED THEN PARALLEL PROCESS THEM
	#flightDirectory = "/cis/otherstu/gvs6104/DIRS/20170928/150flight"
	initialdir = os.getcwd()
	initialdir = "/cis/otherstu/gvs6104/DIRS/"
	flightDirectory = filedialog.askdirectory(initialdir=initialdir,
				title="Choose the RAW MicaSense .tif directory")
	if flightDirectory == '':
		sys.exit()
if geoTiffDir is None:
	geoTiffDir = filedialog.askdirectory(initialdir=os.path.split(flightDirectory)[0],
				title="Choose the directory to place the GeoTiffs")
startTime = time.time()
#print(flightDirectory)
subdirs = glob.glob(flightDirectory+'/*/')
if len(subdirs) != 0 and any("geoTiff" not in s for s in subdirs):
	print("Fixing the naming structure of the {0} directory".format(flightDirectory))
	processedDirectory = fixNamingStructure(flightDirectory)
	#msg = "No subdirectories were found in the specified directory."
	#raise ValueError (msg)
else:
	processedDirectory = flightDirectory

tiffList = sorted(glob.glob(processedDirectory + '/*.tif'))
if len(tiffList)%5 != 0:
	msg = "The number of tiffs in the {0} directory is not divisible by 5".format(processedDirectory)
	raise ValueError(msg)
#imageName = os.path.basename(tiffList[0])

root.deiconify()
status_text = tkinter.StringVar()
label = tkinter.Label(root, textvariable=status_text)
label.pack()
progress_variable = tkinter.DoubleVar()
progressbar = ttk.Progressbar(root, variable=progress_variable,
											maximum=len(tiffList)//5)
progressbar.pack()
root.title("Conversion Progress")
print("Registering RAW imagery and writing out as geotiff.")
print(processedDirectory)
#print(os.path.split(os.path.split(processedDirectory)[0])[0])
with open(os.path.split(os.path.split(processedDirectory)[0])[0]+ "/GPSLog.csv",'w') as resultFile:
	wr = csv.writer(resultFile)

	for images in range(0,len(tiffList),5):
		imageList = [tiffList[images], tiffList[images+1], tiffList[images+2],
					tiffList[images+3], tiffList[images+4]]

		imageOrderDict = {}
		for image in imageList:
			imageDict = metadataGrabber(image)
			imageWavelength = imageDict['Xmp.DLS.CenterWavelength']
			imageOrderDict[image] = imageWavelength
		imageList = sorted(imageOrderDict, key=imageOrderDict.get, reverse=False)

		matchOrder = OrderImagePairs(imageList, addOne=True)
		if matchOrder is None:
			continue
		imageStack, goodCorr = stackImages(imageList, matchOrder,'orb', crop=False)
		if goodCorr:
			normStack = normalizeISOShutter(imageStack, imageList)
			geoTiff = writeGeoTIFF(normStack, imageList, geoTiffDir)
			os.chmod(geoTiff, 0o777)
			logLine = writeGPSLog(imageList[0],geoTiff)
			wr.writerow(logLine)
			#showGeoTIFF(geoTiff)

		progress_variable.set(images//5)
		status_text.set("Writing out GeoTIFF: {0}/{1}".format(
									images//5,len(tiffList)//5))
		root.update_idletasks()

totalTime = time.time()-startTime
print("This took {0}m {1:.2f}s for {2} images.".format(int(totalTime//60),
										totalTime%60, len(tiffList)))
print("You now have {0} geoTiffs.".format(len(glob.glob(geoTiffDir+"*.tiff"))))

root.update()
root.destroy()
