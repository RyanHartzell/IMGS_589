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

    #m,s = divmod(endTime, 60)
    #print("It took {0}m {1}s to run modtran4".format(m, int(s)))

    tape7 = read_tape7(outputPath +'/tape7.scn')

    if any(v.size for v in tape7.values()) == 0:
        #print(currentParams)
        print("Zenith-{0}, Azimuth-{1}".format(currentParams['sensorZenith'], currentParams['sensorAzimuth']))
        msg = "Tape 7 has no information, check your inputs for tape 5"
        raise ValueError(msg)
    shutil.rmtree(outputPath)

    return tape7, endTime

def integrateBandRadiance(radiance, rsrDict, wavelengths, radianceType):
    import copy
    import numpy as np

    bandIntegratedDict = {}
    for b in rsrDict.keys():
        bandEffectiveRadiance = radiance * rsrDict[b]
        bandIntegratedRadiance = np.trapz(bandEffectiveRadiance, wavelengths)
        bandIntegratedRSR = np.trapz(rsrDict[b], wavelengths)
        bandIntegratedDict[radianceType+' '+b] = bandIntegratedRadiance/bandIntegratedRSR
    bandIntegratedDict['radianceType'] = radianceType

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

    writeDict = dict(params, **bandDict)
    writeDict['albedoFilename'] = os.path.basename(writeDict['albedoFilename'])
    writeDict['fileName'] = os.path.basename(writeDict['fileName'])
    writeDict = {k:v for k,v in writeDict.items() if v is not None}
    if writeDict['radianceType'] == 'Target':
        writeDict['targetAltitude'] = writeDict['groundAltitude']

    with open(csvFile, 'a') as f:
        dw = csv.DictWriter(f, writeDict.keys())
        if not exists:
            dw.writeheader()
        dw.writerow(writeDict)

def writeSummary(filename, paramDict, summary, bandIntDictTgt, bandIntDictSolar):
    import csv
    import os
    import numpy as np

    writeDict = {k:v for k,v in paramDict.items() if v is not None}
    writeDict['albedoFilename'] = os.path.basename(writeDict['albedoFilename'])
    writeDict['fileName'] = os.path.basename(writeDict['fileName'])

    with open(filename, 'a') as f:
        w = csv.writer(f)
        w.writerow(list(writeDict.keys())[:-1])
        w.writerow(list(writeDict.values())[:-1])
        w.writerow(list(bandIntDictTgt.keys())[:-1]+list(bandIntDictSolar.keys())[:-1])
        w.writerow(list(bandIntDictTgt.values())[:-1]+list(bandIntDictSolar.values())[:-1])
        #w.writerow(list(bandIntDictSolar.keys()))
        #w.writerow(list(bandIntDictSolar.values()))
        w.writerow(list(summary.keys()))
        for r in range(np.asarray(list(summary.values())).shape[1]):
            w.writerow(np.asarray(list(summary.values()))[:,r])


def createItterations(params):
    import itertools

    listDict = {k:v for k,v in params.items()
                    if type(v) is list
                    if k != 'sensorZenith' if k != 'sensorAzimuth'}
    uniqueDict = {k:v for k,v in listDict.items() if len(v) > 1}
    listCombo = list(dict(zip(listDict, x))
                        for x in itertools.product(*listDict.values()))

    for d in range(len(listCombo)):
        listCombo[d]['sensorZenith'] = params['sensorZenith']
        listCombo[d]['sensorAzimuth'] = params['sensorAzimuth']
        dDict = {k:v for k,v in listCombo[d].items() if type(v) is list}
        dCombo = list(dict(zip(dDict, x))
                            for x in itertools.product(*dDict.values()))
        listCombo[d] = [dict(listCombo[d], **x) for x in dCombo]

    listTargets = [[dict(params, **d) for d in l] for l in listCombo]
    listTargets = [[dict(d, **{'key':key}) for key, d in enumerate(l)]
                                                    for l in listTargets]

    for t in listTargets:
        for d in t:
            if d['sensorZenith'] != 180.0:
                d['targetAltitude'] = 100.0
            elif d['sensorZenith'] == 180.0 and d['sensorAzimuth'] == 0.0:
                d['targetAltitude'] = d['groundAltitude']
            elif d['sensorZenith'] == 180.0 and (d['targetAltitude']
                                                    != d['sensorAltitude']):
                d = None

    itterate = list(filter(None.__ne__, listTargets))

    return itterate, uniqueDict

def plotResults(params, results, blocking=True):
    import matplotlib
    matplotlib.use('Agg')
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
    "Wavelength Increment [microns] - {0}, ".format(
                                        params['wavelengthIncrement']) + \
    "Full Width Half Max [microns] - {0}, ".format(params['fwhm'])

    plt.title(title)

    plt.plot(wavelengths, resultsList[0], color='red',
                                    label="Target Solar Scattering")
    plt.plot(wavelengths, resultsList[1], color='cyan',
                                    label="Ground Reflectance")
    plt.plot(wavelengths, resultsList[2], color='green',
                                    label="Direct Reflectance")
    plt.plot(wavelengths, resultsList[3], color='purple',
                                    label="Total Radiance")
    plt.plot(wavelengths, resultsList[4], color='yellow',
                                    label="Estimated Downwell Solar Scattering")
    plt.plot(wavelengths, resultsList[5], color='blue',
                                    label="Integrated Solar Scattering")
    plt.xlabel("Wavelengths {0}-{1}[microns]".format(
        params['startingWavelength'], params['endingWavelength']))
    plt.ylabel("Radiance Watts/cm^2 str micron")
    plt.xlim(params['startingWavelength'], params['endingWavelength'])
    plt.ylim(0, np.max(np.asarray(resultsList)))
    plt.legend()
    plt.draw()

    figureTitle = "/Modtran4_target-{0}_dAzimuth-{1}_dZenith-{2}.eps".format(
        params['targetLabel'].replace(" ", "_"), params['dAzimuth'],
        params['dZenith'])
    plt.savefig(os.path.dirname(params['albedoFilename']) + figureTitle)

    plt.close()
    if blocking is True:
        plt.show()

def processFunction(params):
    import os
    import getpass
    import numpy as np
    from update_tape5 import update_tape5
    from read_tape7 import read_tape7

    keyDirectory = os.path.dirname(params['albedoFilename'])+ \
                                    '/modtran_{0}'.format(params['key'])
    if not os.path.exists(keyDirectory):
        os.mkdir(keyDirectory)

    params['fileName'] = keyDirectory + '/tape5'
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
    #                   params['sensorZenith'],params['sensorAzimuth']))

    tape7, modtranTime = executeModtran(params)
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

        rsrPath = os.path.dirname(params['albedoFilename']) + '/FullSpectralResponse.csv'
        rsrDict = generateRSR(rsrPath, wavelengths)
        bandIntDict = integrateBandRadiance(totalRadiance, rsrDict,
                                                    wavelengths, 'Target')
        baseDir = os.path.dirname(params['albedoFilename'])
        userName = getpass.getuser()
        #writeToCSV(baseDir + '/{0}_target.csv'.format(userName),
        #                        params, bandIntDict)

    elif params['sensorZenith'] != 180:
        sumSolScat = tape7['sol scat']

        sumSolScat = sumSolScat * np.cos(np.radians(params['sensorZenith'])) *\
                            np.sin(np.radians(params['sensorZenith'])) * \
                np.radians(params['dZenith']) * np.radians(params['dAzimuth'])

    resultDict = {'wavelengths':wavelengths,'sumSolScat':sumSolScat,
                'tgtSolScat':tgtSolScat,'groundReflect':groundReflect,
                'directReflect':directReflect,'estDownwell':estDownwell,
                'totalRadiance':totalRadiance, 'bandIntDictTgt':bandIntDict,
                'modtranTime': modtranTime, 'params': params}

    return resultDict

def modtran(paramList, plotting=True):
    from runModtran4 import processFunction
    from runModtran4 import integrateBandRadiance
    from runModtran4 import writeToCSV
    from runModtran4 import generateRSR
    from runModtran4 import plotResults
    import getpass
    import os
    import numpy as np
    import multiprocessing

    sumSolScat = 0
    useFullCPU = multiprocessing.cpu_count()-2
    modtranTime = []
    modNumber = 5
    targetList = ['tgtSolScat','groundReflect','directReflect','estDownwell',
                    'totalRadiance','bandIntDictTgt']
    if len(paramList) > 46:
        modNumber = 46
    if len(paramList) < useFullCPU: useFullCPU=len(paramList)
    with multiprocessing.Pool(processes=useFullCPU) as pool:
        for resultDict in pool.imap_unordered(processFunction, [param for param in paramList]):
            resultDict = {k:v for k,v in resultDict.items() if v is not None}
            wavelengths = resultDict['wavelengths']
            modtranTime.append(resultDict['modtranTime'])
            if len(modtranTime)%modNumber == 0:
                averageTime = sum(modtranTime)/len(modtranTime)
                m, s = divmod(averageTime, 60)
                print("The current average modtran run time is {0}m {1}s".format(int(m), int(s)))

            if 'sumSolScat' in resultDict.keys():
                sumSolScat += resultDict['sumSolScat']
            elif len([k for t in targetList for k in resultDict.keys() if t in k]) == len(targetList):
                tgtSolScat = resultDict['tgtSolScat']
                groundReflect = resultDict['groundReflect']
                directReflect = resultDict['directReflect']
                estDownwell = resultDict['estDownwell']
                totalRadiance = resultDict['totalRadiance']
                bandIntDictTgt = resultDict['bandIntDictTgt']

    pool.join()
    pool.close()

    userName = getpass.getuser()
    rsrPath = os.path.dirname(paramList[0]['albedoFilename']) +\
                                '/FullSpectralResponse.csv'
    rsrDict = generateRSR(rsrPath, wavelengths)
    bandIntDictSolar = integrateBandRadiance(sumSolScat, rsrDict,
                                        wavelengths, 'Downwelling')

    baseDir = os.path.dirname(paramList[0]['albedoFilename'])
    #writeToCSV(baseDir + '/{0}_downwelling.csv'.format(userName),
    #                                paramList[0], bandIntDictSolar)

    summary = {'wavelengths':wavelengths, 'tgtSolScat':tgtSolScat,
    'groundReflect':groundReflect, 'directReflect':directReflect,
    'estDownwell':estDownwell, 'totalRadiance':totalRadiance,
    'sumSolScat':sumSolScat}
    summary.update(rsrDict)

    writeSummary(baseDir + '/summary.csv', paramList[0], summary, bandIntDictTgt, bandIntDictSolar)

    if plotting:
        results = {'wavelengths':wavelengths, 'targetSolScat': tgtSolScat,
        'groundReflect': groundReflect, 'directReflect':directReflect,
        'totalRadiance':totalRadiance, 'estimatedDownwell':estDownwell,
        'integratedDownwellRadiance': sumSolScat}

        plotResults(paramList[0],results, False)

if __name__ == "__main__":
    import os
    import time
    import multiprocessing
    import numpy as np
    from runModtran4 import modtran

    plotting = False

    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    params = {'fileName':'tape5', 'modelAtmosphere':[2,3,6], 'pathType':2,
        'surfaceAlbedo':None, 'surfaceTemperature':303.15,
        'albedoFilename':currentDirectory+'/spec_alb.dat',
        'targetLabel':["healthy grass",
        "asphalt", "concrete", "blue felt", "green felt", "red felt"],
        'backgroundLabel':["constant, 18%"], 'visibility':[0.0],
        'groundAltitude':0.168, 'sensorAltitude':[0.2137, 0.2823],
        'targetAltitude':0.168, 'sensorZenith':180.0, 'sensorAzimuth':0.0,
        'dZenith': 2.5, 'dAzimuth':5,
        'dayNumber':[312],
        'extraterrestrialSource':0, 'latitude':43.041,
        'longitude':77.698, 'timeUTC':[15.0, 17.0, 19.0],
        'startingWavelength':0.30, 'endingWavelength':1.2,
        'wavelengthIncrement':0.001, 'fwhm':0.001}

    params['targetLabel'] = "green felt"
    #params['dZenith'] = 45
    #params['dAzimuth'] = 180
    #print(np.linspace(1,365,4, False, True))
    params['timeUTC'] = 15.0
    params['sensorAltitude'] = 0.2823
    params['modelAtmosphere'] = 2
    # params['sensorZenith'] = list(np.linspace(0.0, 90.0,
    #                                     90.0/(params['dZenith']+1))) + [180.0]
    # params['sensorAzimuth'] = list(np.linspace(0.0, 360.0,
    #                                     360.0/params['dAzimuth']+1))
    params['sensorZenith'] = list(np.arange(0.0,90.0+params['dZenith'],
                                            params['dZenith'])) + [180.0]
    params['sensorAzimuth'] = list(np.arange(0.0,360.0+params['dAzimuth'],
                                            params['dAzimuth']))
    #params['sensorZenith'] = [0.0, 180.0]
    #params['sensorAzimuth'] = [0.0]

    itterations, uniqueDict = createItterations(params)

    totalCpu = multiprocessing.cpu_count()
    if totalCpu == 8:
        estTime = 20
    else:
        estTime = 100

    numItter = len(itterations)*len(itterations[0])*estTime
    numCPU = totalCpu-2
    if len(itterations[0]) < totalCpu: numCPU = len(itterations[0])
    numItter = numItter/(numCPU)

    m,s = divmod(numItter, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)


    print("Estimated time to complete {0} itterations ".format(len(itterations)*len(itterations[0])) +
    "is {0}d {1}h {2}m {3}s ".format(int(d), int(h), int(m), int(s)) +
    "using {0}/{1} cores at {2}s per itteration.".format(numCPU, totalCpu, estTime))
    print("Unique itterations: {0}, Angle itterations: {1}".format(
                                    len(itterations), len(itterations[0])))
    print("The unique itterations are:")
    for k,v in uniqueDict.items():
        print("\t{0}: {1}".format(k,v))

    print("The angle itterations are:")
    print("\tZenith Angles: {0}".format(params['sensorZenith']))
    print("\tAzimuth Angles: {0}".format(params['sensorAzimuth']))
    print()

    for i in range(len(itterations)):
        unique = {k:v for k,v in itterations[i][0].items() if k in uniqueDict.keys()}
        print("Current Unique Itteration: ", unique)
        startTime = time.time()
        modtran(itterations[i], plotting)
        itterationTime = time.time()-startTime
        m,s = divmod(itterationTime, 60)
        h,m = divmod(m, 60)
        print("\nIt took {0}h {1}m {2}s ".format(int(h),int(m),int(s)) +
            "to complete all angles using a delta zenith angle " +
            "of {0} ".format(params['dZenith']) +
            "and a delta azimuth angle of {0}".format(params['dAzimuth']))

        uM,uS = divmod(itterationTime*(len(itterations)-i-1), 60)
        uH, uM = divmod(uM, 60)
        uD, uH = divmod(uH, 24)
        print("The updated estimated time to complete is {0}d {1}h {2}m {3}s.".format(
            int(uD), int(uH), int(uM), int(uS)))
        print()

    print("You've completed all of the itterations, congratulations")
