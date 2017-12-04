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
    elif bandname == 'Red Edge':
        band = cameraSR[15]    
    #For given time, trace back to nearest SVC measurement for given target
    wavelength,reference,target,target_response = svcReader.svcGrabber(SVCtargetSR)
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

#def findLuts(dictionary, image)#, DNfinder = 'auto'):
#def findLUTS(missionDatafilename,SVCdirectory,cameraresponseSR,bandname):
def findLUTS(missionDatafilename,processsedimagedirectory,cameraresponseSR):
    missionData = np.loadtxt(missionDatafilename,unpack = True, skiprows = 1,dtype = str, delimiter = ',')
    frames = list(np.unique(missionData[1]))
    LUTdict = {}
    for name in frames:

        indices = np.where(missionData[1] == name)
        scenetargets = missionData[0][indices]
        framestd = {}
        svcdict = {}
        DNdict = {}
        if '4' in scenetargets:
            indextarget4 = np.where((missionData[1] == name) & (missionData[0] == '4'))
            std4 = missionData[10:15,indextarget4[0]]
            DN4 = missionData[5:10,indextarget4[0]]
            svcfilenumber = missionData[23,indextarget4]
            framestd['target4'] = std4
            svcdict['target4'] = svcfilenumber
            DNdict['target4'] = DN4
        if '5' in scenetargets:
            indextarget5 = np.where((missionData[1] == name) & (missionData[0] == '5'))
            std5 = missionData[10:15,indextarget5[0]]
            DN5 = missionData[5:10,indextarget5[0]]
            svcfilenumber = missionData[23,indextarget5]
            framestd['target5'] = std5
            svcdict['target5'] = svcfilenumber
            DNdict['target5'] = DN5
        if '1' in scenetargets:
            indextarget1 = np.where((missionData[1] == name) & (missionData[0] == '1'))
            std1 = missionData[10:15,indextarget1[0]]
            DN1 = missionData[5:10,indextarget1[0]]
            svcfilenumber = missionData[23,indextarget1]
            framestd['target1'] = std1
            svcdict['target1'] = svcfilenumber
            DNdict['target1'] = DN1
        if '2' in scenetargets:
            indextarget2 = np.where((missionData[1] == name) & (missionData[0] == '2'))
            std2 = missionData[10:15,indextarget2[0]]
            DN2 = missionData[5:10,indextarget2[0]]
            svcfilenumber = missionData[23,indextarget2]
            framestd['target2'] = std2
            svcdict['target2'] = svcfilenumber
            DNdict['target2'] = DN2
        #print(framestd)
        #print(framestd)

        reflectancedict = {}
        for key, value in svcdict.items():
            SVCfilename = 'T' + value[0][0].zfill(3) + '.sig'
            SVCfile = glob.glob(SVCdirectory + '*' + SVCfilename)
            reflectancevalues = [findReflectance(SVCfile[0],cameraresponseSR,'Blue'),findReflectance(SVCfile[0],cameraresponseSR,'Green'),findReflectance(SVCfile[0],cameraresponseSR,'Red'),findReflectance(SVCfile[0],cameraresponseSR,'Red Edge'),findReflectance(SVCfile[0],cameraresponseSR,'NIR')]
            #print(reflectancevalues)
            reflectancedict[key] = reflectancevalues

        if len(framestd) >= 2:
            for key, value in framestd.items():
                if '0.0' in value:
                    #print('deleting saturated targets')
                    del reflectancedict[key]
                    del DNdict[key]
            #print(DNdict)
                    #print(DNdict)
            if len(DNdict) >= 2:
                for key,value in DNdict.items():
                    if 'target5' in DNdict:
                        gotoTarget = 'target5'
                    elif 'target1' in DNdict:
                        gotoTarget = 'target1'
                    elif 'target2' in DNdict:
                        gotoTarget = 'target2'
                #print(gotoTarget)

                whiteReflect = np.asarray(reflectancedict[gotoTarget])
                blackReflect = np.asarray(reflectancedict['target4'])
                whiteDN = DNdict[gotoTarget].astype(np.float)
                blackDN = DNdict['target4'].astype(np.float)
                #print(type(whiteReflect[0]))
                #print(whiteReflect)
                #print(type(blackReflect[0]))
                #print(blackReflect)
                #print(type(whiteDN))
                #print(whiteDN)
                #print(type(blackDN))
                #print(blackDN)
                for band in np.arange(5):
                    slope = (whiteReflect[band] - blackReflect[band])/(whiteDN[band] - blackDN[band])
                    #print('slope',slope)       
                    intercept = whiteReflect[band] - slope * whiteDN[band]
                    #print('intercept',intercept)
                    imagemetadatafile = processsedimagedirectory + name[:8] + '_' + str(band+1) + '.tif'
                    #print(imagemetadatafile)
                    metadatadict = metadataReader.metadataGrabber(imagemetadatafile)
                    irradiance = metadatadict['Xmp.Camera.Irradiance']
                    #print('I',irradiance)
                    LUTdict[(band,irradiance)] = (slope,intercept)
                    #print('LUTdict',LUTdict)
    #print('LUTdict',LUTdict)
    return LUTdict

                #LUT = slope * fulldepth + intercept
                #print(np.shape(LUT))
            #SVCtargetSR = SVCdirectory + 

            #reflectance = findReflectance(SVCtargetSR,cameraresponseSR,bandname)

            #svcdict[key] = reflectance        

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
if __name__ == '__main__':

    import cv2
    import os
    import time
    import numpy as np
    import scipy
    import scipy.misc
    from osgeo import gdal

    import sys
    sys.path.append("..")

    SVCdirectory = '/cis/otherstu/gvs6104/DIRS/20171109/SVC/'
    processsedimagedirectory = '/cis/otherstu/gvs6104/DIRS/20171109/Missions/1345_375ft/micasense/processed/'
    missionDatafilename = '/cis/otherstu/gvs6104/DIRS/20171109/Missions/1345_375ft/micasense/Flight_20171109T1345_375ft_kxk8298.csv'
    cameraresponseSR = '/cis/otherstu/gvs6104/DIRS/MonochrometerTiffs/Spectral_Response.csv'
    LUTdict = findLUTS(missionDatafilename,processsedimagedirectory,cameraresponseSR)

    
    #print(missionDataarray)
    #print(missionDataarray[10:15,80])
    #print(missionDataarray[:,0])
