"""
title::
 	Spectral Response Calculation

description::
	This program will detect an digital count value in a given image,
	then using the spectral power distribution, calculate the
	spectral response of that sensor for the given wavelengths.

attributes::
    TBD

dependencies::
	os, os.path, pandas, tkinter, cv2, matplotlib

build:
	Tested and run in python3

author::
    Geoffrey Sasaki

copyright::
 Copyright (C) 2017, Rochester Institute of Technology
"""

import cv2
import numpy as np

def Spectral():

	return None

if __name__ == '__main__':
	import os
	from os.path import splitext, basename
	import pandas as pd
	import tkinter
	from tkinter import filedialog
	import cv2
	import matplotlib
	matplotlib.use("TkAgg")
	import matplotlib.pyplot as plt

	root = tkinter.Tk()
	root.withdraw()

	spdFile = filedialog.askopenfilename(initialdir=os.getcwd(), 
						filetypes=[("Excel files", "*.xlsx *.xls"), 
								("Comma Seperated Values", "*.csv")], 
						title="Choose the Spectral Power Distribution")

	if spdFile[-4:] == "xlsx" or spdFile[-3:] == "xls":
		spdXLS = pd.read_excel(spdFile)
		spdArray = spdXLS.as_matrix().transpose()
	elif spdFile[-3:] == "csv":
		spdArray = np.genfromtxt(spdFile, delimiter=',').transpose()
		spdArray = np.nan_to_num(spdArray)
	else:
		msg = "Unsupported filetype given. Cannot create numpy array."
		raise TypeError(msg)
	if spdArray.shape[0] != 2 or spdArray.dtype != np.float64:
		msg = "The spectral power distribution was not read in correctly"
		raise ValueError(msg)

	spdArray[0] = np.around(spdArray[0]).astype(int)
	spdDictionary = dict(zip(spdArray[0],spdArray[1]))

	tiffDir = filedialog.askdirectory(initialdir=os.getcwd())
	root.destroy()

	tiffList = []
	for file in os.listdir(tiffDir):
		if file.endswith(('.tiff','.tif','.TIF','.TIFF')):
	 		tiffList.append(tiffDir +'/'+ file)
	tiffList.sort()

	if len(tiffList) != len(spdDictionary):
		msg = "The number of images and the number of spectral power" + \
				"distributions measured were not the same."
		raise ValueError(msg)

	brightValues = []
	for imageFile in tiffList:
		im = cv2.imread(imageFile, cv2.IMREAD_UNCHANGED)
		im = cv2.resize(im, None, fx=0.10, fy=0.10, 
						interpolation=cv2.INTER_NEAREST)
		gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
		minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
		brightValues.append(maxVal)
		print("The brightest value found was: {0}".format(maxVal))

	brightestImageIndex = np.argmax(brightValues)
	brightestImage = tiffList[brightestImageIndex]
	print("The brightest image was {0}, at wavelenth {1}, with a value of {2}.".format(
			basename(brightestImage), spdArray[0,brightestImageIndex], np.max(brightValues)))
	bIm = cv2.imread(brightestImage, cv2.IMREAD_UNCHANGED)
	maxCount = int(np.power(2,int(str(bIm.dtype)[4:])))
	gray = cv2.cvtColor(bIm, cv2.COLOR_BGR2GRAY)
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
	cv2.namedWindow("brightestImage", cv2.WINDOW_AUTOSIZE)
	cv2.imshow("brightestImage", cv2.resize(cv2.circle(bIm, maxLoc, 
							200, (maxCount,maxCount,maxCount), 5), None, 
							fx=.2,fy=.2, interpolation=cv2.INTER_AREA))

	meanDCList = []
	for imageFile in tiffList:
		im = cv2.imread(imageFile, cv2.IMREAD_UNCHANGED)
		mask = np.zeros(im.shape, np.uint8)
		cv2.circle(mask, maxLoc, 200, (maxCount,maxCount,maxCount), -1)
		#NEED TO FIX THE ABOVE HARDCODED VALUES
		mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
		meanDC = cv2.mean(im, mask=mask)
		meanDCList.append(meanDC)
		print("Mean DCs: Blue {0}, Green {1}, Red {2}".format(
				meanDC[0], meanDC[1], meanDC[2]))

	normDC = meanDCList
	for index in range(len(spdDictionary)):
		normDC[index] = meanDCList[index]/spdArray[1,index]
	normDC = np.asarray(normDC).transpose()

	plt.plot(spdArray[0], normDC[0], 'b-')
	plt.plot(spdArray[0], normDC[1], 'g-')
	plt.plot(spdArray[0], normDC[2], 'r-')
	plt.axis([spdArray[0,0],spdArray[0,-1],np.min(normDC), np.max(normDC)])
	plt.title("Spectral Power Distribution of a Sensor")
	plt.xlabel("Wavelengths [10nm]")
	plt.ylabel("Spectral Power Distribution")
	plt.show()

	cv2.waitKey(0)




