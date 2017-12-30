
def preRegister(imageList, jsonify=False):
    import numpy
    import cv2
    import itertools
    import geoTIFF
    import registration
    #import context
    #from context import geoTIFF, registration

    combinations = [ i for i in itertools.combinations(imageList, 2)]

    matrixDict = {}
    for fix, mov in combinations:
        fixDict, movDict = geoTIFF.metadataGrabber(fix), geoTIFF.metadataGrabber(mov)
        fixBand, movBand = fixDict['Xmp.Camera.BandName'], movDict['Xmp.Camera.BandName']
        fixWL, movWL = fixDict['Xmp.Camera.CentralWavelength'], movDict['Xmp.Camera.CentralWavelength']
        fixIm = cv2.imread(fix, cv2.IMREAD_UNCHANGED)
        movIm = cv2.imread(mov, cv2.IMREAD_UNCHANGED)

        moved, matrix = registration.userMove(fixIm, movIm, matrix=True, resize=4)
        inverse = matrix.copy()
        inverse[:,2] = -matrix[:,2]
        if jsonify:
            matrixDict[(fixBand+'/'+movBand)] = matrix.tolist()
            matrixDict[(movBand+'/'+fixBand)] = inverse.tolist()
        else:
            matrixDict[(fixBand+'/'+movBand)] = matrix
            matrixDict[(movBand+'/'+fixBand)] = inverse


    return matrixDict

if __name__ == "__main__":
    import cv2
    import numpy
    import context
    from context import geoTIFF, registration

    imageDirectory = "/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/processed/"
    blue = imageDirectory + "IMG_0099_1.tif"
    green = imageDirectory + "IMG_0099_2.tif"
    red = imageDirectory + "IMG_0099_3.tif"
    re = imageDirectory + "IMG_0099_5.tif"
    nIR = imageDirectory + "IMG_0099_4.tif"

    imageList = [blue, green, red, re, nIR]
    dictionary = preRegister(imageList)
    print(dictionary)

    im1dict = geoTIFF.metadataGrabber(red)
    im2dict = geoTIFF.metadataGrabber(nIR)
    im1band, im2band = im1dict['Xmp.Camera.BandName'], im2dict['Xmp.Camera.BandName']
    matrix = dictionary[(im1band+'/'+im2band)]
    redIm = cv2.imread(red, cv2.IMREAD_UNCHANGED)
    #greenIm = cv2.imread(green, cv2.IMREAD_UNCHANGED)
    nIRIm = cv2.imread(nIR, cv2.IMREAD_UNCHANGED)

    warped = cv2.warpAffine(nIRIm, matrix, (redIm.shape[1], redIm.shape[0]))
    stack = cv2.addWeighted(redIm, .5, warped, .5, 0)

    cv2.imshow("Stack", stack)
    cv2.waitKey(0)
