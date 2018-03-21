import datetime
import pysolar.solar as ps
import pytz
import os

def find_solar_angles(parameters, year=2017, localzone='US/Eastern'):
    hour = int(parameters['timeUTC']) #Computes the hour from the given time
    minute = int((parameters['timeUTC']-hour) * 60) #Converts decimal min to minute

    #Instanciates the date based on the given time and daynumber given in UTC
    date = datetime.datetime(year, 1, 1, hour, minute, 0, tzinfo=pytz.utc) + \
        datetime.timedelta(parameters['dayNumber'] - 1)
    #Converts the UTC date to the local Timezone and takes care of daylight savings
    timestampEST = date.astimezone(pytz.timezone(localzone))

    latitude = parameters['latitude'] #Pulls the latitude from the parameters
    longitude = parameters['longitude'] #Pulls the longitude from the parameters
    #Computes the solar altitude above the horizon
    altitude = ps.get_altitude(latitude,-1*longitude, timestampEST)
    zenith = 90 - altitude #Converts the solar altitude to zenith angle
    #Computes the azimuth angle from the south
    azimuth = ps.get_azimuth(latitude, -1*longitude, timestampEST)
    azimuth = (180 - azimuth) % 360 #Converts azimuth to be measured from the north

    solarAngles = {"solarZenith": zenith, "solarAzimuth":azimuth}

    return solarAngles

if __name__ == "__main__":

    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    params = {'filename':currentDirectory+'/tape5',
        'modelAtmosphere':2, 'pathType':2,
        'surfaceAlbedo':None, 'surfaceTemperature':303.15,
        'albedoFilename':currentDirectory+'/spec_alb.dat',
        'targetLabel':"healthy grass",
        'backgroundLabel':"healthy grass",
        'visibility':15.0,
        'groundAltitude':0.168, 'sensorAltitude':0.2823,
        'targetAltitude':0.168, 'sensorZenith':None, 'sensorAzimuth':None,
        'dZenith': 45, 'dAzimuth':180,
        'dayNumber': 312,
        'extraterrestrialSource':0, 'latitude':43.041,
        'longitude':77.698, 'timeUTC':16.0,
        'startingWavelength':0.30, 'endingWavelength':1.2,
        'wavelengthIncrement':0.01, 'fwhm':0.001}

    solarAngles = find_solar_angles(params, 2017, 'US/Eastern')
    print(solarAngles['solarZenith'], solarAngles['solarAzimuth'])
