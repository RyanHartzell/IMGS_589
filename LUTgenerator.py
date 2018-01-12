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
def findLUTS(missionDatafilename,processedimagedirectory,cameraresponseSR):
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
            svcfilenumber = missionData[31,indextarget4]
            #print(svcfilenumber)
            framestd['target4'] = std4
            svcdict['target4'] = svcfilenumber
            DNdict['target4'] = DN4
        if '5' in scenetargets:
            indextarget5 = np.where((missionData[1] == name) & (missionData[0] == '5'))
            std5 = missionData[10:15,indextarget5[0]]
            DN5 = missionData[5:10,indextarget5[0]]
            svcfilenumber = missionData[31,indextarget5]
            framestd['target5'] = std5
            svcdict['target5'] = svcfilenumber
            DNdict['target5'] = DN5
        if '1' in scenetargets:
            indextarget1 = np.where((missionData[1] == name) & (missionData[0] == '1'))
            std1 = missionData[10:15,indextarget1[0]]
            DN1 = missionData[5:10,indextarget1[0]]
            svcfilenumber = missionData[31,indextarget1]
            framestd['target1'] = std1
            svcdict['target1'] = svcfilenumber
            DNdict['target1'] = DN1
        if '2' in scenetargets:
            indextarget2 = np.where((missionData[1] == name) & (missionData[0] == '2'))
            std2 = missionData[10:15,indextarget2[0]]
            DN2 = missionData[5:10,indextarget2[0]]
            svcfilenumber = missionData[31,indextarget2]
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
            if len(DNdict) >= 2 and 'target4' in DNdict.keys():
                for key,value in DNdict.items():
                    if 'target5' in DNdict:
                        gotoTarget = 'target5'
                    elif 'target1' in DNdict:
                        gotoTarget = 'target1'
                    elif 'target2' in DNdict:
                        gotoTarget = 'target2'
                #print(gotoTarget)
                #print(reflectancedict)
                #print(DNdict)
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
                    imagemetadatafile = processedimagedirectory + name[:8] + '_' + str(band+1) + '.tif'
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

def applyLuts(LUTdict, processedimagedirectory, geoTiff):
    print(geoTiff[-13:-5])
    imageStack = gdal.Open(geoTiff).ReadAsArray()
    imageStack = np.moveaxis(imageStack, 0 ,-1)
    reflectanceImage = np.zeros(np.shape(imageStack))
    for band in np.arange(1,6):
        rawimage = processedimagedirectory + geoTiff[-13:-5] + '_{}'.format(band) + '.tif'
        #print(rawimage)
        metadatadict = metadataReader.metadataGrabber(rawimage)
        irradiance = metadatadict['Xmp.Camera.Irradiance']
        #print(irradiance)
        refIrradiance = []
        for key, value in LUTdict.items() :
            if key[0] == band-1:
                refIrradiance.append(key[1])
        refIrradiance = np.asarray(refIrradiance)
        comparison = np.abs(refIrradiance-irradiance)
        #print(comparison)
        #print(np.argmin(comparison))
        closestIrradiance = refIrradiance[np.argmin(comparison)]
        #print(closestIrradiance)
        dictionaryreadkey = (band-1,closestIrradiance)
        slope = LUTdict[dictionaryreadkey][0][0]
        intercept = LUTdict[dictionaryreadkey][1][0]
        reflectanceImage[:,:,band-1] = imageStack[:,:,band-1] * slope + intercept
        #print(np.argmin(comparison))
        print(np.max(reflectanceImage[:,:,band-1]))
    return reflectanceImage    
    '''
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
    '''
if __name__ == '__main__':

    import cv2
    import glob
    import os
    import time
    import numpy as np
    import scipy
    import scipy.misc
    from osgeo import gdal

    import sys
    starttime = time.time()
    sys.path.append("..")

    #SVCdirectory = '/cis/otherstu/gvs6104/DIRS/20171109/SVC/'
    #processedimagedirectory = '/cis/otherstu/gvs6104/DIRS/20171109/Missions/1345_375ft/micasense/processed/'
    #missionDatafilename = '/cis/otherstu/gvs6104/DIRS/20171109/Missions/1345_375ft/micasense/Flight_20171109T1345_375ft_kxk8298.csv'
    #cameraresponseSR = '/cis/otherstu/gvs6104/DIRS/MonochrometerTiffs/Spectral_Response.csv'
    #reflectanceDir = '/cis/otherstu/gvs6104/DIRS/20171109/Missions/1345_375ft/micasense/reflectanceproduct/'
    #imagelist = glob.glob('/cis/otherstu/gvs6104/DIRS/20171109/Missions/1345_375ft/micasense/geoTiff/*') 

    #Time Specific
    processedimagedirectory = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1230_150ft/micasense/processed/'
    missionDatafilename = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1230_150ft/micasense/Flight_20171109T1230_150ft_kxk8298.csv'
    reflectanceDir = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1230_150ft/micasense/reflectanceproduct/'
    imagelist = glob.glob('/research/imgs589/imageLibrary/DIRS/20171109/Missions/1230_150ft/micasense/geoTiff/*') 

    #Date Specific
    SVCdirectory = '/research/imgs589/imageLibrary/DIRS/20171109/SVC/'    
    
    #Device Specific
    cameraresponseSR = '/research/imgs589/imageLibrary/DIRS/MonochrometerTiffs/Spectral_Response.csv'

    if not os.path.exists(reflectanceDir):
        os.makedirs(reflectanceDir)
    LUTdict = findLUTS(missionDatafilename,processedimagedirectory,cameraresponseSR)
    print(LUTdict)
    print(time.time() - starttime)
    #sampleimage = '/cis/otherstu/gvs6104/DIRS/20171109/Missions/1345_375ft/micasense/geoTiff/IMG_0160.tiff'
    for image in imagelist:
        reflectanceImage = applyLuts(LUTdict, processedimagedirectory, image)
        
        imagename = 'ref' + image[-13:]
        print(imagename)
        height, width, channels = reflectanceImage.shape
        driver = gdal.GetDriverByName( 'GTiff' )
        if reflectanceImage.dtype == 'uint8':
            GDT = gdal.GDT_Byte
        elif reflectanceImage.dtype == 'uint16':
            GDT = gdal.GDT_UInt16
        elif reflectanceImage.dtype == 'float32':
            GDT = gdal.GDT_Float32
        elif reflectanceImage.dtype == 'float64':
            GDT = gdal.GDT_Float64
        ds = driver.Create (reflectanceDir + imagename, width, height, channels, GDT)
        pWidth, pHeight = 1.0, 1.0
        X, Y = 0.0, 0.0
        geoTransform = ([X,pWidth,0,Y,0,pHeight])
        ds.SetGeoTransform(geoTransform)
        wktProjection = ''
        #srs = osr.SpatialReference(wkt = "")
        ds.SetProjection(wktProjection)
        for band in range(1, reflectanceImage.shape[2]+1):
            ds.GetRasterBand(band).WriteArray(reflectanceImage[:,:,band-1])
        ds.FlushCache()
        ds = None
    print(time.time() - starttime)

        
        #print(missionDataarray)
        #print(missionDataarray[10:15,80])
        #print(missionDataarray[:,0])
