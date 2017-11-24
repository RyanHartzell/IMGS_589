import cv2
import glob
import numpy as np
import os.path
import os
import sys

'''
Name:
   LUT related stuff (Might break this up later)

Description::
   Code responsible for interfacing ground truth measurements with field collect imagery to produce
   a reflectance image based upon irradiance for a given frame.

Inputs::

Version History::
   Filling in the blanks                                                                    11/24/2017
   Converted field notes to excel for csv possibility
   Started                                                                                  11/23/2017
   Sudo Code

Current Bugs/Questions::
   -Integration with other workflows (ex. Image normalization and registration)
   -Best Practice for multiplying SVC response and camera response curves?
      1) Keep SVC data as original as possible, interpolate camera data (Seems proper)
      2) Maintain camera data, downsample SVC data
      3) Modify both data sets
   -Need to streamline manual input method
   -Find relationship between field note times, SVC times, and micasense times
   -More to be discovered!

Author::
   Kevin Kha
'''

def findReflectance(SVCtargetSR,cameraresponseSR,image):
    #Find camera spectral response
    cameraSR = np.loadtxt(cameraresponseSR,unpack = True, skiprows = 1,dtype = float, delimiter = ',')
    #Band Selection
    metadatadict = metadatagrabber(image)
    band = metadatadict['Xmp.Camera.BandName']
    if band == 'Blue':
        band = cameraSR[12]
    elif band == 'Green':
        band = cameraSR[13]
    elif band == 'Red':
        band = cameraSR[14]
    elif band == 'NIR':
        band = cameraSR[16]
    elif band == 'Red edge':
        band = cameraSR[15]
    #Find which target
    
    #Find time in scene
    
    #For given time, trace back to nearest SVC measurement for given target
    
    #Integral of product of SVC and Camera
    numerator = np.sum(band * SVC)
    #Integral of SVC curves
    denominator = np.sum(band)
    #Reflectance = quotient of two integrals
    reflectance = numerator/denominator
    return reflectance
def findLuts(dictionary, image, DNfinder == 'auto'):
    #find irradiance
    metadatadict = metadatagrabber(image)
    irradiance = metadatadict['Xmp.Camera.Irradiance']
    #find reflectance of target one
    
    #find DN of target one
    if DNfinder == 'auto':
        #Target Selection Stuff
    elif DNfiner == 'manual':
        #User Input DN
    #find reflectance of target two
    
    #find DN of target two
    
    #Form LUT
    maxDN = 2**16
    fulldepth = np.arange(maxDN)
    slope = (whiteReflect - blackReflect)/(whiteDN - blackDN)
    intercept = whiteReflect - slope * whiteDN
    LUT = slope * fulldepth + intercept
    #Save out to dictionary irradiance and LUT pair
    dictionary[irradiance] = LUT
    #Return dictionary
    return dictionary
def applyLuts(dictionary, image):
    #Generate array of dictionary key irradiances
    irradianceKeys = np.asarray(list(dictionary.keys()))
    #find irradiance
    metadatadict = metadatagrabber(image)
    irradiance = metadatadict['Xmp.Camera.Irradiance']
    #find closest irradiance in array 
    closestIrradiance = np.abs(irradiancekeys - irradiance).argmin()
    bestIrradiance = irradiancekeys[logical]
    #apply given irradiance/LUT pair to image
    LUT = dictionary[bestIrradiance]
    reflectanceimage = cv2.LUT(image, LUT)
    #saveout image
    
    #return image
    
cwd = os.getcwd()

referencelibrary = {}
referenceimageset = ['/000/IMG_0015_1.tif', '/000/IMG_0030_1.tif','/000/IMG_0060_1.tif','/000/IMG_0094_1.tif','/000/IMG_0150_1.tif','/000/IMG_0199_1.tif']

for ref in referenceimageset:
    im = cv2.imread(cwd + ref, cv2.IMREAD_UNCHANGED)
    referencelibrary = findLuts(referencelibrary,ref)

for image in fullset:
    im = cv2.imread(cwd + image, cv2.IMREAD_UNCHANGED)
    reflectanceImage = applyLuts(referencelibrary, image) 
    