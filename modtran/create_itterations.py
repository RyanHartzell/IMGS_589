import itertools
import numpy as np

def find_unique_itterations(parameters):
    #Finds all of the unique itterations in the parameter dictionary

    #Creates a dictionary of all the k-v pairs where the value is a list
    uniqueDict = {k:v for k,v in parameters.items()
                    if type(v) is list and len(v) > 1
                    if k != 'sensorZenith' if k != 'sensorAzimuth'}

    #Finds all of the k-v pairs where the value is a list of length one
    ones = {k:v[0] for k,v in parameters.items() if type(v) is list and len(v) == 1}
    #Updates the input parameters so length one lists are single values
    parameters.update(ones)

    return uniqueDict

def create_unique_itterations(parameters, uniqueDict, solarAngles,):

    listCombo = list(dict(zip(uniqueDict, x))
                        for x in itertools.product(*uniqueDict.values()))

    solZenith, solAzimuth = solarAngles['solarZenith'], solarAngles['solarAzimuth']
    dZ, dA = parameters['dZenith'], parameters['dAzimuth']
    zenithAngles = list(np.arange(0, 90 + dZ, dZ))
    azimuthAngles = list(np.arange(0, 360 + dA, dA))
    #zenithAngles = [z for z in zenithAngles if z > solZenith+5 or z < solZenith-5]
    #azimuthAngles = [a for a in azimuthAngles if a > solAzimuth+5 or a < solAzimuth-5]
    parameters['sensorZenith'] = zenithAngles
    parameters['sensorAzimuth'] = azimuthAngles

    angleDict = {k:v for k,v in parameters.items()
                    if type(v) is list
                    if k == 'sensorZenith' or k == 'sensorAzimuth'}

    angleDict['sensorZenith'] = [z for z in angleDict['sensorZenith']
                if np.around(np.cos(np.radians(z)), decimals=5) != 0
                and np.around(np.sin(np.radians(z)), decimals=5) != 0
                if z <= 90.0] + [180.0]

    angleCombo = list(dict(zip(angleDict,x)) for x in itertools.product(*angleDict.values()))

    angleCombo = [c for c in angleCombo if c['sensorZenith'] != 180 or c['sensorAzimuth'] == 0]
    ignore = parameters['solarIgnore']
    angleCombo = [c for c in angleCombo
            if not solZenith-ignore <= c['sensorZenith'] <= solZenith+ignore
            and not solAzimuth-ignore <= c['sensorAzimuth'] <= solAzimuth+ignore]

    angleCombo += [{'sensorZenith': solZenith, 'sensorAzimuth':solAzimuth}]
    listCombo = [list(dict(c,**n) for n in angleCombo) for c in listCombo]
    listCombo = [list(dict(parameters,**c) for c in u) for u in listCombo]
    listTargets = [list(dict(d, **{'key':k}) for k, d in enumerate(u)) for u in listCombo]

    for t in listTargets:
        for d in t:
            if d['sensorZenith'] == 180.0 and d['sensorAzimuth'] == 0.0:
                d['targetAltitude'] = d['groundAltitude']
                d['key'] = 'target'
            elif d['sensorZenith'] == solZenith and d['sensorAzimuth'] == solAzimuth:
                d['targetAltitude'] = 100.0
                d['key'] = 'solar'
            else:
                d['targetAltitude'] = 100.0

    return listTargets

if __name__ == "__main__":
    import os
    from find_solar_angles import find_solar_angles

    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    params = {'filename':currentDirectory+'/tape5',
        'modelAtmosphere':[2], 'pathType':2,
        'surfaceAlbedo':None, 'surfaceTemperature':303.15,
        'albedoFilename':currentDirectory+'/spec_alb.dat',
        'targetLabel':["healthy grass",
        "asphalt", "concrete", "blue felt", "green felt", "red felt"],
        'backgroundLabel':["constant, 0%", "constant, 18%", "constant, 100%"],
        'visibility':[5.0, 15.0, 23.0],
        'groundAltitude':0.168, 'sensorAltitude':[0.1686, 0.2137, 0.2372, 0.2600, 0.2823],
        'targetAltitude':0.168, 'sensorZenith':None, 'sensorAzimuth':None,
        'dZenith': 5, 'dAzimuth':10,
        'dayNumber':[172, 312],
        'extraterrestrialSource':0, 'latitude':43.041,
        'longitude':77.698, 'timeUTC':[15.0, 18.0],
        'startingWavelength':0.30, 'endingWavelength':1.2,
        'wavelengthIncrement':0.01, 'fwhm':0.001}

    params['targetLabel'] = "healthy grass"
    params['backgroundLabel'] = "healthy grass"
    #params['dZenith'] = 45
    #params['dAzimuth'] = 180
    params['timeUTC'] = 16.0
    params['visibility'] = 15.0
    params['dayNumber'] = 312
    params['sensorAltitude'] = .2823

    uniqueDict = find_unique_itterations(params)
    solarAngles = find_solar_angles(params)
    itterate = create_unique_itterations(params, uniqueDict, solarAngles)
    #print(itterate[0][4])
