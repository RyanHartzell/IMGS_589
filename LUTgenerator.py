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
   Added comments to findLUTS method, removed commented out lines                           03/17/2018
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
import csv
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

def findLUTS(missionDatafilename,processedimagedirectory,cameraresponseSR,logging = True):
    #Generate numerous LUT to generate reflectance imagery based on downwelling irradiance
    if logging == True:
        csvfile = '/'.join(missionDatafilename.split('/')[:-1])+'/ELM_LUT_logger.csv'
        with open(csvfile,'w', newline = '\n') as currentTextFile:
            writer = csv.writer(currentTextFile, delimiter = ',')
            writer.writerow(['Frame','Altitude','Band','Irradiance','White #','White Rho','White Avg','White Std','Black #','Black Rho','Black Avg','Black Std', 'ELM Slope','ELM Intercept'])
    #From the target acquisition, grab every frame that had targets internal
    missionData = np.loadtxt(missionDatafilename,unpack = True, skiprows = 1,dtype = str, delimiter = ',')
    frames = list(np.unique(missionData[1]))
    #We need to figure out when we are at altitude, lets say we have to be within 95% of peak to be good
    Altitudes = np.loadtxt(missionDatafilename,unpack = True, skiprows = 1,usecols=4,dtype = float, delimiter = ',')
    peakAltitude = np.max(Altitudes)
    requiredAlt = peakAltitude * 0.95

    #For each frame we have to filter according to additional criteria
    LUTdict = {}
    for name in frames:
        indices = np.where(missionData[1] == name)
        scenetargets = missionData[0][indices]
        framestd = {}
        svcdict = {}
        DNdict = {}
        #We always want the black target, as we do not run into capture issues here
        #For any of the targets we grab, we need the same data
        if '4' in scenetargets:
            indextarget4 = np.where((missionData[1] == name) & (missionData[0] == '4'))
            #Store the standard deviation
            std4 = missionData[10:15,indextarget4[0]]
            #Store the target average pixel value
            DN4 = missionData[5:10,indextarget4[0]]
            #Store the corresponding svc file number
            svcfilenumber = missionData[31,indextarget4]
            framestd['target4'] = std4
            svcdict['target4'] = svcfilenumber
            DNdict['target4'] = DN4
            #Since black will always be a valid target, lets grab a flight altitude here
            #If we are still climbing or descending, we don't want this frame
            altitude = missionData[4,indextarget4]
            if float(altitude[0][0]) < requiredAlt:
                continue
        #Ideally we want the brightest white target, but lets grab all 'whites' here
        #5 is our wooden white cal target
        if '5' in scenetargets:
            indextarget5 = np.where((missionData[1] == name) & (missionData[0] == '5'))
            std5 = missionData[10:15,indextarget5[0]]
            DN5 = missionData[5:10,indextarget5[0]]
            svcfilenumber = missionData[31,indextarget5]
            framestd['target5'] = std5
            svcdict['target5'] = svcfilenumber
            DNdict['target5'] = DN5
        #Brightest white on the tribar target
        if '1' in scenetargets:
            indextarget1 = np.where((missionData[1] == name) & (missionData[0] == '1'))
            std1 = missionData[10:15,indextarget1[0]]
            DN1 = missionData[5:10,indextarget1[0]]
            svcfilenumber = missionData[31,indextarget1]
            framestd['target1'] = std1
            svcdict['target1'] = svcfilenumber
            DNdict['target1'] = DN1
        #Our gray target on the white tribar
        if '2' in scenetargets:
            indextarget2 = np.where((missionData[1] == name) & (missionData[0] == '2'))
            std2 = missionData[10:15,indextarget2[0]]
            DN2 = missionData[5:10,indextarget2[0]]
            svcfilenumber = missionData[31,indextarget2]
            framestd['target2'] = std2
            svcdict['target2'] = svcfilenumber
            DNdict['target2'] = DN2

        #All that has been done so far is grabbing data from our target csv file
        #Now we need to manipulate all of the values
        reflectancedict = {}
        #Lets grab a reflectance value for every SVC file that we have, and
        #combining that with our camera RSR measurements
        for key, value in svcdict.items():
            SVCfilename = 'T' + value[0][0].zfill(3) + '.sig'
            SVCfile = glob.glob(SVCdirectory + '*' + SVCfilename)
            reflectancevalues = [findReflectance(SVCfile[0],cameraresponseSR,'Blue'),findReflectance(SVCfile[0],cameraresponseSR,'Green'),findReflectance(SVCfile[0],cameraresponseSR,'Red'),findReflectance(SVCfile[0],cameraresponseSR,'Red Edge'),findReflectance(SVCfile[0],cameraresponseSR,'NIR')]
            reflectancedict[key] = reflectancevalues

        #If we have more than two targets in scene, we have to make a decision
        #on what to use for ELM
        if len(framestd) >= 2:
            #If our standard deviation indicates saturation, we should avoid that target
            #print(framestd.values())
            for key, value in framestd.items():
                if '0' in value:
                    del reflectancedict[key]
                    del DNdict[key]
                if '0.0' in value:
                    del reflectancedict[key]
                    del DNdict[key]
            #If we still have two targets in scene, and one is black, we can do ELM
            if len(DNdict) >= 2 and 'target4' in DNdict.keys():
                for key,value in DNdict.items():
                    #Brightest target after all of this filtering is still priority
                    if 'target5' in DNdict:
                        gotoTarget = 'target5'
                    elif 'target1' in DNdict:
                        gotoTarget = 'target1'
                    elif 'target2' in DNdict:
                        gotoTarget = 'target2'
                #Grab the reflectance values and DN required for ELM
                whiteReflect = np.asarray(reflectancedict[gotoTarget])
                blackReflect = np.asarray(reflectancedict['target4'])
                whiteDN = DNdict[gotoTarget].astype(np.float)
                blackDN = DNdict['target4'].astype(np.float)
                #Perform ELM for each band
                for band in np.arange(5):
                    slope = (whiteReflect[band] - blackReflect[band])/(whiteDN[band] - blackDN[band])
                    intercept = whiteReflect[band] - slope * whiteDN[band]
                    #Grab the specialty of our method, irradiance based ELM
                    imagemetadatafile = processedimagedirectory + name[:8] + '_' + str(band+1) + '.tif'
                    metadatadict = metadataReader.metadataGrabber(imagemetadatafile)
                    irradiance = metadatadict['Xmp.Camera.Irradiance']
                    #Our series of LUT for generating reflectance imagery
                    LUTdict[(band,irradiance)] = (slope,intercept,name)
                    #If we get this far we need to log some info
                    if logging == True:
                        with open(csvfile,'a', newline = '\n') as currentTextFile:
                            writer = csv.writer(currentTextFile, delimiter = ',')
                            writer.writerow([name,altitude[0][0],band,irradiance,gotoTarget,whiteReflect[band],whiteDN[band][0],framestd[gotoTarget][band][0],'target4',blackReflect[band],blackDN[band][0],framestd['target4'][band][0], slope[0],intercept[0]])
    return LUTdict

def applyLuts(LUTdict, processedimagedirectory, geoTiff):
    #Apply our fancy LUT to an image to generate a reflectance image
    print(geoTiff[-13:-5])
    #Read in image/raster with gdal
    imageStack = gdal.Open(geoTiff).ReadAsArray()
    imageStack = np.moveaxis(imageStack, 0 ,-1)
    #Prepare a store of values for reflectance
    reflectanceImage = np.zeros(np.shape(imageStack))
    #Cycle through each band seperately to take advantage of ELM LUTS and doc the LUT used
    CurrentIrradiance = []
    ClosestIrradiance = []
    ReferenceImage = []
    Band = []
    for band in np.arange(1,6):
        rawimage = processedimagedirectory + geoTiff[-13:-5] + '_{}'.format(band) + '.tif'
        metadatadict = metadataReader.metadataGrabber(rawimage)
        #Load in image irrradiance
        irradiance = metadatadict['Xmp.Camera.Irradiance']
        refIrradiance = []
        for key, value in LUTdict.items() :
            if key[0] == band-1:
                refIrradiance.append(key[1])
        #Find the closest irradiance between the LUT and current image
        refIrradiance = np.asarray(refIrradiance)
        comparison = np.abs(refIrradiance-irradiance)
        closestIrradiance = refIrradiance[np.argmin(comparison)]
        dictionaryreadkey = (band-1,closestIrradiance)
        #Grab the calibration coefficients from the LUT
        slope = LUTdict[dictionaryreadkey][0][0]
        intercept = LUTdict[dictionaryreadkey][1][0]
        referenceImage = LUTdict[dictionaryreadkey][2]
        #Generate the reflectance band
        reflectanceImage[:,:,band-1] = imageStack[:,:,band-1] * slope + intercept
        print(np.max(reflectanceImage[:,:,band-1]))
        CurrentIrradiance.append(irradiance)
        ClosestIrradiance.append(closestIrradiance)
        ReferenceImage.append(referenceImage)
        Band.append(band-1)


    return reflectanceImage,CurrentIrradiance,ReferenceImage,ClosestIrradiance,Band

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

    #Time Specific Files
    processedimagedirectory = '/research/imgs589/imageLibrary/DIRS/20171108/Missions/1330_375ft/micasense/processed/'
    missionDatafilename = '/research/imgs589/imageLibrary/DIRS/20171108/Missions/1330_375ft/micasense/Flight_20171108T1330_375ft_kxk8298.csv'
    reflectanceDir = '/research/imgs589/imageLibrary/DIRS/20171108/Missions/1330_375ft/micasense/reflectanceproduct/'
    imagelist = glob.glob('/research/imgs589/imageLibrary/DIRS/20171108/Missions/1330_375ft/micasense/geoTiff/*.tiff')

    #Date Specific Files
    SVCdirectory = '/research/imgs589/imageLibrary/DIRS/20171108/SVC/'

    #Device Specific Files
    cameraresponseSR = '/research/imgs589/imageLibrary/DIRS/MonochrometerTiffs/Spectral_Response.csv'

    if not os.path.exists(reflectanceDir):
        os.makedirs(reflectanceDir)
    LUTdict = findLUTS(missionDatafilename,processedimagedirectory,cameraresponseSR)
    logging = True

    if logging == True:
        csvfile = '/'.join(missionDatafilename.split('/')[:-1])+'/ELM_App_logger.csv'
        with open(csvfile,'w', newline = '\n') as currentTextFile:
            writer = csv.writer(currentTextFile, delimiter = ',')
            writer.writerow(['Image','Band','Irradiance','Ref Image','Ref Irradiance'])

    print(time.time() - starttime)
    imagelist.sort()
    for image in imagelist:
        ReflectanceImage,CurrentIrradiance,ReferenceImage,ClosestIrradiance,Band = applyLuts(LUTdict, processedimagedirectory, image)
        imagename = 'ref' + image[-13:]
        if logging == True:
            csvfile = '/'.join(missionDatafilename.split('/')[:-1])+'/ELM_App_logger.csv'
            with open(csvfile,'a', newline = '\n') as currentTextFile:
                writer = csv.writer(currentTextFile, delimiter = ',')
                for index in np.arange(len(CurrentIrradiance)):
                    writer.writerow([imagename,Band[index],CurrentIrradiance[index],ReferenceImage[index],ClosestIrradiance[index]])

        #Stuff to write out image to server using gdal
        height, width, channels = ReflectanceImage.shape
        driver = gdal.GetDriverByName( 'GTiff' )
        if ReflectanceImage.dtype == 'uint8':
            GDT = gdal.GDT_Byte
        elif ReflectanceImage.dtype == 'uint16':
            GDT = gdal.GDT_UInt16
        elif ReflectanceImage.dtype == 'float32':
            GDT = gdal.GDT_Float32
        elif ReflectanceImage.dtype == 'float64':
            GDT = gdal.GDT_Float64
        ds = driver.Create (reflectanceDir + imagename, width, height, channels, GDT)
        pWidth, pHeight = 1.0, 1.0
        X, Y = 0.0, 0.0
        geoTransform = ([X,pWidth,0,Y,0,pHeight])
        ds.SetGeoTransform(geoTransform)
        wktProjection = ''
        #srs = osr.SpatialReference(wkt = "")
        ds.SetProjection(wktProjection)
        for band in range(1, ReflectanceImage.shape[2]+1):
            ds.GetRasterBand(band).WriteArray(ReflectanceImage[:,:,band-1])
        ds.FlushCache()
        ds = None
    print(time.time() - starttime)
