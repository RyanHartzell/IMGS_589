import argparse
import os
import numpy as np
from interp1 import interp1
from update_tape5 import update_tape5
from read_tape7 import read_tape7
import cv2
import csv
import copy
import glob
import sys
import matplotlib.pyplot as plt
import getpass
import tkinter
from tkinter import filedialog, ttk
import context
from context import targets
root = tkinter.Tk()
root.withdraw()
root.update()
userName = getpass.getuser()



testing = True

dZenith = 10
dAzimuth = 30
interpOrder = 1
extrap = False
if testing:
    dZenith = 45
    dAzimuth = 180


########## Define parameters for MODTRAN5 Card5 Modification ###################
modelAtmospheres = [1, 2, 3] #Tropical, Mid Lat Summer, Mid Lat Winter
#modelAtmosphere = [2]
#pathTypes = [1,2,3] #1-Horizontal Path 2-Slant Altitude 3-Slant Ground Space
pathTypes = [2,3] #Path type 2 is straight down type3 is the Look to Space
surfaceAlbedos = [0, 1] #0 is Ground Reflectance 1 is Solar Scattering
surfaceTemperature = 303.15
albedoFilename = None
targetLabel = None
backgroundLabel = None
visibility = 0
groundAltitude = 0.168
sensorAltitudes = [0.2137, 0.282] #213m, 700ft AGL, 282m, 925ft AGL
#sensorAltitudes = [0.268]
targetAltitude = 0.168 #168m, 551ft Ground Level
#sensorZeniths = list(np.linspace(0.0, 90.0, 90/dZenith+1)) #0 to 90 Downwelling
#sensorZeniths = [180.0] #180 IS STRAIGHT DOWN
#sensorAzimuths = list(np.linspace(0.0, 360.0, 360/dAzimuth+1)) # 0 to 360 Downwelling
#sensorAzimuths = [0.0]
dayNumbers = [1, 90, 180, 270] #Jan 1, April 1, June 30, Sept 28
#dayNumbers = [270]
extraterrestrialSource = 0 #0-Sun 1-Moon(Night)
latitude = 43.041 #Rochester, NY
longitude = 77.698 #Henrietta Firetower
timesUTC = [15.0, 17.0, 19.0] #11AM, 1PM, 3PM
#timesUTC = [15.0]
startingWavelength = 0.35 #Units of microns 350nm
endingWavelength = 1.2 #Units of Microns 1200nm
wavelengthIncrement = 0.001 #Units of Microns 1nm Increment
fwhm = 0.001 #If FWHM=Increment No Convolution
############### USE THESE FOR UPDATE TAPE 5 CODE ###############################


#########    GET THE FILENAMES AND PATHS FOR USE LATER     #####################

parser = argparse.ArgumentParser(description='Collect files for Modtran4 Runs')
parser.add_argument('-r', '--relativeSpectralResponse', type=str,
                                        help='The camera RSR excel file path')
parser.add_argument('-s', '--svcDirectory', type=str,
                                        help='The SVC File Directory')

args = parser.parse_args()
rsrPath = args.relativeSpectralResponse
svcDirPath = args.svcDirectory

currentDirectory = os.path.dirname(os.path.abspath(__file__))
#ex. /cis/otherstu/gvs6104/src/python/IMGS_589/modtran

if rsrPath is None:
    rsrPath = currentDirectory + '/FullSpectralResponse.csv'
    if not os.path.isfile(rsrPath):
        rsrPath = filedialog.askopenfilename(
                        initialdir = os.getcwd(),
                        title="Choose the camera RSR csv file",
                        filetypes=[("Comma Seperated Values", "*.csv")])

if svcDirPath is None:
    #DEFAULT DIRECTORY PATH
    svcDirPath = "/research/imgs589/imageLibrary/DIRS/20171108/SVC/"
    if not os.path.isdir(svcDirPath):
        svcDirPath = filedialog.askdirectory(
                initialdir = "/research/imgs589/imageLibrary/DIRS/",
                title="Choose the SVC Directory")

tape5Path = currentDirectory + '/tape5'
if not os.path.isfile(tape5Path):
    #TKinter filedialog box
    tape5Path = filedialog.askopenfilename(initialdir = os.getcwd(),
        title="Choose the modtran tape5 Card")

tape7Path = currentDirectory + '/tape7.scn'
if not os.path.isfile(tape7Path):
    #TKinter filedialog box
    tape7Path = filedialog.askopenfilename(initialdir = os.getcwd(),
        title="Choose the modtran tape7.scn output",
        filetypes=[("Scenario", "*.scn")])

albedoFilename = currentDirectory + '/spec_alb.dat'
if not os.path.isfile(specAlbPath):
    #TKinter filedialog box
    albedoFilename = filedialog.askopenfilename(initialdir = os.getcwd(),
        title="Choose the modtran spec_albp.dat file",
        filetypes=[("Data", "*.dat")])

#########     GET THE FILENAMES AND PATHS FOR USE LATER     ####################
######### tape7Path, tape5Path, svcDirPath, rsrPath, currentDirectory ##########


###############  Parse the svc and RSR for the necessary data   ################
samples = (endingWavelength-startingWavelength)/wavelengthIncrement+1
modtranWL = np.linspace(startingWavelength, endingWavelength, samples)
wLRange = np.max(modtranWL)-np.min(modtranWL)

with open(rsrPath, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    fieldnames = reader.fieldnames

rsrData = np.genfromtxt(rsrPath, delimiter=',', skip_header=1)
rsrData[rsrData < 0] = 0
rsrWavelengths = rsrData[:,0]*0.001 #Units of micrometers
rsrDict = {'Norm Raw Blue':0, 'Norm Raw Green':0,'Norm Raw Red':0,
            'Norm Raw RE':0,'Norm Raw IR':0}
for band in rsrDict.keys():
    rsr = rsrData[:,fieldnames.index(band)]
    rsr = interp1(rsrWavelengths, rsr, modtranWL, interpOrder, extrap)
    rsr[np.isnan(rsr)] = 0
    rsrDict[band] = rsr

flightNotes = '/'.join(svcDirPath.split('/')[:6]) + \
                '/GroundDocumentation/datasheets/Flight_Notes.tsv'

times,filenumbers,targetdescriptor = targets.ROIExtraction.fieldData(flightNotes)
descriptorList = ["Asphalt", "Grass", "Dark Gray Tri", "Medium Gray Tri",
                    "White Tri", "Concrete", "White Cal Panel (Shaded)",
                    "Black Cal Panel (Shaded)", "White Cal Panel",
                    "Black Cal Panel", "Red Felt (Sun)", "Blue Felt (Sun)",
                    "Green Felt (Sun)", "Brown Felt (Sun)"]

targetDictionary = dict(zip(filenumbers,targetdescriptor))
targetDictionary = { k:v for k, v in targetDictionary.items() if v in descriptorList}
#svcFiles = glob.glob(svcDirPath+"*.sig")
#print(list(glob.iglob(svcDirPath+"*112.sig")))
svcDict = {}
for k, v in targetDictionary.items():
    for f in glob.glob(svcDirPath+ "*.sig"):
        if f.endswith("{0}.sig".format(k)):
            svcDict[f] = v
#targetDictionary = { k:v  for k,v in targetDictionary.items() if k for f in svcFiles if
#                any(f.endswith("{0}.sig".format(k))) for n in targetDictionary.keys() }
#print(svcFiles)
#print(len(svcDict.keys()))
#sys.exit(0)

#tgtFileNum = filenumbers[np.isin(targetdescriptor, descriptorList)]
#svcFiles = sorted([f for f in glob.glob(svcDirPath+"*.sig") if
#                any(f.endswith("{0}.sig".format(n)) for n in tgtFileNum)])


if len(svcDict) == 0:
    msg = "No SVC Files with good descriptors were found in the given directory"
    raise ValueError(msg)

##### GETS ALL THE SVC FILES OF THE TARGETS LISTED IN THE DESCRIPTOR LIST ######
################ Returns: rsr(wavelengths,b,g...), svcDICT  ####################



#################### TIME TO START THE LOOPS ###################################
with open(currentDirectory + os.path.sep + userName + "MODTRAN.csv",
                                                    'w', newline= '\n') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['Model Atmosphere', 'Path Type', 'Day', 'Time', 'Altitude',
                    'Target Descriptor','SVC Filename', 'Band Integrated Blue',
                    'Band Integrated Green', 'Band Integrated Red',
                    'Band Integrated RedEdge', 'Band Integrated Infrared'])


    for modelAtmosphere in modelAtmospheres:
        for sensorAltitude in sensorAltitudes:
            for dayNumber in dayNumbers:
                for timeUTC in timesUTC:

                    for pathType in pathTypes:
                        if pathType == 2: #Downwelling
                            sensorZeniths = [180.0]
                            sensorAzimuths = [0.0]
                        elif pathType == 3:
                            sensorZeniths = list(np.linspace(0.0, 90.0, 90/dZenith+1))
                            sensorAzimuths = list(np.linspace(0.0, 360.0, 360/dAzimuth+1))
                        angSumSolScat = 0
                        angSumGrndReflt = 0

                        for sensorZenith in sensorZeniths:
                            zeinith = np.radians(sensorZenith)
                            for sensorAzimuth in sensorAzimuths:
                                azimuth = np.radians(sensorAzimuth)

                                for surfaceAlbedo in surfaceAlbedos:
                                    #Updates the tape 5 file with new params
                                    # print("Tape 5 Path: ", tape5Path)
                                    # print("Model Atmosphere ", modelAtmosphere)
                                    # print("Path Type ", pathType)
                                    # print("Surface Albedo ", surfaceAlbedo)
                                    # print("Visibility ", visibility)
                                    # print("Ground Altitude ", groundAltitude)
                                    # print("Sensor Altitude ", sensorAltitude)
                                    # print("Target Altitude ", targetAltitude)
                                    # print("Sensor Zenith ", sensorZenith)
                                    # print("Sensor Azimuth ", sensorAzimuth)
                                    # print("Day Number ", dayNumber)
                                    # print("Space Source ", extraterrestrialSource)
                                    # print("Latitude ", latitude)
                                    # print("Longitude ", longitude)
                                    # print("Time UTC ", timeUTC)
                                    # print("Starting Wavelength ", startingWavelength)
                                    # print("End Wavelength ", endingWavelength)
                                    # print("Wavelength Increment ", wavelengthIncrement)
                                    # print("Full Width Half Max ", fwhm)

                                    update_tape5(tape5Path,
                                                modelAtmosphere,
                                                pathType,
                                                surfaceAlbedo,
                                                visibility,
                                                groundAltitude,
                                                sensorAltitude,
                                                targetAltitude,
                                                sensorZenith,
                                                sensorAzimuth,
                                                dayNumber,
                                                extraterrestrialSource,
                                                latitude,
                                                longitude,
                                                timeUTC,
                                                startingWavelength,
                                                endingWavelength,
                                                wavelengthIncrement,
                                                fwhm)

                                    print("Running modtran4, Albedo: {0}".format(
                                                                surfaceAlbedo))
                                    try:
                                        os.system('/dirs/bin/modtran4' + \
                                                    '> /dev/null 2>&1')
                                    except KeyboardInterrupt:
                                        print("User Quit Modtran4")
                                        sys.exit(0)

                                    print("Reading tape7")
                                    tape7Dict = read_tape7(tape7Path)
                                    if any(v.size for v in tape7Dict.values()) == 0:
                                        msg = "Tape 7 has no information. Please "+\
                                        "check your inputs for tape 5"
                                        raise ValueError(msg)

                                    if surfaceAlbedo == 0:
                                        solScat = tape7Dict['sol scat']
                                        if pathType == 2:
                                            angSumSolScat += solScat
                                        elif pathType == 3:
                                            angSumSolScat += solScat * \
                                            np.cos(zeinith)* np.sin(zeinith) * \
                                            np.radians(dZenith) * np.radians(dAzimuth)

                                    elif surfaceAlbedo == 1:
                                        angSumGrndReflt += tape7Dict['grnd rflt']

                        #print("Angle Sum Ground Reflectance: ", angSumGrndReflt)
                        #print("Angle Sum Solar Scattering: ", angSumSolScat)
                        for s, t in svcDict.items():
                            wL, _, _, svcRef = targets.svcReader.svcGrabber(s)
                            tgtRefl = interp1((wL*0.001), svcRef, tape7Dict['wavlen mcrn'],
                                                            interpOrder, extrap)
                            tgtRefl[np.isnan(tgtRefl)] = 0

                            radiance = tgtRefl*angSumGrndReflt+ angSumSolScat

                            bIntDict = copy.deepcopy(rsrDict)
                            for b in rsrDict.keys():
                                beRadiance = radiance * rsrDict[b]
                                biRad = np.trapz(beRadiance, wLRange)
                                biRSR = np.trapz(rsrDict[b], wLRange)
                                #biRad = np.sum(beRadiance)/wLRange
                                #biRSR = np.sum(rsrDict[b])/wLRange
                                bIntDict[b] = biRad/biRSR

                            line = [modelAtmosphere, pathType, dayNumber, int(timeUTC),
                                    sensorAltitude, t, os.path.basename(s)[-13:-4],
                                    bIntDict['Norm Raw Blue'],
                                    bIntDict['Norm Raw Green'],
                                    bIntDict['Norm Raw Red'],
                                    bIntDict['Norm Raw RE'],
                                    bIntDict['Norm Raw IR']]
                            print(line)
                            writer.writerow(line)
