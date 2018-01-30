
def plotExposure(imageDirectory, bands=5):
    import sys
    import glob
    import bisect
    from metadataReader import metadataGrabber

    processedList = sorted(glob.glob(imageDirectory + "*.tif"))
    if len(processedList) % bands != 0:
        print("The total number of found '.tiff' images mod bands is not 0")
        sys.exit(1)
    totalUniqueImages = len(processedList)//bands

    #PLOT ISO BY SHUTTER SPEED SEPERATED BY COLOR FOR BAND
    ISO = [[], [], [], [], []]
    Exposure = [[], [], [], [], []]
    CentralWavelengthOrder = []
    for t in range(0,len(processedList),bands):
        for i in range(bands):
            imageMetadata = metadataGrabber(processedList[t+i])
            imageWavelength = imageMetadata["Xmp.Camera.CentralWavelength"]
            if t == 0:
                bisect.insort_left(CentralWavelengthOrder, imageWavelength,
                                    lo=0, hi=len(CentralWavelengthOrder))
            else:
                imageExposure = imageMetadata["Exif.Photo.ExposureTime"]
                imageISO = imageMetadata["Exif.Photo.ISOSpeed"]
                imageIndex = CentralWavelengthOrder.index(imageWavelength)
                ISO[imageIndex].append(imageISO)
                Exposure[imageIndex].append(imageExposure)
            print(t, "/", len(processedList))
    print(ISO)
    print(Exposure)
    print(CentralWavelengthOrder)





            #uniqueImageList.append(processedList[t+i])
            #metadataReader.metadataGrabber(processedList[t+1])






if __name__ == "__main__":
    imageDirectory = "/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/processed/"
    plotExposure(imageDirectory, bands=5)
