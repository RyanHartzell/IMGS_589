

import numpy as np
import os
import subprocess
import shutil
import time
import cv2
from update_tape5 import update_tape5
from read_tape7 import read_tape7

	
baseDirectory = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

tape5Filename = os.path.join(baseDirectory, 'tape5')
tape7Filename = os.path.join(baseDirectory, 'tape7.scn')

# Perform hemispheric integral to compute the diffuse downwelling radiance
first = True
dZenith = 45
dAzimuth = 180

grndRfltFirst = True

cumSolarScatteringComponent = 0
cumGroundReflectComponent = 0
for currentAtmos in np.arange(1, 3+1, 1): #for currentAtmos in np.arange(1, 3+1, 1)
	for currentDay in np.asarray([1, 90, 180, 270]): #np.asarray([1, 90, 180, 270]):
		for currentTime in np.asarray([15.0, 17.0, 19.0]): #np.asarray([15.0, 17.0, 19.0]):
			for currentAltitude in np.asarray([.2137, .282]):

				#solarScatteringComponent = 0
				for zenith in np.arange(0.0, 90.0, dZenith):
					for azimuth in np.arange(0.0, 360.0, dAzimuth):
						for currentAlbedo in np.asarray([0, 1])



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
								sensorAzimuth=azimuth
								surfaceAlbedo = currentAlbedo)


							os.system('/dirs/bin/modtran4' + '> /dev/null 2>&1')
							tape7 = read_tape7(tape7Filename)



							if currentAlbedo == 0:
								#calculate downwelled component
								downwelledComponent = \
									tape7['sol scat'] * \
									np.cos(np.radians(zenith)) * \
									np.sin(np.radians(zenith)) * \
									np.radians(dZenith) * \
									np.radians(dAzimuth)

								if first:
									downwelledSpectralRadiance = downwelledComponent
									first = False
								else:
									downwelledSpectralRadiance += downwelledComponent


							elif currentAlbedo == 1:
								currentGroundReflectComponent = tape7['grnd rflt']
								if grndRfltFirst:
									groundReflectComponent = currentGroundReflectComponent
									grndRfltFirst = False
								else:
									groundReflectComponent += currentGroundReflectComponent


				cumSolarScatteringComponent = downwelledSpectralRadiance
				cumGroundReflectComponent = 






# print('Downwelled spectral radiance:')
# print(downwelledSpectralRadiance)