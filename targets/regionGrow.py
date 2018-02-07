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
        # if image.dtype == np.uint8:
        #     threshMahal = 7
        # elif image.dtype == np.uint16:
        #     threshMahal = 7
        # else:
        #     threshMahal = 10
        if image.shape[2] == 3:
            threshMahal = 7
            threshDiff = 3
        elif image.shape[2] == 5:
            threshMahal = 7
            threshDiff = 50

        #print("Using default threshold variance of {0}".format(threshVar))

    #eightBit = (displayImage*255).astype(np.uint8)
    #sX = np.absolute(cv2.Sobel(displayImage, cv2.CV_64F, 1,0, ksize=5))
    #sY = np.absolute(cv2.Sobel(displayImage, cv2.CV_64F, 0,1, ksize=5))
    #sobel = sX*sY
    #image = sobel
    # cv2.circle(image,seedPoint, 2, (1,1,1), -1)
    # cv2.imshow("Image", image)
    # cv2.waitKey(0)

    print("Growing region based on seed point, be paitent for 2 seconds please")
    thresh = np.zeros(image.shape[:2])

    #Create the 3x3 inverse covariance matrix
    seedArea = image[seedPoint[1]-2:seedPoint[1]+3, seedPoint[0]-2:seedPoint[0]+3]
    flatSeed = seedArea.reshape(-1,seedArea.shape[-1])
    V = np.cov(flatSeed.T)
    #print("Covariance Sample Size: ({0},{1}) \n".format(seedArea.shape[0],seedArea.shape[1]), V)
    saturated = False
    if 0 or 1 in np.sum(V, axis=1):
        #print(np.sum(V,axis=1))
        saturated=True
        print("The seed area has no variance in a band")
    #try:                # print("Moving Value: {0} Seed Value: {1} Mahal Score: {2}".format(
                # inputValue,imrgbage[seedPoint[1],seedPoint[0]], int(zscore)))
    if saturated is False:
        #THIS DOES NOT WORK FOR TARGETS THAT ARE SATURATED
        try:
            VI = np.linalg.inv(V)
            #print("Inverse Covariance (rounded) \n", np.around(VI))
        except:
            saturated = True
    #except:
    #    print("Seed did not grow, please select points as usual.")
    #    return None, None

    newPixels = True
    listOfGoodPoints = [seedPoint]
    thresh[seedPoint[1],seedPoint[0]] = 1
    # rgb = image[:,:,:3]/np.max(image[:,:,:3])
    # moving = rgb.copy()
    # good = rgb.copy()
    # badMah, badDiff = rgb.copy(), rgb.copy()
    #rgb = cv2.circle(rgb.copy(),tuple(seedPoint), 2, (1,1,1), -1)
    #cv2.imshow("Seed Point on Image", rgb)
    #cv2.waitKey(0)

    seedValue = image[seedPoint[1], seedPoint[0]]
    startTime = time.time()
    #print(seedPoint)
    #movement is defined in xy coordinates to be coimageStacknsistant with the seed
    for point in listOfGoodPoints:
        movement = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]
        for m in range(len(movement)):
            movingPoint = (point[0]+movement[m][0], point[1]+movement[m][1])
            #cv2.circle(moving,movingPoint, 2, (1,1,1), -1)
            #cv2.imshow("Moving Point", moving)
            #cv2.waitKey(1)
            try:
                inputValue = image[movingPoint[1], movingPoint[0]]
            except:
                continue
            if saturated is False:
                zscore = mahalanobis(inputValue, image[seedPoint[1],seedPoint[0]], VI)
                #print(float(inputValue)-float(image[seedPoint[1],seedPoint[0]]))
                movingArray = np.asarray(inputValue, dtype=np.float)
                seedArray = np.asarray(image[seedPoint[1],seedPoint[0]], dtype=np.float)
                difference = np.absolute(np.subtract(movingArray,seedArray))
                #print(difference)
                # print("Moving Value: {0} Seed Value: {1} Mahal Score: {2}".format(
                # inputValue,image[seedPoint[1],seedPoint[0]], int(zscore)))
                #print(zscore, np.asarray(movingPoint)*1.5)
                #c50v2.waitKey(0)
                #if zscore < threshMahal:
                #print("Difference Sum: {0} Mahal Score: {1}".format(np.sum(difference), zscore))
                if zscore > threshMahal and np.sum(difference) < threshDiff:
                    #print("Moving Value: {0} Seed Value: {1} Mahal Score: {2}".format(
                    #    inputValue,image[seedPoint[1],seedPoint[0]], int(zscore)))
                    #cv2.circle(good,movingPoint,2,(0,1,0),-1)
                    thresh[movingPoint[1], movingPoint[0]] = 1
                    if movingPoint not in listOfGoodPoints:
                        listOfGoodPoints.append(movingPoint)
                # if zscore < threshMahal:
                #     cv2.circle(badMah,movingPoint, 2, (0,0,1), -1)
                # if np.sum(difference) > threshDiff:
                #     cv2.circle(badDiff,movingPoint, 2, (1,0,0), -1)
                #
                # cv2.imshow("Good Points", good)
                # cv2.imshow("Bad Points (Mah)", badMah)
                # cv2.imshow("Bad Points (Diff)", badDiff)

                #cv2.waitKey(1)
                    #print("Moving Coordinate [xy] {0}".format(movingPoint))
            else:
                #print("Moving Value: {0} Seed Value: {1}".format(
                    #inputValue,image[seedPoint[1],seedPoint[0]]))
                if 0 in inputValue-seedValue:
                #if np.array_equal(inputValue, seedValue):
                #if inputValue == seedValue:
                    thresh[movingPoint[1], movingPoint[0]] = 1
                    if movingPoint not in listOfGoodPoints:
                        listOfGoodPoints.append(movingPoint)
        elapsedTime = time.time() - startTime
        if elapsedTime > 2:
            #If region growing takes longer thanimageStack 5 seconds break
            print("Ran out of time... 2 seconds.")
            break
        listOfGoodPoints.pop(0)

    #kernel = np.ones((3,3), np.uint8)
    #thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = (thresh*255).astype(np.uint8)

    kernel = np.ones((2,2), np.uint8)
    floodmask = cv2.erode(thresh,kernel,iterations = 1)

    #floodmask = thresh

    #cv2.imshow("FLOOD MASK", floodmask*image[:,:,0])
    #cv2.waitKey(0)

    _, contours, hierarchy = cv2.findContours(floodmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #c = max(contours[0], key=cv2.contourArea)
    #rgb = image[:,:,3]/np.max(image[:,:,:3])
    #cv2.imshow("RGB",rgb)
    #cv2.drawContours(rgb, contours, -1,(1,1,1),3)
    #cv2.imshow("CONTOURS", rgb)
    #cv2.waitKey(0)
    x, y = None, None
    #print(len(contours))
    #print(seedPoint)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    try:
        area = cv2.contourArea(contours[0])
        if area <=2:
            contours = []
    except:
        pass

    print("Completed Region Growing. Contours Found: {0}".format(len(contours)))
    if len(contours) >= 1:
        cpoints = contours[0]

        left = tuple(cpoints[cpoints[:, :, 0].argmin()][0])
        right = tuple(cpoints[cpoints[:, :, 0].argmax()][0])
        top = tuple(cpoints[cpoints[:, :, 1].argmin()][0])
        bot = tuple(cpoints[cpoints[:, :, 1].argmax()][0])

        x = [top[0], right[0], bot[0], left[0]]
        y = [top[1], right[1], bot[1], left[1]]

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
