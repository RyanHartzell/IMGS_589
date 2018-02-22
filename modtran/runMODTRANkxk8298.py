#import radiometry.modtran
import time
from read_tape7 import *
from update_tape5 import *
import numpy as np
from matplotlib import pyplot
import csv

home = os.path.expanduser('~')
path = home
specalbFilename = os.path.join(path, 'spec_alb.dat')
tape5Filename = os.path.join(path, 'tape5')
tape7Filename = os.path.join(path, 'tape7.scn')
csvfile = os.path.join(path, 'grass18background.csv')
#New Stuff

#Tropical Atmosphere, Mid-Latitude Summer, and Sub-Artic Summer
ModelAtmosphere = [2]
#DayNumber = [0,90,180,270]
DayNumber = [312]
TimeUTC = [15.0]
#Sensor altitude as flight altitude plus sea level approximation
SensorAltitude = [.2823]
sensorAltitude = 0.2823
groundAltitude = 0.168
targetAltitude = 0.168
#Other params
#SurfaceAlbedo = [1.0,0.0]
dZenith = 2.5
dAzimuth = 5.0

#Other parameters
visibility = 0.0
background = 'constant, 18%'
target = 'healthy grass'
#All other values to default to update_tape5 code

firstscat = True
firstrefl = True

for modelAtmosphere in ModelAtmosphere:
   for dayNumber in DayNumber:
      for timeUTC in TimeUTC:
         for sensorAltitude in SensorAltitude:
            msg = 'Running MODTRAN for '
            msg += 'Atmosphere {}, '.format(modelAtmosphere)
            msg += 'Day {}, '.format(dayNumber)
            msg += 'Time in UTC: {}, '.format(timeUTC)
            msg += 'Alt MSL  {}'.format(sensorAltitude)
            print(msg)
            for zenith in numpy.arange(0.0, 90.0, dZenith):
               for azimuth in numpy.arange(0.0, 360.0, dAzimuth):

                 submsg = 'Running MODTRAN for '
                 submsg += 'zenith={0:.1f} degrees, '.format(zenith)
                 submsg += 'azimuth={0:.1f} degrees'.format(azimuth)
                 print(submsg)
                 update_tape5(
                    filename=tape5Filename,
                    modelAtmosphere=modelAtmosphere,
                    pathType=2,
                    surfaceAlbedo='LAMBER',
                    surfaceTemperature=303.15,
                    albedoFilename='spec_alb.dat',
                    targetLabel=target,
                    backgroundLabel=background,
                    visibility=visibility,
                    groundAltitude=groundAltitude,
                    sensorAltitude=sensorAltitude,
                    targetAltitude=100,
                    sensorZenith=zenith,
                    sensorAzimuth=azimuth,
                    dayNumber=dayNumber,
                    extraterrestrialSource=0,
                    latitude=43.041,
                    longitude=77.698,
                    timeUTC = timeUTC,
                    startingWavelength=0.30,
                    endingWavelength=1.2,
                    wavelengthIncrement=0.001,
                    fwhm=0.001)

                 os.chdir(path)
                 print(path)
                 cwd = os.getcwd()
                 print(cwd)
                 startTime = time.time()
                 os.system('/dirs/bin/modtran4' + '> /dev/null 2>&1')
                 print('Elapsed time = {0} [s]'.format(time.time() - startTime))

                 tape7 = read_tape7(tape7Filename)
                 print(tape7Filename)
                 downwelledComponent = \
                    tape7['sol scat'] * \
                    np.cos(numpy.radians(zenith)) * \
                    np.sin(numpy.radians(zenith)) * \
                    np.radians(dZenith) * \
                    np.radians(dAzimuth)

                 if firstscat:
                    downwelledSpectralRadiance = downwelledComponent
                    firstscat = False
                 else:
                    downwelledSpectralRadiance += downwelledComponent

#Run for target reflectance/radiance

print('Last MODTRAN run, checking ground reflected target')

update_tape5(
    filename=tape5Filename,
    modelAtmosphere=2,
    pathType=2,
    surfaceAlbedo='LAMBER',
    surfaceTemperature=303.15,
    albedoFilename='spec_alb.dat',
    targetLabel=target,
    backgroundLabel=background,
    visibility=visibility,
    groundAltitude=groundAltitude,
    sensorAltitude=sensorAltitude,
    targetAltitude=targetAltitude,
    sensorZenith=180,
    sensorAzimuth=0,
    dayNumber=dayNumber,
    extraterrestrialSource=0,
    latitude=43.041,
    longitude=77.698,
    timeUTC = timeUTC,
    startingWavelength=0.30,
    endingWavelength=1.2,
    wavelengthIncrement=0.001,
    fwhm=0.001)

os.chdir(path)
print(path)
cwd = os.getcwd()
print(cwd)
startTime = time.time()
os.system('/dirs/bin/modtran4' + '> /dev/null 2>&1')
print('Elapsed time = {0} [s]'.format(time.time() - startTime))

tape7 = read_tape7(tape7Filename)
wavelength = tape7['wavlen mcrn']
groundReflectance = tape7['grnd rflt']
solarScattering= tape7['sol scat']
reflectedDownwelling = tape7['drct rflt']
totalRadiance = tape7['total rad']

#csvFile = open(csvfile, 'w', newline = '\n')
with open(csvfile,'w', newline = '\n') as currentTextFile:
    writer = csv.writer(currentTextFile, delimiter = ',')

    writer.writerow(['Model Atmosphere','Visibility','Day','Time','Ground Altitude','Sensor Altitude', 'Target Altitude', 'dZenith', 'dAzimuth', 'Background', 'Target'])
    writer.writerow([modelAtmosphere,visibility,dayNumber,timeUTC,groundAltitude,sensorAltitude, targetAltitude, dZenith, dAzimuth, background, target])
    writer.writerow(['wavelength','groundReflectance','solarScattering','reflectedDownwelling','totalRadiance'])
    for i in np.arange(0,wavelength.size):
        writer.writerow([wavelength[i],groundReflectance[i],solarScattering[i],reflectedDownwelling[i],totalRadiance[i]])


#writer.writerow['Model Atmosphere', 'Visibility', 'Day', 'Time', 'Ground Altitude', 'Sensor Altitude', 'Target Altitude', 'Zenith', 'Azimuth', 'Background', 'Target']

#if simType == 'target':
#    if csvType == 'real':
#        writer.writerow(['Model Atmosphere', 'Visibility', 'Day', 'Time', 'Ground Altitude', 'Sensor Altitude', 'Target Altitude', 'Zenith', 'Azimuth', 'Background', 'Target', 'Band Integrated Blue', 'Band Integrated Green', 'Band Integrated Red', 'Band Integrated RedEdge', 'Band Integrated Infrared'])
#    elif csvType == 'rawTape7':
#        writer.writerow(['wavelength', 'scattered Path (sol scat)', 'reflected downwelling (grnd rflt - drct rflt)', 'ground reflected (grnd rflt)', 'sensor reaching (total rad)'])#
#
#elif simType == 'downwelling':
#    if csvType == 'real':
#        writer.writerow(['Model Atmosphere', 'Visibility', 'Day', 'Time', 'Ground Altitude', 'Sensor Altitude', 'Target Altitude', 'Albedo', 'Band Integrated Downwelling Blue', 'Band Integrated Downwelling Green', 'Band Integrated Downwelling Red', 'Band Integrated Downwelling RedEdge', 'Band Integrated Downwelling Infrared'])
#    elif csvType == 'rawTape7':
#        writer.writerow(['wavelength', 'Downwelling Spectral Radiance'])

pyplot.plot(wavelength,downwelledSpectralRadiance,color='blue')
pyplot.plot(wavelength,groundReflectance,color='cyan')
pyplot.plot(wavelength,solarScattering,color='red')
pyplot.plot(wavelength,reflectedDownwelling,color='green')
pyplot.plot(wavelength,totalRadiance,color='magenta')

pyplot.legend(['Hemispheric Downwelling','Ground Reflected', 'Scattered Path', 'Reflected Downwelling', 'Sensor Reaching'], loc='upper right')
pyplot.xlim(0.3,1.2)
pyplot.ylim(0,0.04)
pyplot.xlabel('Wavelength')
pyplot.ylabel('Spectral Radiance')
pyplot.show()
