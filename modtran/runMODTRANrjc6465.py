def svcGrabber(filename):
	import numpy as np
	#Simple load in of spectrometer data in arrays
	data = np.loadtxt(filename,unpack = True, skiprows = 25,dtype = float)
	wavelength = data[0]
	reference = data[1]
	target = data[2]
	spectral_reflectance = data[3] #2/5/2018, this was changed from 'spectral_response' to 'spectral reflectance'. Functions below this were also adjusted
	return wavelength,reference,target,spectral_reflectance


import numpy as np
import os
import subprocess
import pandas as pd
import cv2
from update_tape5 import update_tape5
from read_tape7 import read_tape7
from interp1 import interp1
import matplotlib.pyplot as plt
import csv

baseDirectory = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
tape5Filename = os.path.join(baseDirectory, 'tape5')
tape7Filename = os.path.join(baseDirectory, 'tape7.scn')

# Perform hemispheric integral to compute the diffuse downwelling radiance
first = True
dZenith = 45
dAzimuth = 180
grndRfltFirst = True

# #Get SVC files to use for reference
baseSVCdir = '/research/imgs589/imageLibrary/DIRS/20171108/SVC/'
SVCFilenames = ['000000_0000_R092_T094.sig', '000000_0000_R092_T095.sig', '000000_0000_R092_T096.sig', '000000_0000_R092_T097.sig', '000000_0000_R092_T098.sig', '000000_0000_R092_T099.sig', '000000_0000_R108_T110.sig', '000000_0000_R108_T111.sig']




#get the RSR info
RSRFilePath = 'FullSpectralResponse.csv'
RSRdata = np.genfromtxt(baseDirectory + RSRFilePath, delimiter = ',', skip_header = 1)
RSR_wavelengths = RSRdata[:, 0] * 0.001

blueRSR_base= RSRdata[:, 17]
greenRSR_base= RSRdata[:, 18]
redRSR_base= RSRdata[:, 19]
redEdgeRSR_base= RSRdata[:, 20]
irRSR_base= RSRdata[:, 21]

#correct for any values < 0
blueRSR_base[blueRSR_base < 0] = 0
greenRSR_base[greenRSR_base < 0] = 0
redRSR_base[redRSR_base < 0] = 0
redEdgeRSR_base[redEdgeRSR_base < 0] = 0
irRSR_base[irRSR_base < 0] = 0


#get MODTRAN wavelengths and interpolate the measured RSRs to that spectral resolution
basetape7 = read_tape7(baseDirectory + 'tape7Base.scn')
MODTRANtape7Wavelengths = basetape7['wavlen mcrn']

blueRSR = interp1(RSR_wavelengths, blueRSR_base, MODTRANtape7Wavelengths)
greenRSR = interp1(RSR_wavelengths, greenRSR_base, MODTRANtape7Wavelengths)
redRSR = interp1(RSR_wavelengths, redRSR_base, MODTRANtape7Wavelengths)
redEdgeRSR = interp1(RSR_wavelengths, redEdgeRSR_base, MODTRANtape7Wavelengths)
irRSR = interp1(RSR_wavelengths, irRSR_base, MODTRANtape7Wavelengths)

blueRSR[np.isnan(blueRSR)] = 0
greenRSR[np.isnan(greenRSR)] = 0
redRSR[np.isnan(redRSR)] = 0
redEdgeRSR[np.isnan(redEdgeRSR)] = 0
irRSR[np.isnan(irRSR)] = 0



#Start CSV file
csvFile = open('rjc6465MODTRAN_AT' + '.csv', 'w', newline = '\n')
writer = csv.writer(csvFile, delimiter = ',')
writer.writerow(['Model Atmosphere', 'Day', 'Time', 'Altitude', 'SVC Filename', 'Band Integrated Blue', 'Band Integrated Green', 'Band Integrated Red', 'Band Integrated RedEdge', 'Band Integrated Infrared'])




#START
cumSolarScatteringComponent = 0
cumGroundReflectComponent = 0
for currentAtmos in np.arange(1, 3+1, 1): #for currentAtmos in np.arange(1, 3+1, 1)
	for currentDay in np.asarray([1, 90, 180, 270]): #np.asarray([1, 90, 180, 270]):
		for currentTime in np.asarray([15.0, 17.0, 19.0]): #np.asarray([15.0, 17.0, 19.0]):
			for currentAltitude in np.asarray([.2137, .282]):

				#Current sequence of iterated MODTRAN inputs
				for zenith in np.arange(0.0, 90.0, dZenith):
					for azimuth in np.arange(0.0, 360.0, dAzimuth):
						for currentAlbedo in np.asarray([0, 1]):



							# Typical path between two altitudes run
							update_tape5(
								modelAtmosphere=currentAtmos,
								dayNumber=currentDay,
								filename=tape5Filename,
								timeUTC = currentTime,
								pathType=3,
								extraterrestrialSource=0,
								groundAltitude=0.168,
								sensorAltitude=currentAltitude,
								targetAltitude=0.168,
								sensorZenith=zenith,
								sensorAzimuth=azimuth,
								surfaceAlbedo = currentAlbedo)


							os.system('/dirs/bin/modtran4' + '> /dev/null 2>&1')
							tape7 = read_tape7(tape7Filename)


							#get solar scattering component
							if currentAlbedo == 0:
								#calculate downwelled component
								downwelledComponent = \
									tape7['sol scat'] * \
									np.cos(np.radians(zenith)) * \
									np.sin(np.radians(zenith)) * \
									np.radians(dZenith) * \
									np.radians(dAzimuth)
								#print(len(downwelledComponent))
								if first:
									downwelledSpectralRadiance = downwelledComponent
									first = False
								else:
									downwelledSpectralRadiance += downwelledComponent

							#Get ground reflect component
							elif currentAlbedo == 1:
								currentGroundReflectComponent = tape7['grnd rflt']
								#print(len(currentGroundReflectComponent))
								if grndRfltFirst:
									groundReflectComponent = currentGroundReflectComponent
									grndRfltFirst = False
								else:
									groundReflectComponent += currentGroundReflectComponent


				#Current sequence over all azimuth/zenith angles
				cumSolarScatteringComponent = downwelledSpectralRadiance
				cumGroundReflectComponent = groundReflectComponent
				first = True
				grndRfltFirst = True
				downwelledSpectralRadiance = 0
				groundReflectComponent = 0

				for i in np.linspace(0, len(SVCFilenames), len(SVCFilenames)+1).astype(np.int32):
					currentSVCFilename = baseSVCdir + SVCFilenames[i]
					wavelength, reference, target, spectralReflectance_SVC = svcGrabber(currentSVCFilename)
					#interpolate SVC measurements to match MODTRAN spectral resolution, convert SVC wavelength from nm to um
					spectralReflectance = interp1((wavelength*0.001), spectralReflectance_SVC, tape7['wavlen mcrn'])
					spectralReflectance[np.isnan(spectralReflectance)] = 0

					sensorReachingRadiance = (spectralReflectance * cumGroundReflectComponent) + cumSolarScatteringComponent

					#calculate the band effective radiances for each band
					BER_blue = sensorReachingRadiance * blueRSR
					BER_green = sensorReachingRadiance * greenRSR
					BER_red = sensorReachingRadiance * redRSR
					BER_redEdge = sensorReachingRadiance * redEdgeRSR
					BER_ir = sensorReachingRadiance * irRSR

					#integrate to get band-integrated radiance for each band
					bandIntegratedBlue = np.sum(BER_blue)/(np.max(MODTRANtape7Wavelengths) - np.min(MODTRANtape7Wavelengths))
					bandIntegratedGreen = np.sum(BER_green)/(np.max(MODTRANtape7Wavelengths) - np.min(MODTRANtape7Wavelengths))
					bandIntegratedRed = np.sum(BER_red)/(np.max(MODTRANtape7Wavelengths) - np.min(MODTRANtape7Wavelengths))
					bandIntegratedRedEdge = np.sum(BER_redEdge)/(np.max(MODTRANtape7Wavelengths) - np.min(MODTRANtape7Wavelengths))
					bandIntegratedInfrared = np.sum(BER_ir)/(np.max(MODTRANtape7Wavelengths) - np.min(MODTRANtape7Wavelengths))
					#print(SVCFilenames[i])
					#print([bandIntegratedBlue, bandIntegratedGreen, bandIntegratedRed, bandIntegratedRedEdge, bandIntegratedInfrared])
					#print(' ')
					writer.writerow([currentAtmos, currentDay, currentTime, currentAltitude, SVCFilenames[i], bandIntegratedBlue, bandIntegratedGreen, bandIntegratedRed, bandIntegratedRedEdge, bandIntegratedInfrared])

csvFile.close()


# # print('Downwelled spectral radiance:')
# # print(downwelledSpectralRadiance)
