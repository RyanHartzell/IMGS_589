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
	os, os.path, pandas, tkinter, cv2, matplotlib, numpy

build:
	Tested and run in python3

author::
    Geoffrey Sasaki

copyright::
 Copyright (C) 2017, Rochester Institute of Technology
"""

import os
import tkinter
import cv2
import matplotlib
matplotlib.use("TkAgg")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import filedialog, ttk
from os.path import splitext, basename


def openAndReadSPD():
	"""
	This function prompts the user to select the spectral power
	distribution excel document or comma seperated values. It then
	creates and returns a numpy array of the data while rounding the 
	wavelengths to the nearest integer, typically in 10nm increments.
	"""
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
	#spdDictionary = dict(zip(spdArray[0],spdArray[1]))

	return spdArray

def openAndReadTiff(root):
	"""
	This function prompts the user to select the directory with the tiff
	images and creates a list with all of the tiff image locations and 
	creates a list with all of the images that have been read in.
	"""
	tiffDir = filedialog.askdirectory(initialdir=os.getcwd())

	tiffList = []
	for file in os.listdir(tiffDir):
		if file.endswith(('.tiff','.tif','.TIF','.TIFF')):
	 		tiffList.append(tiffDir +'/'+ file)
	tiffList.sort()

	root.deiconify()
	imageList = []
	status_text = tkinter.StringVar()
	label = tkinter.Label(root, textvariable=status_text)
	label.pack()
	progress_variable = tkinter.DoubleVar()
	progressbar = ttk.Progressbar(root, variable=progress_variable, maximum=len(tiffList))
	progressbar.pack()

	for imageFile in tiffList:
		im = cv2.imread(imageFile, cv2.IMREAD_UNCHANGED)
		imageList.append(im)
		progress_variable.set(tiffList.index(imageFile))
		status_text.set("Reading in image {0}".format(os.path.basename(imageFile)))
		root.update_idletasks()
	
	root.update()
	root.withdraw()
	return tiffList, imageList

def findBrightestPoint(imageList, tiffList, radius=200, verbose=False):
	"""
	This function takes in the list of images and then computes the
	minimum and maximum digital count and their respective locations 
	of the gray version of the images. It then finds the brightest
	digital count out of all of the images its location. 
	"""

	brightValues = []
	brightLocations = []
	for image in imageList:
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
		brightValues.append(maxVal)
		brightLocations.append(maxLoc)
		#print("The brightest value found was: {0} at {1}".format(maxVal, maxLoc))

	brightestImageIndex = np.argmax(brightValues)
	maxLocation = brightLocations[brightestImageIndex]

	if verbose:
		brightestImage = tiffList[brightestImageIndex]
		bIm = cv2.imread(brightestImage, cv2.IMREAD_UNCHANGED)
		maxCount = int(np.power(2,int(str(bIm.dtype)[4:])))
		cv2.circle(bIm, maxLocation, radius, (maxCount,maxCount,maxCount), 5)
		cv2.namedWindow("brightestImage", cv2.WINDOW_AUTOSIZE)
		cv2.imshow("brightestImage", cv2.resize(bIm, None, 
							fx=.2,fy=.2, interpolation=cv2.INTER_AREA))

	return maxLocation

def calculateMeanDC(imageList, maxLocation, spdArray, radius=200):
	"""
	This function takes in all of the images, the maximum location,
	the spectral power distribution, and a user specified radius.
	It then creates a circular mask with the given radius over each 
	of the images to compute the mean of the circle in the image.
	After it computes the mean digital count of the circle, it normalizes
	it by the spectral power distribution at that wavelength.
	"""

	meanDCList = []
	for image in imageList:
		mask = np.zeros(image.shape, np.uint8)
		cv2.circle(mask, maxLocation, radius, (255,255,255), -1)
		mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
		meanDC = cv2.mean(image, mask=mask)[:3]
		meanDCList.append(meanDC)
		#print("Mean DCs: Blue {0}, Green {1}, Red {2}".format(
		#		meanDC[0], meanDC[1], meanDC[2]))

	return np.asarray(meanDCList, dtype='float64')

def normalizeMeanDC(meanDC, spdArray):
	"""
	Implements the normalization by spectral power distribution and
	the peak normalized relative spectral response.
	"""
	normSP = np.zeros_like(meanDC, dtype='float64')
	normSP[:] = meanDC[:]/spdArray[1].astype('float64')
	
	peakNormalized = np.zeros_like(normSP, dtype='float64')
	for band in np.arange(0,peakNormalized.shape[0]):
		peakNormalized[band] = normSP[band]/np.amax(normSP[band])
	
	return peakNormalized, normSP

def plotSpectralResponse(spdArray, meanDC, normDC, peakNorm):
	"""
	Show's each of the graphs using matplotlib
	"""
	plt.ion()

	figure1 = plt.figure('Spectral Power Distribution')
	x = spdArray[0]
	SPD = figure1.add_subplot(1,1,1)
	SPD.set_title("Spectral Power Distribution Function")
	SPD.set_xlabel("Wavelength [nm]")
	SPD.set_ylabel("Power [Watts]")
	SPD.set_ylim([0,max(spdArray[1])+.25*max(spdArray[1])])
	SPD.set_xlim([min(spdArray[0]),max(spdArray[0])]) 
	SPD.plot(x, spdArray[1], color = 'black') 
	
	figure2 = plt.figure('RAW Sensor Spectral Response')
	RAW = figure2.add_subplot(1,1,1)
	RAW.set_title("RAW sensor spectral response")
	RAW.set_xlabel("Wavelength [nm]")
	RAW.set_ylabel("Spectral Response [Digital Count]")
	RAW.set_ylim([0,max(meanDC.flat)+.25*max(meanDC.flat)])
	RAW.set_xlim([min(spdArray[0]),max(spdArray[0])]) 
	RAW.plot(x, meanDC[0], color = 'blue') 
	RAW.plot(x, meanDC[1], color = 'green') 
	RAW.plot(x, meanDC[2], color = 'red') 

	figure3 = plt.figure('Relative Sensor Spectral Response')
	RSR = figure3.add_subplot(1,1,1)
	RSR.set_title("Relative Sensor spectral response")
	RSR.set_xlabel("Wavelength [nm]")
	RSR.set_ylabel("Relative Spectral Response [Digital Count/Watt]")
	RSR.set_ylim([0,max(normDC.flat)])
	RSR.set_xlim([min(spdArray[0]),max(spdArray[0])])
	RSR.plot(x, normDC[0], color = 'blue')
	RSR.plot(x, normDC[1], color = 'green') 
	RSR.plot(x, normDC[2], color = 'red') 
	
	figure4 = plt.figure('Peak Normalized Relative Sensor Spectral Response')
	PRSR = figure4.add_subplot(1,1,1)
	PRSR.set_title("Peak Normalized Relative Sensor Spectral Response")
	PRSR.set_xlabel("Wavelength [nm]")
	PRSR.set_ylabel("Peak Normalized Relative Spectral Response [unitless]")
	PRSR.set_ylim([0,max(peakNorm.flat)])
	PRSR.set_xlim([min(spdArray[0]),max(spdArray[0])])
	PRSR.plot(x, peakNorm[0], color = 'blue') 
	PRSR.plot(x, peakNorm[1], color = 'green') 
	PRSR.plot(x, peakNorm[2], color = 'red') 
	
	plt.draw()
	plt.pause(.001)

	plt.show()

def saveData(spdArray, meanDC, normDC, peakNorm, tiffList):
	"""
	This function writes out the resultant data. They can be found
	seprately or in its entirety in a single comma seperated value.
	"""
	directory = os.path.dirname(tiffList[0])
	SpectralResponse = np.concatenate((spdArray, meanDC, 
					normDC, peakNorm), axis=0).transpose()

	meanDC = np.insert(meanDC, 0, spdArray[0], axis=0)
	normDC = np.insert(normDC, 0, spdArray[0], axis=0)
	peakNorm = np.insert(peakNorm, 0, spdArray[0], axis=0)

	np.savetxt(directory+"/SpectralPowerDistribution.csv", 
								spdArray.transpose(), delimiter=",")
	np.savetxt(directory+"/RAWSpectralResponse.csv", 
								meanDC.transpose(), delimiter=",")
	np.savetxt(directory+"/RelativeSpectralResponse.csv", 
								normDC.transpose(), delimiter=",")
	np.savetxt(directory+"/PeakNormalizedRSR.csv", 
								peakNorm.transpose(), delimiter=",")

	np.savetxt(directory+"/SpectralResponse.csv", SpectralResponse, 
				delimiter=",", header="Wavelength, Power, Raw Blue," + \
				"Raw Green, Raw Red, Norm Blue, Norm Green, Norm Red,"+ \
				"Peak Blue, Peak Green, Peak Red", comments='')

def flush():
    print( 'Press "c" to continue, ESC to exit, "q" to quit')
    delay = 100
    while True:
        k = cv2.waitKey(delay)

        # ESC pressed
        if k == 27 or k == (65536 + 27):
            action = 'exit'
            print( 'Exiting ...')
            plt.close()
            break

        # q or Q pressed
        if k == 113 or k == (65536 + 113) or k == 81 or k == (65536 + 81):
            action = 'quit'
            print( 'Quitting ...')
            plt.close()
            break

        # c or C pressed
        if k == 99 or k == (65536 + 99) or k == 67 or k == (65536 + 67):
            action = 'continue'
            print( 'Continuing ...')
            plt.close()
            break

    return action

if __name__ == '__main__':

	root = tkinter.Tk()
	root.withdraw()
	root.geometry('{0}x{1}'.format(400,100))
	verbose = True
	radius = 200

	root.update()
	spdArray = openAndReadSPD()
	
	root.update()
	tiffList, imageList = openAndReadTiff(root)

	if len(tiffList) != len(spdArray[0]):
		msg = "The number of images and the number of spectral power" + \
				"distributions measured were not the same."
		raise ValueError(msg)	

	maxLocation = findBrightestPoint(imageList, tiffList, radius, verbose)
	
	meanDC = calculateMeanDC(imageList, maxLocation, spdArray, radius)
	meanDC = meanDC.transpose()

	peakNormalized, normSP = normalizeMeanDC(meanDC, spdArray)

	plotSpectralResponse(spdArray, meanDC, normSP, peakNormalized)
	
	saveData(spdArray, meanDC, normSP, peakNormalized, tiffList)

	action = flush()
	
	root.destroy()


