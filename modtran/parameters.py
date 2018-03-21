import os
import os.path

class parameters(object):

    def __init__(self):
        self.filename = 'tape5'
        self.modelAtmosphere = 2
        self.pathType = 2
        self.surfaceAlbedo = None
        self.surfaceTemperature = 303.15
        self.albedoFilename = 'spec_alb.dat'
        self.targetLabel = "healthy grass"
        self.backgroundLabel = "healty grass"
        self.visibility = 15.0
        self.groundAltitude = 0.168
        self.sensorAltitude = 0.2823
        self.targetAltitude = 0.168
        self.sensorZenith = 180
        self.sensorAzimuth = 0
        self.dZenith = 10
        self.dAzimuth = 30
        self.dayNumber = 312
        self.extraterrestrialSource = 0
        self.latitude = 43.041
        self.longitude = 77.698
        self.timeUTC = 16.0
        self.startingWavelength = .30
        self.endingWavelength = 1.2
        self.wavelengthIncrement = 0.01
        self.fwhm = 0.001

class solar(parameters):
    import datetime
    import pysolar as ps
    import pytz

    def testdef(parameters):
        print(parameters)
        print(parameters.timeUTC)
        return parameters

    def arg(parameters):
        return "Testing"

    def compute_solar_angles(parameters, year=2017, localzone='US/Eastern'):
        hour = int(parameters.timeUTC) #Computes the hour from the given time
        minute = int((parameters.timeUTC-hour) * 60) #Converts decimal min to minute

        #Instanciates the date based on the given time and daynumber given in UTC
        date = datetime.datetime(year, 1, 1, hour, minute, 0, tzinfo=pytz.utc) + \
          datetime.timedelta(parameters.dayNumber - 1)
        #Converts the UTC date to the local Timezone and takes care of daylight savings
        timestampEST = date.astimezone(pytz.timezone(localzone))

        latitude = parameters.latitude #Pulls the latitude from the parameters
        longitude = parameters.longitude #Pulls the longitude from the parameters
        #Computes the solar altitude above the horizon
        altitude = ps.get_altitude(latitude,-1*longitude, timestampEST)
        zenith = 90 - altitude #Converts the solar altitude to zenith angle
        #Computes the azimuth angle from the south
        azimuth = ps.get_azimuth(latitude, -1*longitude, timestampEST)
        azimuth = (180 - azimuth) % 360 #Converts azimuth to be measured from the north

        return zenith, azimuth

class hemisphere(self, parameters):


    def update_parameters(self, dictionary):
        filename = dictionary['filename']
        modelAtmosphere = dictionary['modelAtmosphere']
        pathType = dictionary['pathType']
        surfaceAlbedo = dictionary['surfaceAlbedo']
        surfaceTemperature = dictionary['surfaceTemperature']
        albedoFilename = dictionary['albedoFilename']
        targetLabel = dictionary['targetLabel']
        backgroundLabel = dictionary['backgroundLabel']
        visibility = dictionary['visibility']
        groundAltitude = dictionary['groundAltitude']
        sensorAltitude = dictionary['sensorAltitude']
        targetAltitude = dictionary['targetAltitude']
        sensorZenith = dictionary['sensorZenith']
        sensorAzimuth = dictionary['sensorAzimuth']
        dZenith = dictionary['dZenith']
        dAzimuth = dictionary['dAzimuth']
        dayNumber = dictionary['dayNumber']
        extraterrestrialSource = dictionary['extraterrestrialSource']
        latitude = dictionary['latitude']
        longitude = dictionary['longitude']
        timeUTC = dictionary['timeUTC']
        startingWavelength = dictionary['startingWavelength']
        endingWavelength = dictionary['endingWavelength']
        wavelengthIncrement = dictionary['wavelengthIncrement']
        fwhm = dictionary['fwhm']
