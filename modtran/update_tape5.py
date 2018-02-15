import numpy
import os.path

def update_tape5(filename='tape5', modelAtmosphere=2,
                                   pathType=2,
                                   surfaceAlbedo=1.0,
                                   surfaceTemperature=303.15,
                                   albedoFilename=None,
                                   targetLabel=None,
                                   backgroundLabel=None,
                                   visibility=0.0,
                                   groundAltitude=0.168,
                                   sensorAltitude=0.268,
                                   targetAltitude=0.168,
                                   sensorZenith=180.0,
                                   sensorAzimuth=0.0,
                                   dayNumber=313,
                                   extraterrestrialSource=0,
                                   latitude=43.041,
                                   longitude=77.698,
                                   timeUTC = 15.0,
                                   startingWavelength=0.30,
                                   endingWavelength=1.2,
                                   wavelengthIncrement=0.001,
                                   fwhm=0.001):

   """
   title::
      update_tape5

   description::
      Create a "tape5" input file for MODTRAN v.4 with default parameters
      or using updated named parameters given below.

   attributes::
      filename
         Complete path/filename for the "tape5" file to be created (by default
         a file named "tape5" will be created in the directory from which this
         method is exectuted

      modelAtmosphere (MODEL)
         1 Tropical Atmosphere (15° North Latitude)
         2 Mid-Latitude Summer (45° North Latitude)
         3 Mid-Latitude Winter (45° North Latitude)
         4 Sub-Arctic Summer (60° North Latitude)
         5 Sub-Arctic Winter (60° North Latitude)
         6 1976 US Standard Atmosphere
         7 User-specified model atmosphere (radiosonde data) is to be read in

      pathType (ITYPE)
         1 Horizontal (constant-pressure) path, i.e., single layer, no
           refraction calculation
         2 Vertical or slant path between two altitudes
         3 Vertical or slant path to space or ground

      surfaceAlbedo (SURREF)
         Albedo of the earth, equal to one minus the surface emissivity and
         spectrally independent (constant)

      surfaceTemperature (AATEMP)
         Area-averaged ground surface temperature [K]

      albedoFilename (SALBFL)
         Name of the spectral albedo data file / If specified, then the
         surface albedo (SURREF) will be set equal to 'LAMBER' and
         CARD 4A, CARD 4L1, and CARD 4L2 will be included to specify the
         target and background names in the provided spectral albedo file

      targetLabel (CSALB)
         The number or name associated with a target spectral albedo curve
         from the spectral albedo data file

      backgroundLabel (CSALB)
         The number or name associated with a background spectral albedo curve
         from the spectral albedo data file

      visibility (VIS)
         > 0.0 User specified surface meteorological range (km)
         = 0.0 Uses the default meteorological range set by IHAZE

      groundAltitude (GNDALT)
         Altitude of surface relative to sea level (km). GNDALT may be negative
         but may not exceed 6 km / The baseline 0 to 6-km aerosol profiles are
         compressed (or stretched) based on input GNDALT / GNDALT is set to the
         first profile altitude when radiosonde data is used (MODEL = 7)

      sensorAltitude (H1)
         Initial altitude (km)

      targetAltitude (H2)
         Final altitude (km)

      sensorZenith (H2)
         Initial zeneth angle (degrees) as measured from H1 (180.0 is straight
         down)

      dayNumber (IDAY)
         Day of the year from 1 to 365

      extraterrestrialSource (ISOURC)
         0 Sun
         1 Moon (or Sun off)

      latitude (PARM1 of CARD3A2 when IPARM=0)
         Observer latitude (-90 degrees to +90 degrees)

      longitude (PARM2 of CARD3A2 when IPARM=0)
         Observer longitude (0 degrees to 360 degress west of Greenwich)

      timeUTC (TIME)
         Greenwich time in decimal hours (e.g. 8:45am is 8.75, 5:20pm is 17.33)

      sensorAzimuth (PSIPO)
         Sensor (path) azimuth degrees East of North (i.e. due North is 0.0
         degrees, due East is 90.0 degrees)

      startingWavelength (V1)
         Initial wavelength in units of microns

      endingWavelength (V2)
         Final wavelength in units of microns

      wavelengthIncrement (DV)
         Wavelength increment used for spectral outputs (the recommended value
         FWHM / 2) in units of microns

      fwhm (FWHM)
         Slit function full width at half maximum in units of microns (no
         convolution is performed if FWHM equals the bin size and the default
         slit function is selected)

   author::
      Carl Salvaggio

   copyright::
      Copyright (C) 2018, Rochester Institute of Technology

   license::
      GPL

   version::
      1.0.0

   disclaimer::
      This source code is provided "as is" and without warranties as to
      performance or merchantability. The author and/or distributors of
      this source code may have made statements about this source code.
      Any such statements do not constitute warranties and shall not be
      relied on by the user in deciding whether to use this source code.

      This source code is provided without any express or implied warranties
      whatsoever. Because of the diversity of conditions and hardware under
      which this source code may be used, no warranty of fitness for a
      particular purpose is offered. The user is advised to test the source
      code thoroughly before relying on it. The user must assume the entire
      risk of using the source code.
   """

   # Default tape 5 card deck
   card1 = 'TS  2    2    2    1    0    0    0    0    0    0    1    0    0   0.000   1.00'
   card1a = 'T   8T   0 360.00000         0         0 T F F         0.000'
   card1a2 = ''
   card2 = '    1    1    0    0    0    0   0.00000   0.00000   0.00000   0.00000   0.16800'
   card3 = '     0.268     0.168   180.000     0.000     0.000     0.000    0          0.000'
   card3a1 = '    1    2  313    0'
   card3a2 = '    43.041    77.698     0.000     0.000    15.000     0.000     0.000     0.000'
   card4 = '     0.350     1.200     0.001     0.001RM        MR A   '
   card4a = None
   card4l1 = None
   card4l2 = None
   card5 = '    0'

   # Update cards using default or user-provided parameters
   card1 = card1[0:2] + '{0:3d}'.format(modelAtmosphere) + card1[5:]
   card1 = card1[0:5] + '{0:5d}'.format(pathType) + card1[10:]
   card1 = card1[0:65] + '{0:8.3f}'.format(surfaceTemperature) + card1[73:]

   if albedoFilename:
      card1 = card1[0:73] + ' LAMBER'
      numberSurfaces = 0
      if targetLabel:
         numberSurfaces += 1
      if backgroundLabel:
         numberSurfaces += 1
      if numberSurfaces > 0:
         card4a = '{0:1d}'.format(numberSurfaces)
         card4a += '{0:9.0f}'.format(surfaceTemperature)
         card4l1 = '{0:<80}'.format(albedoFilename)
         card4l2 = '{0:<80}'.format(targetLabel) if targetLabel else ''
         if backgroundLabel:
            card4l2 += \
               '\n' + \
               '{0:<80}'.format(backgroundLabel) if backgroundLabel else ''
   else:
      card1 = card1[0:73] + '{0:7.2f}'.format(surfaceAlbedo)

   card2 = card2[0:30] + '{0:10.5f}'.format(visibility) + card2[40:]
   card2 = card2[0:70] + '{0:10.5f}'.format(groundAltitude)
   card3 = '{0:10.3f}'.format(sensorAltitude) + card3[10:]
   card3 = card3[0:10] + '{0:10.3f}'.format(targetAltitude) + card3[20:]
   card3 = card3[0:20] + '{0:10.3f}'.format(sensorZenith) + card3[30:]
   card3a1 = card3a1[0:10] + '{0:5d}'.format(dayNumber) + card3a1[15:]
   card3a1 = card3a1[0:15] + '{0:5d}'.format(extraterrestrialSource) + \
             card3a1[20:]
   card3a2 = '{0:10.3f}'.format(latitude) + card3a2[10:]
   card3a2 = card3a2[0:10] + '{0:10.3f}'.format(longitude) + card3a2[20:]
   card3a2 = card3a2[0:40] + '{0:10.3f}'.format(timeUTC) + card3a2[50:]
   card3a2 = card3a2[0:50] + '{0:10.3f}'.format(sensorAzimuth) + card3a2[60:]
   card4 = '{0:10.3f}'.format(startingWavelength) + card4[10:]
   card4 = card4[0:10] + '{0:10.3f}'.format(endingWavelength) + card4[20:]
   card4 = card4[0:20] + '{0:10.3f}'.format(wavelengthIncrement) + card4[30:]
   card4 = card4[0:30] + '{0:10.3f}'.format(fwhm) + card4[40:]

   # Write card deck to specified file
   f = open(filename, 'w')
   f.write(card1 + '\n')
   f.write(card1a + '\n')
   f.write(card1a2 + '\n')
   f.write(card2 + '\n')
   f.write(card3 + '\n')
   f.write(card3a1 + '\n')
   f.write(card3a2 + '\n')
   f.write(card4 + '\n')
   if card4a:
      f.write(card4a + '\n')
      if card4l1:
         f.write(card4l1 + '\n')
      if card4l2:
         f.write(card4l2 + '\n')
   f.write(card5 + '\n')
   f.close()

   return None


if __name__ == '__main__':

   import radiometry.modtran
   import time

   home = os.path.expanduser('~')
   path = home
   tape5Filename = os.path.join(path, 'tape5')
   tape7Filename = os.path.join(path, 'tape7.scn')

   # Typical path between two altitudes run
   radiometry.modtran.update_tape5(
      filename=tape5Filename,
      pathType=2,
      extraterrestrialSource=0,
      sensorAltitude=0.268,
      targetAltitude=0.168,
      sensorZenith=180.0,
      sensorAzimuth=0.0)

   # Typical downwelling radiance run
   radiometry.modtran.update_tape5(
      filename=tape5Filename,
      pathType=3,
      extraterrestrialSource=0,
      sensorAltitude=0.168,
      targetAltitude=0.168,
      sensorZenith=45.0,
      sensorAzimuth=145.0)

   # Perform hemispheric integral to compute the diffuse downwelling radiance
   first = True
   dZenith = 10.0
   dAzimuth = 30.0
   for zenith in numpy.arange(0.0, 90.0, dZenith):
      for azimuth in numpy.arange(0.0, 360.0, dAzimuth):

         msg = 'Running MODTRAN for '
         msg += 'zenith={0:.1f} degrees, '.format(zenith)
         msg += 'azimuth={0:.1f} degrees'.format(azimuth)
         print(msg)

         radiometry.modtran.update_tape5(
            filename=tape5Filename,
            pathType=3,
            extraterrestrialSource=0,
            groundAltitude=0.168,
            sensorAltitude=0.168,
            targetAltitude=0.168,
            sensorZenith=zenith,
            sensorAzimuth=azimuth)

         os.chdir(path)
         startTime = time.time()
         os.system('/dirs/bin/modtran4' + '> /dev/null 2>&1')
         print('Elapsed time = {0} [s]'.format(time.time() - startTime))

         tape7 = radiometry.modtran.read_tape7(tape7Filename)

         downwelledComponent = \
            tape7['sol scat'] * \
            numpy.cos(numpy.radians(zenith)) * \
            numpy.sin(numpy.radians(zenith)) * \
            numpy.radians(dZenith) * \
            numpy.radians(dAzimuth)

         if first:
            downwelledSpectralRadiance = downwelledComponent
            first = False
         else:
            downwelledSpectralRadiance += downwelledComponent

   print('Downwelled spectral radiance:')
   print(downwelledSpectralRadiance)
