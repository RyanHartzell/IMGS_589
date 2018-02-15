def executeModtran(currentParams):
    import os
    import time
    import shutil
    from read_tape7 import read_tape7

    outputPath = os.path.dirname(currentParams['fileName']) + os.path.sep
    command = '/dirs/bin/modtran4 > /dev/null 2>&1'
    os.chdir(outputPath)

    startTime = time.time()
    os.system(command)
    endTime = time.time()-startTime

    splitted = currentParams['fileName'].split('/')
    os.chdir('/'.join(splitted[:-2])+ os.path.sep)

    m,s = divmod(endTime, 60)
    print("It took {0}m {1}s to run modtran4".format(m, int(s)))

    tape7 = read_tape7(outputPath +'/tape7.scn')

    if any(v.size for v in tape7.values()) == 0:
        print(currentParams)
        msg = "Tape 7 has no information, check your inputs for tape 5"
        raise ValueError(msg)
    shutil.rmtree(outputPath)

    return tape7

def integrateBandRadiance(radiance, rsrDict, wavelengths):
    import copy
    import numpy as np

    bandIntegratedDict = copy.deepcopy(rsrDict)
    for b in rsrDict.keys():
        bandEffectiveRadiance = radiance * rsrDict[b]
        bandIntegratedRadiance = np.trapz(bandEffectiveRadiance, wavelengths)
        bandIntegratedRSR = np.trapz(rsrDict[b], wavelengths)
        bandIntegratedDict[b] = bandIntegratedRadiance/bandIntegratedRSR

    return bandIntegratedDict

def generateRSR(rsrPath, wavelengths, interpOrder=1, extrap=False):
    import csv
    import numpy as np
    from interp1 import interp1

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
        rsr = interp1(rsrWavelengths, rsr, wavelengths, interpOrder, extrap)
        rsr[np.isnan(rsr)] = 0
        rsrDict[band] = rsr

    return rsrDict

def writeToCSV(csvFile, params, bandDict):
    import os
    import csv

    bandList = [v for v in bandDict.values()]

    exists = os.path.isfile(csvFile)

    with open(csvFile, 'a') as f:
        writer = csv.writer(f)

        if params['targetAltitude'] == 100:
            headders=['Model Atmosphere', 'Visibility', 'Day', 'Time',
                    'Ground Altitude', 'Sensor Altitude', 'Target Altitude', 'Albedo',
                    'Band Integrated Downwelling Blue', 'Band Integrated Downwelling Green',
                    'Band Integrated Downwelling Red', 'Band Integrated Downwelling RedEdge',
                     'Band Integrated Downwelling Infrared']

            if not exists:
                writer.writerow(headders)

            row = [params['modelAtmosphere'], params['visibility'],
                    params['dayNumber'], params['timeUTC'], params['groundAltitude'],
                    params['sensorAltitude'], params['targetAltitude']] + bandList
            print(row)
            writer.writerow(row)

        if params['targetAltitude'] == params['groundAltitude']:
            headders = ['Model Atmosphere', 'Visibility', 'Day', 'Time',
                            'Ground Altitude','Sensor Altitude',
                                'Target Altitude', 'Zenith', 'Azimuth',
                                'Background', 'Target', 'Band Integrated Blue',
                                'Band Integrated Green', 'Band Integrated Red',
                                'Band Integrated RedEdge', 'Band Integrated Infrared']
            if not exists:
                writer.writerow(headders)
            row = [params['modelAtmosphere'], params['visibility'],
                    params['dayNumber'], params['timeUTC'], params['groundAltitude'],
                    params['sensorAltitude'], params['targetAltitude'],
                    params['sensorZenith'], params['sensorAzimuth'],
                    params['backgroundLabel'], params['targetLabel']] + bandList
            print(row)
            writer.writerow(row)

def createItterations(params):
    import itertools

    listDict = {k:v for k,v in params.items() if type(v) is list if k != 'sensorZenith' if k != 'sensorAzimuth'}
    listCombo = list(dict(zip(listDict, x)) for x in itertools.product(*listDict.values()))

    for d in range(len(listCombo)):
        listCombo[d]['sensorZenith'] = params['sensorZenith']
        listCombo[d]['sensorAzimuth'] = params['sensorAzimuth']
        dDict = {k:v for k,v in listCombo[d].items() if type(v) is list}
        dCombo = list(dict(zip(dDict, x)) for x in itertools.product(*dDict.values()))
        listCombo[d] = [dict(listCombo[d], **x) for x in dCombo]

    listTargets = [[dict(params, **d) for d in l] for l in listCombo]
    listTargets = [[dict(d, **{'key':key}) for key, d in enumerate(l)] for l in listTargets]

    for t in listTargets:
        for d in t:
            if d['sensorZenith'] != 180.0:
                d['targetAltitude'] = 100.0
            elif d['sensorZenith'] == 180.0 and d['sensorAzimuth'] == 0.0:
                d['targetAltitude'] = d['groundAltitude']
            elif d['sensorZenith'] == 180.0 and d['targetAltitude'] != d['sensorAltitude']:
                d = None

    itterate = list(filter(None.__ne__, listTargets))

    return itterate

def plotResults(params, results, blocking=True):
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    wavelengths = results['wavelengths']
    targetSolScat = results['targetSolScat']
    groundReflect = results['groundReflect']
    directReflect = results['directReflect']
    totalRadiance = results['totalRadiance']
    estimatedDownwell = results['estimatedDownwell']
    integratedDownwellRadiance = results['integratedDownwellRadiance']
    resultsList = [targetSolScat,groundReflect,directReflect,
                    totalRadiance,estimatedDownwell,integratedDownwellRadiance]

    for r in range(len(resultsList)):
        if type(resultsList[r]) is int or len(resultsList[r]) == 1:
            resultsList[r] = np.zeros_like(wavelengths)

    title = "Atmosphere Model - {0}, ".format(params['modelAtmosphere']) + \
    "Surface Temperature - {0}, ".format(params['surfaceTemperature']) + \
    "Target Label - {0}, \n".format(params['targetLabel']) + \
    "Background Label - {0},".format(params['backgroundLabel']) + \
    "Visibility [km] - {0}, ".format(params['visibility']) + \
    "Ground Altitude AGL [km] - {0}, \n".format(params['groundAltitude']) + \
    "Sensor Altitude AGL [km] - {0}, ".format(params['sensorAltitude']) + \
    "Target Altitude AGL [km] - {0},".format(params['targetAltitude']) + \
    "Day Number - {0}, \n".format(params['dayNumber']) + \
    "Latitude - {0}, ".format(params['latitude']) + \
    "Longitude - {0}, ".format(params['longitude']) + \
    "Time GMT - {0}, \n".format(params['timeUTC']) + \
    "Wavelength Increment [microns] - {0}, ".format(params['wavelengthIncrement']) + \
    "Full Width Half Max [microns] - {0}, ".format(params['fwhm'])

    plt.title(title)

    plt.plot(wavelengths, resultsList[0], color='red', label="Target Solar Scattering")
    plt.plot(wavelengths, resultsList[1], color='cyan', label="Ground Reflectance")
    plt.plot(wavelengths, resultsList[2], color='green', label="Direct Reflectance")
    plt.plot(wavelengths, resultsList[3], color='purple', label="Total Radiance")
    plt.plot(wavelengths, resultsList[4], color='yellow', label="Estimated Downwell Solar Scattering")
    plt.plot(wavelengths, resultsList[5], color='blue', label="Integrated Solar Scattering")
    plt.xlabel("Wavelengths {0}-{1}[microns]".format(params['startingWavelength'],
                                        params['endingWavelength']))
    plt.ylabel("Radiance Watts/cm^2 str micron")
    plt.xlim(params['startingWavelength'], params['endingWavelength'])
    plt.ylim(0, np.max(np.asarray(resultsList)))
    plt.legend()
    plt.draw()

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    figureTitle = "/Modtran4_target-{0}_dAzimuth-{1}_dZenith-{2}.eps".format(
                    params['targetLabel'], params['dAzimuth'], params['dZenith'])
    plt.savefig(currentDirectory + figureTitle)

    if blocking is True:
        plt.show()

def processFunction(params,q=None):
    import os
    import numpy as np
    from update_tape5 import update_tape5
    from read_tape7 import read_tape7

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    keyDirectory = currentDirectory+'/modtran_{0}'.format(params['key'])
    if not os.path.exists(keyDirectory):
        os.mkdir(keyDirectory)

    params['fileName'] = keyDirectory + '/tape5'
    params['albedoFilename'] = currentDirectory + '/spec_alb.dat'
    update_tape5(params['fileName'], params['modelAtmosphere'],
            params['pathType'], params['surfaceAlbedo'],
            params['surfaceTemperature'], params['albedoFilename'],
            params['targetLabel'], params['backgroundLabel'],
            params['visibility'], params['groundAltitude'],
            params['sensorAltitude'], params['targetAltitude'],
            params['sensorZenith'], params['sensorAzimuth'],
            params['dayNumber'], params['extraterrestrialSource'],
            params['latitude'], params['longitude'],
            params['timeUTC'], params['startingWavelength'],
            params['endingWavelength'], params['wavelengthIncrement'],
            params['fwhm'])

    #print("Running Modtran4 with Zenith {0}, Azimuth {1}".format(
    #                        params['sensorZenith'],params['sensorAzimuth']))

    tape7 = executeModtran(params)
    wavelengths = tape7['wavlen mcrn']

    sumSolScat = None
    tgtSolScat = None
    groundReflect = None
    directReflect = None
    estDownwell = None
    totalRadiance = None
    bandIntDict = None

    if params['sensorZenith'] == 180 and params['sensorAzimuth'] == 0:
        tgtSolScat = tape7['sol scat']
        groundReflect = tape7['grnd rflt']
        directReflect = tape7['drct rflt']
        estDownwell = groundReflect - directReflect
        totalRadiance = tape7['total rad']

        rsrPath = currentDirectory + '/FullSpectralResponse.csv'
        rsrDict = generateRSR(rsrPath, wavelengths)
        bandIntDict = integrateBandRadiance(totalRadiance, rsrDict, wavelengths)

    elif params['sensorZenith'] != 180:
        sumSolScat = tape7['sol scat']

        sumSolScat = sumSolScat * np.cos(np.radians(params['sensorZenith'])) * \
                            np.sin(np.radians(params['sensorZenith'])) * \
                np.radians(params['dZenith']) * np.radians(params['dAzimuth'])

    resultDict = {'wavelengths':wavelengths,'sumSolScat':sumSolScat,
                'tgtSolScat':tgtSolScat,'groundReflect':groundReflect,
                'directReflect':directReflect,'estDownwell':estDownwell,
                'totalRadiance':totalRadiance, 'bandIntDictTgt':bandIntDict}

    return resultDict

def modtran(paramList, plotting=True):
    from runModtran4 import processFunction
    from runModtran4 import integrateBandRadiance
    from runModtran4 import writeToCSV
    from runModtran4 import generateRSR
    from runModtran4 import plotResults
    import getpass
    import os
    import multiprocessing


    with multiprocessing.Pool(processes=multiprocessing.cpu_count()-2) as pool:
        resultArray = pool.map(processFunction, [param for param in paramList])
    pool.join()
    pool.close()

    resultList = [dict((k,v) for k,v in d.items() if v is not None) for d in resultArray]

    wavelengths = resultList[0]['wavelengths']
    sumSolScat = 0
    for r in range(len(resultList)):
        if len(resultList[r]) == 7:
            tgtSolScat = resultList[r]['tgtSolScat']
            groundReflect = resultList[r]['groundReflect']
            directReflect = resultList[r]['directReflect']
            estDownwell = resultList[r]['estDownwell']
            totalRadiance = resultList[r]['totalRadiance']
            bandIntDictTgt = resultList[r]['bandIntDictTgt']
        else:
            dictionary = resultList[r]
            for key in dictionary.keys():
                if key == 'sumSolScat':
                    sumSolScat += dictionary[key]

    userName = getpass.getuser()
    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    rsrPath = currentDirectory + '/FullSpectralResponse.csv'
    rsrDict = generateRSR(rsrPath, wavelengths)
    bandIntDictSolar = integrateBandRadiance(sumSolScat, rsrDict, wavelengths)
    writeToCSV(currentDirectory+'/{0}_downwelling.csv'.format(userName), paramList[0], bandIntDictSolar)
    writeToCSV(currentDirectory+'/{0}_target.csv'.format(userName), paramList[0], bandIntDictTgt)

    if plotting:
        results = {'wavelengths':wavelengths, 'targetSolScat': tgtSolScat,
        'groundReflect': groundReflect, 'directReflect':directReflect,
        'totalRadiance':totalRadiance, 'estimatedDownwell':estDownwell,
        'integratedDownwellRadiance': sumSolScat}

        plotResults(paramList[0],results)

if __name__ == "__main__":
    import os
    import time
    import multiprocessing
    import numpy as np
    from runModtran4 import modtran

    plotting = False

    params = {'fileName':'tape5', 'modelAtmosphere':[1,2,3], 'pathType':2,
        'surfaceAlbedo':None, 'surfaceTemperature':303.15,
        'albedoFilename':'spec_alb.dat', 'targetLabel':["healthy grass", "asphalt",
        "concrete", "blue felt", "green felt", "red felt"],
        'backgroundLabel':["constant, 18%"], 'visibility':[0.0],
        'groundAltitude':0.168, 'sensorAltitude':[0.2137, 0.2823],
        'targetAltitude':0.168, 'sensorZenith':180.0, 'sensorAzimuth':0.0,
        'dZenith': 2.5, 'dAzimuth':5,
        'dayNumber':[312], 'extraterrestrialSource':0, 'latitude':43.041,
        'longitude':77.698, 'timeUTC':[15.0,17.1,19.0], 'startingWavelength':0.30,
        'endingWavelength':1.2, 'wavelengthIncrement':0.001, 'fwhm':0.001}

    params['sensorZenith'] = list(np.linspace(0.0, 90.0, 90/params['dZenith']+1)) + [180.0]
    params['sensorAzimuth'] = list(np.linspace(0.0, 360.0, 360/params['dAzimuth']+1))

    itterations = createItterations(params)

    numCPU = multiprocessing.cpu_count()
    if numCPU == 8:
        numItter = len(itterations)*len(itterations[0])*20
    else:
        numItter = len(itterations)*len(itterations[0])*100

    numItter = numItter/(numCPU-2)

    m,s = divmod(numItter, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    print("Estimated time to complete {0} itterations is {1}d {2}h {3}m {4}s using {5} cores".format(
        len(itterations)*len(itterations[0]),int(d), int(h), int(m), int(s), numCPU-2))
    print("The number of unique itterations is {0}".format(len(itterations)))

    for itteration in itterations:
        startTime = time.time()
        modtran(itteration, plotting)
        m,s = divmod(time.time()-startTime, 60)
        h,m = divmod(m, 60)
        print("It took {0}h {1}m {2}s to run with a delta z {3} and a delta a {4}".format(
                                    h, m, s, params['dZenith'], params['dAzimuth']))
