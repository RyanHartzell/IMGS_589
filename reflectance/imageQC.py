import cv2
import glob
import numpy as np
import os
import rasterio
import glob

'''
Name::
    imageQC

Description::
    A variety of methods focused on providing quick analysis of reflectance
    imagery. Currently focused on identifying reflectance values over 1 and
    under 0.

Version History::
    Wrote Script, Documentation                                        3/14/2018

To Do::
    1) Create 'ScanImageBand' where each individual band is parsed, generating
    the same blue/gray/red map with a gray-scale image.
    2) Update any 'ScanImage' varients to generate an image with a gradient red
    and blue color mapping
        -How many 'blue' and 'red' levels to include
            -Linear or Logarithmic gradient?

Current Bugs::

Author::
    Kevin Kha
'''

def ScanImage(imagepath,savedirectory,displayImage = False):
    #Part 1: This is a raster image, need to convert to a numpy array
    image = rasterio.open(imagepath)
    band1 = image.read(1)
    band2 = image.read(2)
    band3 = image.read(3)
    band4 = image.read(4)
    band5 = image.read(5)
    #Build an BGR image for later reference, and a 5 band image for manipulation
    visualimage = np.dstack((band1,band2,band3))
    actualimage = np.dstack((band1,band2,band3,band4,band5))

    #Part 2: Check if image has values greater than 1 or less than 0, and act accordingly
    if (np.max(actualimage) >= 1) or (np.min(actualimage) <= 0):
        print('Something funky')
        #Make a map with a gray display
        mapHiLow = np.full(np.shape(visualimage),128)
        highVals = np.where(actualimage>=1)
        lowVals = np.where(actualimage<=0)
        #Make map blue where reflectance is zero or negative
        mapHiLow[lowVals[0],lowVals[1],:] = 0
        mapHiLow[lowVals[0],lowVals[1],0] = 255
        #Make map red where reflectance is one or greater
        mapHiLow[highVals[0],highVals[1],:] = 0
        mapHiLow[highVals[0],highVals[1],2] = 255
        mapHiLow = mapHiLow.astype('uint8')
        #Part 3: Prepare side by side visualization
        visualimage = np.clip(visualimage * 255,0,255).astype('uint8')
        side2side = np.hstack((visualimage,mapHiLow))
        if displayImage == True:
            side2side = cv2.resize(side2side, (0,0), fx = 0.5, fy = 0.5)
            cv2.imshow('Trouble Cases',side2side)
            cv2.waitKey()
        if not os.path.exists(savedirectory):
            os.makedirs(savedirectory)
        finalimagename = savedirectory + imagepath.split('/')[-1]
        cv2.imwrite(finalimagename,side2side)
    else:
        #No 'bad' reflectances
        print('We good')

def QCvideo(imagedirectory):
    images = glob.glob(imagedirectory + '*.tiff')
    images.sort()
    sampleimage = cv2.imread(images[0])
    height,width,channels = sampleimage.shape
    videopath = imagedirectory + 'qualitycheck.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(videopath,fourcc,5.0,(width,height))
    for image in images:
        print(image.split('/')[-1])
        image = cv2.imread(image)
        video.write(image)
    cv2.destroyAllWindows()
    video.release()

if __name__ == '__main__':

    #Grab all of the images in a given directory
    images = glob.glob('/research/imgs589/imageLibrary/DIRS/20171108/Missions/1300_225ft/micasense/reflectanceproduct/*.tiff')
    images.sort()
    #The directory to save to
    saveout = '/research/imgs589/imageLibrary/DIRS/20171108/Missions/1300_225ft/micasense/reflectanceproduct/parsed/'
    print(saveout)
    for image in images:
        print(image.split('/')[-1])
        ScanImage(image,saveout)

    QCvideo(saveout)
