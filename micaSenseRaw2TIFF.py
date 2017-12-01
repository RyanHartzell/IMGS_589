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
import os
import glob
import numpy as np
import time
import csv
import sys
from fileStructure.fixMicaSenseStructure import fixNamingStructure
from geoTIFF.createGeoTIFF import writeGeoTIFF, showGeoTIFF, writeGPSLog
from geoTIFF.normalizeDC import normalizeISOShutter
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

#IF MULTIPLE DIRECTORIES ARE SELECTED THEN PARALLEL PROCESS THEM
#flightDirectory = "/cis/otherstu/gvs6104/DIRS/20170928/150flight"
initialdir = os.getcwd()
initialdir = "/cis/otherstu/gvs6104/DIRS/"
flightDirectory = filedialog.askdirectory(initialdir=initialdir,
			title="Choose the RAW MicaSense .tif directory")
if flightDirectory == '':
	sys.exit()
geoTiffDir = filedialog.askdirectory(initialdir=initialdir,
			title="Choose the directory to place the GeoTiffs")
startTime = time.time()
#print(flightDirectory)
subdirs = glob.glob(flightDirectory+'/*/')
if len(subdirs) != 0 and any("geoTiff" not in s for s in subdirs):
	processedDirectory = fixNamingStructure(flightDirectory)
	#msg = "No subdirectories were found in the specified directory."
	#raise ValueError (msg)

tiffList = sorted(glob.glob(processedDirectory + '/*.tif'))
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

with open(os.path.split(flightDirectory)[0]+ "/GPSLog.csv",'w') as resultFile:
	wr = csv.writer(resultFile)

	for images in range(0,len(tiffList),5):
		im1 = tiffList[images]
		im2 = tiffList[images+1]
		im3 = tiffList[images+2]
		im4 = tiffList[images+3]
		im5 = tiffList[images+4]

		imageList = [im1, im2, im3, im4, im5]
		matchOrder = OrderImagePairs(imageList, addOne=True)
		imageStack, goodCorr = stackImages(imageList, matchOrder,'orb', crop=False)

		if goodCorr:
			normStack = normalizeISOShutter(imageStack, imageList)
			geoTiff = writeGeoTIFF(normStack, im1, geoTiffDir)
			logLine = writeGPSLog(im1,geoTiff)
			wr.writerow(logLine)
			#showGeoTIFF(geoTiff)

		progress_variable.set(images//5)
		status_text.set("Writing out GeoTIFF: {0}/{1}".format(
									images//5,len(tiffList)//5))
		root.update_idletasks()

totalTime = time.time()-startTime
print("This took {0}m {1:.2f}s for {2} images.".format(int(totalTime//60),
										totalTime%60, len(tiffList)))

root.update()
root.destroy()
