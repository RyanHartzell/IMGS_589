def integrated_bands(srcWl, srcVal, rsrWl, rsrVal, tgtWl):
    import numpy as np
    from interp1 import interp1
    import collections

    normalized = [k for k in rsrVal.keys() if "Norm" in k]
    bandIntegratedDict = collections.OrderedDict()
    for b in normalized:
        interpRSR = interp1(rsrWl, rsrVal[b], tgtWl)
        interpRSR[np.isnan(interpRSR)] = 0
        interpArray = interp1(srcWl, srcVal, tgtWl)
        interpArray[np.isnan(interpArray)] = 0
        bandEffective = interpArray * interpRSR
        bandIntegrated = np.trapz(bandEffective, tgtWl)
        bandIntegratedRSR = np.trapz(interpRSR, tgtWl)
        key = b.replace("Norm", "").strip()
        bandIntegratedDict[key] = np.divide(bandIntegrated, bandIntegratedRSR)

    return bandIntegratedDict

def generate_rsr(rsrPath):
    import csv
    import collections
    import numpy as np

    with open(rsrPath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        rsrDictionary = collections.OrderedDict.fromkeys(fieldnames, [])
        for row in reader:
            for column, value in row.items():
                if float(value) < 0:
                    value = 0
                rsrDictionary[column] = rsrDictionary[column] + [float(value)]
        rsrDictionary = collections.OrderedDict({k:np.asarray(v) for k,v in rsrDictionary.items()})

    rsrDictionary['Wavelength'] = rsrDictionary['Wavelength']*0.001 #Units of micrometers

    return rsrDictionary

if __name__ == "__main__":
    import os
    from find_solar_angles import *
    from groundTruth import *
    from create_itterations import *
    from newModtran import *
    import time

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    path = currentDirectory + '/camera_rsr.csv'
    rsrDictionary = generate_rsr(path)
    rsrWl = rsrDictionary['Wavelength']

    params = {'filename':currentDirectory+'/tape5',
        'modelAtmosphere':2, 'pathType':2,
        'surfaceAlbedo':None, 'surfaceTemperature':303.15,
        'albedoFilename':currentDirectory+'/spec_alb.dat',
        'targetLabel':"healthy grass",
        'backgroundLabel':"healthy grass",
        'visibility':15.0,
        'groundAltitude':0.168, 'sensorAltitude':0.1686,
        'targetAltitude':0.168, 'sensorZenith':None, 'sensorAzimuth':None,
        'dZenith': 45, 'dAzimuth':180,
        'dayNumber': 312,
        'extraterrestrialSource':0, 'latitude':43.041,
        'longitude':77.698, 'timeUTC':16.0,
        'startingWavelength':0.30, 'endingWavelength':1.2,
        'wavelengthIncrement':0.001, 'fwhm':0.001}

    uniqueDict = find_unique_itterations(params)
    solarAngles = find_solar_angles(params)
    itterate = create_unique_itterations(params, uniqueDict, solarAngles)
    for unique in itterate:
       radiances = modtran(unique)
       modtranWl = radiances['wavelengths']
       reflectance = radiances['reflectance']
       bandIntegrated = integrated_bands(modtranWl, reflectance, rsrWl, rsrDictionary, modtranWl)
       specArray = read_spec_alb(params['albedoFilename'], params['targetLabel'])
       bandIntegratedSVC = integrated_bands(specArray[:,0],specArray[:,1], rsrWl, rsrDictionary, modtranWl)
       print(bandIntegrated)
       print(bandIntegratedSVC)
