#A method to use morphology to use a single click to get a target

def regionGrow(image, mapName=None, seedPoint=None, threshVar=None):
    import cv2
    import PointsSelected
    import numpy as np

    if image is None:
        print("No image was found, please check the path or the read in.")
        sys.exit(1)
    displayImage = image.copy()
    #elif len(image.shape) > 2:
    #    displayImage = np.zeros_like(image,dtype=np.float64)
    #    for channel in range(image.shape[2]):
    #        displayImage[:,:,channel] = image[:,:,channel]/np.max(image[:,:,channel])
    #else:
    #    displayImage = image/np.max(image)

    # windowName = "Sobel"
    #
    # if windowName == "Sobel":
    #     #Sobel works on color images, just does it by layer
    #     sobelx = np.absolute(cv2.Sobel(displayImage,cv2.CV_64F,1,0,ksize=3))
    #     sobely = np.absolute(cv2.Sobel(displayImage,cv2.CV_64F,0,1,ksize=3))
    #     gradient = sobely*sobelx
    # elif windowName == "Laplacian":
    #     gradient = cv2.Laplacian(displayImage, cv2.CV_64F)

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

    if threshVar is None:
        if image.dtype == np.uint8:
            threshVar = 1
        elif image.dtype == np.uint16:
            threshVar = 10
        else:
            threshVar = .1
        #print("Using default threshold variance of {0}".format(threshVar))
    #print(threshVar)
    thresh = np.zeros(image.shape[:2])
    for c in range(image.shape[2]):
        mask = np.zeros(image.shape[:2])
        seedValue = image[seedPoint[1], seedPoint[0],c]
        mask[((image[:,:,c] > seedValue-threshVar)&(image[:,:,c] < seedValue+threshVar))] =1
        thresh += mask

    thresh = (np.around(thresh/image.shape[2])*255).astype(np.uint8)

    kernel = np.ones((2,2), np.uint8)
    #thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    #cv2.imshow("thresh", thresh)
    mask = np.zeros((thresh.shape[0]+2, thresh.shape[1]+2),np.uint8)

    floodflags = 4
    floodflags |= cv2.FLOODFILL_MASK_ONLY
    floodflags |= (1 << 8)

    num,thresh,floodmask,rect = cv2.floodFill(thresh, mask, seedPoint, 1, (10,)*3, (10,)*3, floodflags)
    #num,thresh,floodmask,rect = cv2.floodFill(thresh, mask, seedPoint, 1)
    floodmask = floodmask[1:floodmask.shape[0]-1, 1:floodmask.shape[1]-1]
    kernel = np.ones((2,2), np.uint8)
    floodmask = cv2.erode(floodmask,kernel,iterations = 3)
    #cv2.imshow("FloodMask", floodmask.astype(np.float64))
    #print(np.sum(floodmask))
    #floodmask = cv2.resize(floodmask, None,fx=.95, fy=.95,interpolation=cv2.INTER_AREA)
    #floodmask = cv2.erode(floodmask, )
    _, contours, hierarchy = cv2.findContours(floodmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #c = max(contours[0], key=cv2.contourArea)
    cpoints = contours[0]
    left = tuple(cpoints[cpoints[:, :, 0].argmin()][0])
    right = tuple(cpoints[cpoints[:, :, 0].argmax()][0])
    top = tuple(cpoints[cpoints[:, :, 1].argmin()][0])
    bot = tuple(cpoints[cpoints[:, :, 1].argmax()][0])

    x = [top[0], right[0], bot[0], left[0]]
    y = [top[1], right[1], bot[1], left[1]]

    #disp = displayImage[:,:,:3].copy()
    #points = np.asarray(list(zip(x, y)),np.int32)
    #points = points.reshape((-1,1,2))
    #cv2.polylines(disp, [points], True, (1, 0, 0))

    #cv2.circle(disp, left, 1, (0, 0, 1), -1)
    #cv2.circle(disp, right, 1, (0, 1, 0), -1)
    #cv2.circle(disp, top, 1, (1, 0, 0), -1)
    #cv2.circle(disp, bot, 1, (1, 1, 0), -1)
    #disp = cv2.drawContours(disp, contours, -1, (0,0,1), 1)
    #cv2.imshow("Press 'y' to accept the contours, 'n' to reject", disp)

    #ans = None
    #while ans is None:
    #    resp = cv2.waitKey(10)
    #    if resp == ord('y'):
    #        ans = True
    #    elif resp == ord('n'):
    #        ans = False
    #    elif resp == 27:
    #        sys.exit(0)
    #cv2.destroyWindow("Press 'y' to accept the contours, 'n' to reject")


    #cv2.destroyAllWindows()
    return x, y

if __name__ == '__main__':
    import cv2
    import os
    import time
    import numpy as np
    from osgeo import gdal
    geotiffFilename = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/geoTiff/IMG_0106.tiff'

    imageStack = gdal.Open(geotiffFilename).ReadAsArray()
    imageStack = np.moveaxis(imageStack, 0, -1)

    radius = 175
    #imageCenter = (imageStack.shape[0]//2, imageStack.shape[1]//2)
    #iSCrop = imageStack[imageCenter[0]-radius:imageCenter[0]+radius,imageCenter[1]-radius:imageCenter[1]+radius, :]
    #blue = imageStack[:,:,0]
    #imageStack= cv2.resize(iSCrop, None,fx=2, fy=2,interpolation=cv2.INTER_AREA)
    #blue = blue/np.max(blue)
    morphology = regionGrow(imageStack, seedPoint=None)
