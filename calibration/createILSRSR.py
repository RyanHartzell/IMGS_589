def getImages(imageDirectory, plotting=True):
    import glob
    import os
    import numpy
    import context
    import matplotlib
    from matplotlib import pyplot as plt
    from context import geoTIFF
    from geoTIFF import metadataReader

    dlsDictList = [{},{},{},{},{}]
    orientation = ['Left', 'Middle', 'Right']
    for o in orientation:
        currentDirectory = imageDirectory+'/'+o+'/*.tif'
        imageList = sorted(glob.glob(currentDirectory))
        dlsDict = {"Blue": [], "Green": [], "Red": [],
                                    "NIR": [], "Red edge": []}
        for image in imageList:
            metadata = metadataReader.metadataGrabber(image)
            dlsIrrad = metadata['Xmp.DLS.SpectralIrradiance']
            bandName = metadata['Xmp.Camera.BandName']
            dlsDict[bandName].append(dlsIrrad)

        maxList = {k:max(v) for k,v in dlsDict.items()}
        maxList = sorted(maxList, key=maxList.get, reverse=True)

        if o == "Middle":
            dlsDictList[4] = dlsDict["Red edge"]


        if plotting:
            xvals = numpy.arange(380, 1000 + 10, 10)
            for k in dlsDict.keys():
                plt.figure(o)
                plt.title("Downwelling Light Sensor Orientation: {0}".format(o))
                plt.plot(xvals, dlsDict[k], label=k)
                plt.xlabel("Wavelengths [nm]")
                plt.ylabel("DLS Spectral Irradiance [W/m^2/nm]")
                plt.xlim(380, 1000)
                plt.ylim(0, max(dlsDict[maxList[0]]) + .002)
                plt.legend(loc=5)
                

            for a in [0,1]:
                annotation = "{0} max {1:.5f}".format(maxList[a],max(dlsDict[maxList[a]]))
                plt.annotate(annotation,
                        (xvals[dlsDict[maxList[a]].index(max(dlsDict[maxList[a]]))],
                        max(dlsDict[maxList[a]])))
            plt.show()



if __name__ == "__main__":

    baseDirectory = "/research/imgs589"
    getImages(baseDirectory)
