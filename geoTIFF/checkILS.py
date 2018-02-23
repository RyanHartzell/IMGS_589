import metadataReader
import glob

def findallILS(imagedirectory,band):
    if band == 'blue':
        bandspec = '_1.tif'
    elif band == 'green':
        bandspec = '_2.tif'
    elif band == 'red':
        bandspec = '_3.tif'
    elif band == 'NIR':
        bandspec = '_4.tif'
    elif band == 'RedEdge':
        bandspec = '_5.tif'
    imagelist = glob.glob(imagedirectory + '*' + bandspec)

    ILSreadings = []
    n = 0
    for image in imagelist:
        print('Image {} completed of {}'.format(n,len(imagelist)))
        metadatadict = metadataReader.metadataGrabber(image)
        ILS = metadatadict['Xmp.DLS.SpectralIrradiance']
        ILSreadings.append(ILS)
        n += 1
    return ILSreadings

def findFlightAngle(imagedirectory):
    imagelist = glob.glob(imagedirectory + '*' + '_1.tif')

    rollReadings = []
    pitchReadings = []
    yawReadings = []
    n = 1
    for image in imagelist:
        print('Image {} completed of {}'.format(n,len(imagelist)))
        metadatadict = metadataReader.metadataGrabber(image)
        roll = metadatadict['Xmp.DLS.Roll']
        #roll = metadatadict['Xmp.Camera.IrradianceRoll']
        rollReadings.append(roll)
        pitch = metadatadict['Xmp.DLS.Pitch']
        #pitch = metadatadict['Xmp.Camera.IrradiancePitch']
        pitchReadings.append(pitch)
        yaw = metadatadict['Xmp.DLS.Yaw']
        #yaw = metadatadict['Xmp.Camera.IrradianceYaw']
        yawReadings.append(yaw)
        n += 1
    return rollReadings,pitchReadings,yawReadings

if __name__ == '__main__':

    from matplotlib import pyplot as plt
    import numpy as np

    print('here')
    directoryname = '/research/imgs589/imageLibrary/DIRS/20171108/Missions/1330_375ft/micasense/processed/'
    #directoryname = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/processed/'
    band = 'blue'
    print('here')
    ILSreadings = findallILS(directoryname,band)
    print('here')
    #plt.plot(ILSreadings)
    #plt.show()

    #ILSreadings = np.asarray(ILSreadings)
    #ILSslopes = np.gradient(ILSreadings)

    #plt.plot(ILSslopes)
    #plt.show()
    rollReadings,pitchReadings,yawReadings = findFlightAngle(directoryname)
    #pitchvalues = np.asarray(pitchReadings)
    #pitchReadings = np.gradient(pitchvalues)
    #derivative = np.gradient(rollReadings)
    #plt.plot(rollReadings)
    #plt.show()

    pitch = np.asarray(pitchReadings)
    badindices = np.where(np.absolute(pitch)>=0.1)[0]
    print(badindices)
    allindices = np.arange(0,np.size(pitch))
    print(allindices)
    goodindices = np.setdiff1d(allindices,badindices)
    print(goodindices)
    filteredILS = []
    filteredPitch = []
    for index in goodindices:
        print(int(index))
        index = int(index)
        filteredILS.append(ILSreadings[index])
        filteredPitch.append(pitchReadings[index])
    plt.figure(figsize=(15,7))
    plt.subplot(2,1,1)
    plt.plot(filteredILS, 'b-')
    plt.xlabel('Reduced Image #')
    plt.ylabel('Radiance')

    plt.subplot(2,1,2)
    plt.plot(filteredPitch, 'r-')
    plt.xlabel('Reduced Image #')
    plt.ylabel('Pitch')
    plt.show()
