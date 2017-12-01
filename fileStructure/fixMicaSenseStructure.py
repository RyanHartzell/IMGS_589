"""
title::
	Fix MicaSense Rededge Directory Structure

description::
	The Fix Naming Structure Method:
	Renames the images shot on the MicaSense Redege so they are
	alphanumerically in order by the time they were shot. The
	original directory structure looked like below:
		Flight/000/IMG_0000_1.tif
		Flight/001/IMG_0050_1.tif
		Flight/002/IMG_0012_4.tif
		Flight/003/IMG_0156_2.tif
	Where the image numbers IMG_"####"_2.tif did not go past 200
	so based on the directory Flight/"###"/IMG_0000 this method
	renames them by the following formula:
		NewImageNumber = SubDirectory*200 + OriginalImageNumber
	It then places them under the original flight folder with the
	following naming structure:
		Flight/IMG_0000_1.tif
		Flight/IMG_0000_2.tif
		...				...
		Flight/IMG_0992_1.tif
	This script will be good for any number of subdirectories and
	can accomidate more than 4 indices for the image number.

	The Group Bands Method:
	Takes all of the renamed images from the above method then
	places them into subdirectories per band. The new directories
	are formatted below:
		band1, band2, band3, ... ,band[n]
		band1/IMG_0000_1.tif, band1/IMG_0001_1.tif, ...
		band2/IMG_0000_2.tif, band2/IMG_0001_2.tif, ...
		band3/IMG_0000_3.tif, band3/IMG_0001_3.tif, ...

author::
	Geoffrey Sasaki

copyright::
	Copyright (C) 2017, Rochetser Institute of Technology
"""

#import os, glob

#from os.path import basename, dirname


def fixNamingStructure(directory):
	import os, glob
	import shutil
	from os.path import basename, dirname, split

	if len(glob.glob(directory+'/*/')) == 0:
		msg = "No subdirectories were found in the specified directory."
		raise ValueError (msg)
	elif len(glob.glob(directory+'/*/*.tif')) == 0:
		msg = "No '.tif' files were found in the specified subdirectory."
		raise ValueError (msg)

	processedDirectory = os.path.split(directory)[0] + "/processed/"

	for subDirectory in sorted(glob.iglob(directory + '/[0-9][0-9][0-9]/')):
		#Goes through every subdirectory in the format of '/000/ or /###/'
		subNumber = int(basename(dirname(subDirectory)))
		#Finds the subdirectory number: /000/ = 0 /001/ = 1
		for oldFilename in sorted(glob.iglob(subDirectory+'/*.tif')):
			#Goes through every '.tif' file in the subdirectory of /###/
			baseFileName = basename(oldFilename)
			#Creates a base filename without the path: IMG_0000_1.tif
			fileNumber = int(baseFileName[4:8])
			#Finds the filenumber '0000' in the case of IMG_0000_1.tif
			newFileNumber = str((subNumber*200) + fileNumber).zfill(4)
			#Creates the new filenumber: 2*200 + 30 = 0430
			newBaseFileName = baseFileName[:4] + newFileNumber + \
													baseFileName[8:]
			#Adds the new filenumber to the position of the old number
			newFileName = processedDirectory + os.path.sep + newBaseFileName
			#Creates the new file with the original directory extension

			#os.rename(oldFilename, newFileName)
			shutil.copyfile(oldFilename, newFileName)
			#Renames the images. BE CAREFUL
		#os.rmdir(subDirectory)
		#Removes the empty /000/ directory once all images are renamed

	return processedDirectory

def groupBands(directory):
	import glob
	import os

	if len(glob.glob(directory+'/*.tif')) == 0:
		msg = "No '.tif' files were found in the specified directory."
		raise ValueError(msg)
	else:
		tiffList = glob.glob(directory + '/*.tif')

	bands = int(max([tiffList[i][-5] for i in range(len(tiffList))]))
	#Finds the number of bands from the maximum extension of the images

	for b in range(1, bands+1):
		#Loops through all of the bands with a 1 index to the band #
		bandDirectory = directory + "/band{0}".format(b)
		#Creates a band directory for the current itteration band
		if not os.path.exists(bandDirectory):
			#If the bandDirectory does not exist it makes the directory
			os.makedirs(bandDirectory)
		for tiff in glob.iglob(directory + '/*{0}.tif'.format(b)):
			#Loops through all of the tiffs with the band extension
			movedFile = bandDirectory + os.path.sep + basename(tiff)
			#Creates the new filename in the new band directory
			os.rename(tiff, movedFile)
			#Renames the original image BE CAREFUL

if __name__ == "__main__":
	import tkinter
	import sys
	from tkinter import filedialog
	from fixMicaSenseStructure import fixNamingStructure, groupBands

	root = tkinter.Tk()
	root.withdraw()

	root.update()
	initialdir = os.getcwd()
	initialdir = "/cis/otherstu/gvs6104/DIRS/20171012/150ft"
	flightDirectory = filedialog.askdirectory(initialdir=initialdir)

	if flightDirectory == '':
		sys.exit()

	processedDirectory = fixNamingStructure(flightDirectory)
	groupBands(flightDirectory)
