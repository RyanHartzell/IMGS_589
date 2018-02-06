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
import cv2
import json
from fileStructure.fixMicaSenseStructure import fixNamingStructure
from geoTIFF.createGeoTIFF import writeGeoTIFF, showGeoTIFF, writeGPSLog
from geoTIFF.normalizeDC import normalizeISOShutter
from geoTIFF.metadataReader import metadataGrabber
from registration.correlateImages import OrderImagePairs
from registration.createImageStack import stackImages
from registration.preRegister import preRegister

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
parser.add_argument('-s', '--startIndex',type=int, help="The index at which to start writing")
parser.add_argument('-j', '--registrationDict',type=str, help="The location of the json file holding the registration")
args = parser.parse_args()
flightDirectory = args.input
geoTiffDir = args.output
startIndex = args.startIndex
registrationDict = args.registrationDict

if startIndex is None:
	startIndex = 0

if flightDirectory is None:
	#IF MULTIPLE DIRECTORIES ARE SELECTED THEN PARALLEL PROCESS THEM
	#flightDirectory = "/cis/otherstu/gvs6104/DIRS/20170928/150flight"
	initialdir = os.getcwd()
	initialdir = "/research/imgs589/imageLibrary/DIRS/"
	flightDirectory = filedialog.askdirectory(initialdir=initialdir,
				title="Choose the RAW MicaSense .tif directory")
	if flightDirectory == '' or type(flightDirectory) == tuple:
		sys.exit()
else:
	if flightDirectory[-1] == '/':
		flightDirectory = flightDirectory[:-1]

if geoTiffDir is None:
	splitted = flightDirectory.split('/')
	geoTiffDir = '/'.join(splitted[:-1]) + os.path.sep
	if os.path.isdir(geoTiffDir + "geoTiff/"):
		geoTiffDir = geoTiffDir + "geoTiff/"
	else:
		geoTiffDir = filedialog.askdirectory(initialdir=os.path.split(flightDirectory)[0],
				title="Choose the directory to place the GeoTiffs")
		if geoTiffDir == '' or type(geoTiffDir) == tuple:
			sys.exit(0)

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

#tiffList = tiffList[startIndex*5:]

if registrationDict is None:
	splitted = flightDirectory.split('/')
	preRegisterLog = '/'.join(splitted[:-1]) + os.path.sep + "micasensePreRegister.json"
	#try:
	if not os.path.isfile(preRegisterLog):

		#sampleDirectory = "/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/processed/"
		#for t in range(0,len(tiffList),5):
		t = startIndex*5
		wait = 0
		while t < len(tiffList)-5:
			blue, green, red, nIR, re = tiffList[t], tiffList[t+1], tiffList[t+2], tiffList[t+3], tiffList[t+4]
			blueIm = cv2.imread(blue, cv2.IMREAD_UNCHANGED)
			greenIm = cv2.imread(green, cv2.IMREAD_UNCHANGED)
			redIm = cv2.imread(red, cv2.IMREAD_UNCHANGED)
			stack = np.dstack((blueIm, greenIm, redIm))
			cv2.imshow("RGB: ' 'x2 accept | 'c' continue | 'p' pause",
				cv2.resize(stack, None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA))
			resp = cv2.waitKey(wait)
			if resp == ord(' '):
				wait = 0
				confirm = cv2.waitKey(0)
				if confirm == ord(' '):
					break
			elif resp == ord('p'):
				wait = 0
			elif resp == ord('c'):
				wait = 100
			elif resp == ord('a'):
				wait = 0
				t -= 10
			elif resp == ord('d'):
				wait = 0
				pass
			elif resp == 27:
				sys.exit(0)
			t += 5
		cv2.destroyWindow("RGB: ' 'x2 accept | 'c' continue | 'p' pause")
		cv2.destroyAllWindows()
		imageList = [blue, green, red, re, nIR]
		transformDictionary = preRegister(imageList, jsonify=True)

		with open(preRegisterLog, 'w') as f:
			json.dump(transformDictionary, f, indent=4)
		f.close()
		os.chmod(preRegisterLog, 0o775)


	with open(preRegisterLog, 'r') as f:
		transformDictionary = json.load(f)
	f.close()
	transformDictionary.update({k : np.matrix(v).astype(np.float32) for k,v in transformDictionary.items()})

stackQC = True
wait = 500

splitted = flightDirectory.split('/')
gpsLog = '/'.join(splitted[:-1]) + os.path.sep + "GPSLog.csv"
with open(gpsLog,'w') as resultFile:
	wr = csv.writer(resultFile)

	images = startIndex*5
	#for images in range(0,len(tiffList),5):
	while images < len(tiffList)-5:
		print("Current image number: {0}".format(images//5))
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
		imageStack, goodCorr = stackImages(imageList, matchOrder,transformDictionary,'ECC', crop=False, bandQC=False)

		if stackQC:
			green, red, ir = imageStack[:,:,1], imageStack[:,:,2], imageStack[:,:,4]
			cv2.imshow("RGB - ' ' to accept | 'n' to reject [1 sec]",
				cv2.resize(imageStack[:,:,:3], None, fx=.5, fy=.5, interpolation=cv2.INTER_AREA))
			cv2.imshow("False Re", cv2.resize(imageStack[:,:,1:4], None, fx=.3, fy=.3, interpolation=cv2.INTER_AREA))
			cv2.imshow("False IR", cv2.resize(np.dstack((green,red, ir)), None, fx=.3, fy=.3, interpolation=cv2.INTER_AREA))
			while True:
				if wait == 0:
					qcWait = ord('n')
				else:
					qcWait = cv2.waitKey(wait)
				wasdList = [ord('w'), ord('W'), ord('a'), ord('A'), ord('s'), ord('S'),
							ord('d'), ord('D')]
				if qcWait == ord(' '):
					break
				elif qcWait == -1:
					break
				elif qcWait == ord('n') or qcWait in wasdList:
					wait = 0
					images -= 5
					print(chr(qcWait))
					print("Press a to go back, d to go forward, n to reject")
					step = cv2.waitKey(0)
					if step == ord('a'):
						images -= 5
						break
					elif step == ord('d'):
						images += 5
						break
					elif step == ord('n'):
						imageStack, goodCorr = stackImages(imageList, matchOrder,
							transformDictionary,'ECC', crop=False, bandQC=True)
						#cv2.destroyAllWindows()
						wait = 500
						break
					elif step == 27:
						sys.exit()
					elif step > 0:
						wait = 500
						break
				if qcWait == 27:
					sys.exit(1)

		if goodCorr:
			normStack = normalizeISOShutter(imageStack, imageList)
			geoTiff = writeGeoTIFF(normStack, imageList, geoTiffDir)
			os.chmod(geoTiff, 0o775)
			logLine = writeGPSLog(imageList[0],geoTiff)
			wr.writerow(logLine)
			#showGeoTIFF(geoTiff)

		images += 5
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
