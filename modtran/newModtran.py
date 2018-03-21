import os
import time
import numpy as np
import multiprocessing

def executeModtran(currentParams):
    from read_tape7 import read_tape7

    outputPath = os.path.dirname(currentParams['filename']) + os.path.sep
    command = '/dirs/bin/modtran4 > /dev/null 2>&1'
    os.chdir(outputPath)

    startTime = time.time()
    os.system(command)
    endTime = time.time()-startTime

    splitted = currentParams['filename'].split('/')
    os.chdir('/'.join(splitted[:-2])+ os.path.sep)
    tape7 = read_tape7(outputPath +'/tape7.scn')

    if any(v.size for v in tape7.values()) == 0:
        print("There was an error")

    return tape7, endTime

def processFunction(params):
    from update_tape5 import update_tape5

    keyDirectory = os.path.dirname(params['filename'])+ \
                                    '/modtran_{0}'.format(params['key'])
    if not os.path.exists(keyDirectory):
        os.mkdir(keyDirectory)

    params['filename'] = keyDirectory + '/tape5'
    update_tape5(dictionary = params)

    tape7, modtranTime = executeModtran(params)

    wavelengths = tape7['wavlen mcrn']
    skyIrradiance = None
    solarIrradiance = None
    targetRadiance = None
    tAlt = params['targetAltitude']
    zen = params['sensorZenith']
    azi = params['sensorAzimuth']

    if params['key'] == 'target':
        targetRadiance = tape7['total rad']
        #print("{0}: Target Altitude {1}, Zenith {2}, Azimuth: {3}".format(params['key'],tAlt, zen, azi))

    elif params['key'] == 'solar':
        solarIrradiance = tape7['total rad']
        solarIrradiance *= np.cos(np.radians(params['sensorZenith'])) *\
                            np.sin(np.radians(params['sensorZenith'])) * \
                            np.radians(.5) * np.radians(.5)
        # solarIrradiance *= np.cos(np.radians(params['sensorZenith'])) *\
        #                     np.sin(np.radians(params['sensorZenith'])) * \
        #                     .5 * .5
        print("{0}: Target Altitude {1}, Zenith {2}, Azimuth: {3}".format(params['key'],tAlt, zen, azi))


    else:
        #skyIrradiance = tape7['sol scat']
        skyIrradiance = tape7['total rad']
        skyIrradiance *= np.cos(np.radians(params['sensorZenith'])) *\
                            np.sin(np.radians(params['sensorZenith'])) * \
                        np.radians(params['dZenith']) * np.radians(params['dAzimuth'])


    resultDict = {'wavelengths':wavelengths,'skyIrradiance':skyIrradiance,
                'solarIrradiance':solarIrradiance,'targetRadiance':targetRadiance,
                'modtranTime': modtranTime}

    return resultDict

def modtran(paramList):
    skyIrradiance = []
    modtranTime = []
    with multiprocessing.Pool() as pool:
        for resultDict in pool.imap_unordered(processFunction,
                            [param for param in paramList]):

            resultDict = {k:v for k,v in resultDict.items() if v is not None}
            wavelengths = resultDict['wavelengths']
            modtranTime.append(resultDict['modtranTime'])

            if 'skyIrradiance' in resultDict.keys():
                skyIrradiance.append(resultDict['skyIrradiance'])
            elif 'solarIrradiance' in resultDict.keys():
                solarIrradiance = resultDict['solarIrradiance']
            elif 'targetRadiance' in resultDict.keys():
                targetRadiance = resultDict['targetRadiance']

        skyIrradiance = np.array(sum(skyIrradiance))
        downwellingIrradiance = skyIrradiance + solarIrradiance
        downwellingRadiance = downwellingIrradiance / np.pi
        reflectance = targetRadiance/downwellingRadiance
        averageModtran = sum(modtranTime)/len(modtranTime)

        radiances = {'skyIrradiance':skyIrradiance, 'solarIrradiance':solarIrradiance,
            'downwellingIrradiance':downwellingIrradiance, 'downwellingRadiance': downwellingRadiance,
            'targetRadiance': targetRadiance, 'reflectance': reflectance,
            'wavelengths':wavelengths, 'averageModtran': averageModtran}

    pool.join()
    pool.close()

    return radiances


if __name__ == "__main__":
    from create_itterations import *
    from find_solar_angles import find_solar_angles
    from matplotlib import pyplot as plt
    from runModtran4 import getAverageSVC
    from interp1 import interp1

    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    params = {'filename':currentDirectory+'/tape5',
        'modelAtmosphere':2, 'pathType':2,
        'surfaceAlbedo':None, 'surfaceTemperature':303.15,
        'albedoFilename':currentDirectory+'/spec_alb.dat',
        'targetLabel':"healthy grass",
        'backgroundLabel':"healthy grass",
        'visibility':15.0,
        'groundAltitude':0.168, 'sensorAltitude':0.1686,
        'targetAltitude':0.168, 'sensorZenith':None, 'sensorAzimuth':None,
        'dZenith': 5, 'dAzimuth':10,
        'dayNumber': 312,
        'extraterrestrialSource':0, 'latitude':43.041,
        'longitude':77.698, 'timeUTC':16.0,
        'startingWavelength':0.33, 'endingWavelength':1.2,
        'wavelengthIncrement':0.001, 'fwhm':0.001}

    uniqueDict = find_unique_itterations(params)
    solarAngles = find_solar_angles(params)
    itterate = create_unique_itterations(params, uniqueDict, solarAngles)
    for unique in itterate:
        startTime = time.time()
        radiances = modtran(unique)
        totalTime = time.time()-startTime
        print("This took {0}s to complete 1 run".format(totalTime))
        print("Average Modtran Run Time: {0}s".format(radiances['averageModtran']))

        plt.figure()
        plt.title("Downwelling Irradiance")
        plt.plot(radiances['wavelengths'], radiances['skyIrradiance'], label="skyIrradiance")
        plt.plot(radiances['wavelengths'], radiances['solarIrradiance'], label="solarIrradiance")
        plt.plot(radiances['wavelengths'], radiances['downwellingIrradiance'], label="downwellingIrradiance")
        plt.legend()

        plt.figure()
        plt.title("Downwelling Radiance")
        plt.plot(radiances['wavelengths'], radiances['downwellingRadiance'], label="downwellingRadiance")
        plt.plot(radiances['wavelengths'], radiances['targetRadiance'], label="targetRadiance")
        plt.legend()

        svcArray = getAverageSVC(params['albedoFilename'], params['targetLabel'])
        truth = interp1(svcArray[:,0], svcArray[:,1], radiances['wavelengths'])
        plt.figure()
        plt.title("Computed vs Average SVC Reflectances")
        plt.plot(radiances['wavelengths'], radiances['reflectance'], label="Computed")
        plt.plot(radiances['wavelengths'], truth, label="Truth")
        plt.legend()
        plt.show()
