#A method to use morphology to use a single click to get a target

def regionGrow(image, mapName=None, seedPoint=None, threshMahal=None):
    import cv2
    import time
    import PointsSelected
    import numpy as np
    import scipy
    from scipy.spatial.distance import mahalanobis

    if image is None:
        print("No image was found, please check the path or the read in.")
        sys.exit(1)
    displayImage = image.copy()

    if seedPoint is None:
        if len(displayImage.shape) > 2:
            if mapName is not None:
                cv2.imshow(mapName, displayImage[:,:,:3])
            else:
                cv2.imshow("Choose Seed Point", displayImage[:,:,:3])
        else:
            if mapName is not None:
                cv2.imshow(mapName, displayImage)
            else:
                cv2.imshow("Choose Seed Point", displayImage)

        if mapName is not None:
            p = PointsSelected.PointsSelected(mapName, verbose=False)
        else:
            p = PointsSelected.PointsSelected("Choose Seed Point", verbose=False)

        while p.number(p) < 1:
            cv2.waitKey(10)
        if mapName is None:
            cv2.destroyWindow("Choose Seed Point")
        seedPoint = (p.x(p)[0], p.y(p)[0])
        #print(seedPoint)
        #print(image[seedPoint[1],seedPoint[0]])

    if threshMahal is None:
        if image.dtype == np.uint8:
            threshMahal = 7
        elif image.dtype == np.uint16:
            threshMahal = 7
        else:
            threshMahal = 10
        #print("Using default threshold variance of {0}".format(threshVar))

    #eightBit = (displayImage*255).astype(np.uint8)
    sX = np.absolute(cv2.Sobel(displayImage, cv2.CV_64F, 1,0, ksize=5))
    sY = np.absolute(cv2.Sobel(displayImage, cv2.CV_64F, 0,1, ksize=5))
    sobel = sX*sY
    #image = sobel
    # cv2.circle(image,seedPoint, 2, (1,1,1), -1)
    # cv2.imshow("Image", image)
    # cv2.waitKey(0)

    print("Growing region based on seed point, be paitent for 2 seconds please")
    thresh = np.zeros(image.shape[:2])

    #Create the 3x3 inverse covariance matrix
    seedArea = image[seedPoint[1]-1:seedPoint[1]+2, seedPoint[0]-1:seedPoint[0]+2]
    flatSeed = seedArea.reshape(-1,seedArea.shape[-1])

    V = np.cov(flatSeed.T)
    saturated = False
    if np.sum(V) == 0:
        saturated=True
        print("The seed area has no variance per band")
    #try:
    if saturated is False:
        #THIS DOES NOT WORK FOR TARGETS THAT ARE SATURATED
        VI = np.linalg.inv(V)
    #except:
    #    print("Seed did not grow, please select points as usual.")
    #    return None, None


    newPixels = True
    listOfGoodPoints = [seedPoint]
    thresh[seedPoint[1],seedPoint[0]] = 1
    startTime = time.time()
    #movement is defined in xy coordinates to be coimageStacknsistant with the seed
    for point in listOfGoodPoints:
        movement = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]
        for m in range(len(movement)):
            movingPoint = (point[0]+movement[m][0], point[1]+movement[m][1])
            #cv2.circle(image,movingPoint, 2, (1,1,1), -1)
            #cv2.imshow("Image", image)
            #cv2.waitKey(1)
            try:
                inputValue = image[movingPoint[1], movingPoint[0]]
            except:
                continue
            if saturated is False:
                zscore = mahalanobis(inputValue, image[seedPoint[1],seedPoint[0]], VI)
                if zscore < threshMahal:
                    thresh[movingPoint[1], movingPoint[0]] = 1
                    if movingPoint not in listOfGoodPoints:
                        listOfGoodPoints.append(movingPoint)
            else:
                if inputValue == image[seedPoint[1], seedPoint[0]]:
                    thresh[movingPoint[1], movingPoint[0]] = 1
                    if movingPoint not in listOfGoodPoints:
                        listOfGoodPoints.append(movingPoint)
        elapsedTime = time.time() - startTime
        if elapsedTime > 2:
            #If region growing takes longer thanimageStack 5 seconds break
            break
        listOfGoodPoints.pop(0)

    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = (thresh*255).astype(np.uint8)

    kernel = np.ones((3,3), np.uint8)
    floodmask = cv2.erode(thresh,kernel,iterations = 2)

    _, contours, hierarchy = cv2.findContours(floodmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #c = max(contours[0], key=cv2.contourArea)
    x, y = None, None
    if len(contours) > 0:
        cpoints = contours[0]
        left = tuple(cpoints[cpoints[:, :, 0].argmin()][0])
        right = tuple(cpoints[cpoints[:, :, 0].argmax()][0])
        top = tuple(cpoints[cpoints[:, :, 1].argmin()][0])
        bot = tuple(cpoints[cpoints[:, :, 1].argmax()][0])

        x = [top[0], right[0], bot[0], left[0]]
        y = [top[1], right[1], bot[1], left[1]]
    print("Completed Region Growing")

    return x, y

if __name__ == '__main__':
    import cv2
    import os
    import time
    import numpy as np
    from osgeo import gdal
    #geotiffFilename = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/geoTiff/IMG_0106.tiff'
    geotiffFilename = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/geoTiff/IMG_0020.tiff'

    imageStack = gdal.Open(geotiffFilename).ReadAsArray()
    imageStack = np.moveaxis(imageStack, 0, -1)
    #imageStack = imageStack/np.max(imageStack)
    rgb = imageStack[:,:,:3]
    rgb = rgb/np.max(rgb)
    mapName = "Test Image"
    #radius = 175
    #imageCenter = (imageStack.shape[0]//2, imageStack.shape[1]//2)
    #iSCrop = imageStack[imageCenter[0]-radius:imageCenter[0]+radius,imageCenter[1]-radius:imageCenter[1]+radius, :]
    #blue = imageStack[:,:,0]
    #imageStack= cv2.resize(iSCrop, None,fx=2, fy=2,interpolation=cv2.INTER_AREA)
    #blue = blue/np.max(blue)
    x, y = regionGrow(rgb, mapName, seedPoint=None)
    points = np.asarray(list(zip(x, y)),np.int32)
    points = points.reshape((-1,1,2))
    rgb = cv2.polylines(rgb.copy(), [points], True, (.9, 0, 0))
    cv2.imshow(mapName, rgb)
    cv2.waitKey(0)
