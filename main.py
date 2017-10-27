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
from general_toolbox.directoryFix import fixNamingStructure
from general_toolbox.writeGeoTIFF import writeGeoTIFF, showGeoTIFF, writeGPSLog
from ImageRegistration.correlateImages import OrderImagePairs
from ImageRegistration.registerMultiSpectral import stackImages

#import resource

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
flightDirectory = "/cis/otherstu/gvs6104/DIRS/20170928/150flight"
#initialdir = os.getcwd()
#flightDirectory = filedialog.askdirectory(initialdir=initialdir)
#print(flightDirectory)
#fixNamingStructure(flightDirectory)
tiffList = sorted(glob.glob(flightDirectory + '/*.tif'))
imageName = os.path.basename(tiffList[0])

root.deiconify()
status_text = tkinter.StringVar()
label = tkinter.Label(root, textvariable=status_text)
label.pack()
progress_variable = tkinter.DoubleVar()
progressbar = ttk.Progressbar(root, variable=progress_variable, 
											maximum=len(tiffList)//5)
progressbar.pack()

gpsLog = []
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
		#Normalize Image Stack
		geoTiff = writeGeoTIFF(imageStack, im1)
		logLine = writeGPSLog(im1)
		gpsLog.append(logString)
		#showGeoTIFF(geoTiff)
	progress_variable.set(images//5)
	status_text.set("Writing out GeoTIFF: {0}/{1}".format(
								images//5,len(tiffList)//5))
	root.update_idletasks()

gpsLog = np.asarray(gpsLog)
numpy.savetxt(flightDirectory+"/GPSLog.csv", gpsLog, delimiter=',')


root.update()
root.destroy()