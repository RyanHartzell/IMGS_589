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
   findReflectance function completed                                                       11/26/2017
   Filling in the blanks                                                                    11/24/2017
   Converted field notes to excel for csv possibility
   Started                                                                                  11/23/2017
   Sudo Code

Current Bugs/Questions::
   -Need to create manual input method
   -Find relationship between field note times, SVC times, and micasense times
   -More to be discovered!

Author::
   Kevin Kha
'''

import cv2
import glob
import numpy as np
import os.path
import os
import sys
from targets import svcReader
from geoTIFF import metadataReader

def findReflectance(SVCtargetSR,cameraresponseSR,bandname):
    #Find camera spectral response
    cameraSR = np.loadtxt(cameraresponseSR,unpack = True, skiprows = 1,dtype = float, delimiter = ',')
    #Band Selection
    wavelengthMono = cameraSR[0]
    if bandname == 'Blue':
        band = cameraSR[12]
    elif bandname == 'Green':
        band = cameraSR[13]
    elif bandname == 'Red':
        band = cameraSR[14]
    elif bandname == 'NIR':
        band = cameraSR[16]
    elif bandname == 'Red edge':
        band = cameraSR[15]    
    #For given time, trace back to nearest SVC measurement for given target
    wavelength,reference,target,target_response = svcGrabber(SVCtargetSR)
    target_response = target_response/100
    #Gaussian Curve fit for interpolation of data for a given band
    mean = np.sum(band * wavelengthMono)/np.sum(band)
    std = np.sqrt(np.abs(np.sum((wavelengthMono-mean)**2*band)/np.sum(band)))
    #Assignment of cameraSR to domain of SVC measurements
    gaussianResponse = np.exp(-(mean-wavelength)**2/std)    
    #Integral of product of SVC and Camera
    numerator = np.sum(gaussianResponse * target_response)
    #Integral of SVC curves
    denominator = np.sum(gaussianResponse)
    #Reflectance = quotient of two integrals
    reflectance = numerator/denominator
    return reflectance

def findLuts(dictionary, image, DNfinder = 'auto'):
    #find irradiance
    metadatadict = metadatagrabber(image)
    irradiance = metadatadict['Xmp.Camera.Irradiance']
    #find reflectance of target one
    
    #find DN of target one
    if DNfinder == 'auto':
        print('Target Selection Stuff')
    elif DNfiner == 'manual':
        print('Manual Input Method')
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
    
    