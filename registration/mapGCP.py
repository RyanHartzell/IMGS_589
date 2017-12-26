def selectGCPoints(fixedIm, movingIm):
    import tkinter
    import cv2
    import numpy
    import context
    from context import targets

    root = tkinter.Tk()
    root.withdraw()
    root.update()
    screenWidth = root.winfo_screenwidth()
    screenHeight = root.winfo_screenheight()
    imageHeight, imageWidth = fixedIm.shape

    scaleFactor = (screenHeight)/imageHeight
    displayFixed = cv2.resize(fixedIm, None, fx=scaleFactor,
        fy=scaleFactor, interpolation=cv2.INTER_NEAREST)
    displayMoving = cv2.resize(movingIm, None, fx=scaleFactor,
        fy=scaleFactor, interpolation=cv2.INTER_NEAREST)

    if len(displayFixed.shape) == 2:
        displayFixed = cv2.merge((displayFixed, displayFixed, displayFixed))

    if len(displayMoving.shape) == 2:
        displayMoving = cv2.merge((displayMoving, displayMoving, displayMoving))

    displayFixed = ((displayFixed/numpy.max(displayFixed))*255).astype(numpy.uint8)
    displayMoving = ((displayMoving/numpy.max(displayMoving))*255).astype(numpy.uint8)
    drawFixed = displayFixed.copy()
    drawMoving = displayMoving.copy()

    fixedName = 'Select GCP for the fixed image. "f" to reset'
    cv2.namedWindow(fixedName, cv2.WINDOW_AUTOSIZE)
    movingName = 'Select GCP for the moving image. "m" to reset'
    cv2.namedWindow(movingName, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(fixedName, displayFixed)
    cv2.imshow(movingName, displayMoving)

    fixedP = targets.PointsSelected(fixedName, windowID=2, verbose=False)
    movingP = targets.PointsSelected(movingName, windowID=3,  verbose=False)
    fixedP.clearPoints(fixedP)
    movingP.clearPoints(movingP)

    fixedPoints = fixedP.number(fixedP)
    movingPoints = movingP.number(movingP)

    while True:

        if movingP.number(movingP) != movingPoints:
            movingPoints = movingP.number(movingP)
            cv2.circle(drawMoving,(movingP.x(movingP)[-1],movingP.y(movingP)[-1]), 2, (0,0,255), -1)
            cv2.putText(drawMoving,str(movingPoints),(movingP.x(movingP)[-1],
                        movingP.y(movingP)[-1]),cv2.FONT_HERSHEY_SIMPLEX,1,
                        (255,255,255),2,cv2.LINE_AA)
            cv2.imshow(movingName, drawMoving)
        if fixedP.number(fixedP) != fixedPoints:
            fixedPoints = fixedP.number(fixedP)
            cv2.circle(drawFixed,(fixedP.x(fixedP)[-1],fixedP.y(fixedP)[-1]), 2, (0,0,255), -1)
            cv2.putText(drawFixed,str(fixedPoints),(fixedP.x(fixedP)[-1],
                        fixedP.y(fixedP)[-1]),cv2.FONT_HERSHEY_SIMPLEX,1,
                        (255,255,255),2,cv2.LINE_AA)
            cv2.imshow(fixedName, drawFixed)

        resp = cv2.waitKey(100)
        if resp == ord('f'):
            fixedP.clearPoints(fixedP)
            fixedPoints = 0
            drawFixed = displayFixed.copy()
            cv2.imshow(fixedName, displayFixed)
        elif resp == ord('m'):
            movingP.clearPoints(movingP)
            movingPoints = 0
            drawMoving = displayMoving.copy()
            cv2.imshow(movingName, displayMoving)
        elif resp == ord(' '):
            if fixedPoints == 0 and movingPoints == 0:
                break
            elif fixedPoints > 2 and movingPoints > 2:
                break
            elif fixedPoints != movingPoints:
                print("You must select the same points on both images")
                print("Fixed Image Points {0}".format(fixedPoints))
                print("Moving Image Points {0}".format(movingPoints))
            else:
                print("0 or at least 3 points need to be chosen")
                print("Fixed Image Points {0}".format(fixedPoints))
                print("Moving Image Points {0}".format(movingPoints))
        elif resp == 27:
            fixedP.clearPoints(fixedP)
            movingP.clearPoints(movingP)
            break

    fixedPoints, movingPoints = fixedP.points(fixedP), movingP.points(movingP)
    fixedCoordXY = [(x/scaleFactor, y/scaleFactor) for x, y in fixedPoints]
    movingCoordXY = [(x/scaleFactor, y/scaleFactor) for x, y in movingPoints]

    cv2.destroyAllWindows()

    return fixedCoordXY, movingCoordXY

def mapGCP(fixedIm, movingIm, fixedCoor, movingCoor, order=1):
    import numpy
    import cv2

    fixedX = [x for x, y in fixedCoor]
    fixedY = [y for x, y in fixedCoor]
    movingX = [x for x, y in movingCoor]
    movingY = [y for x, y in movingCoor]

    warpedImage = None

    fX = numpy.asmatrix(fixedX, dtype=numpy.float64)
    fY = numpy.asmatrix(fixedY, dtype=numpy.float64)
    mX = numpy.asmatrix(movingX, dtype=numpy.float64)
    mY = numpy.asmatrix(movingY, dtype=numpy.float64)

    for orderY in range(order+1):
        for orderX in range(order+1):
            currentX = numpy.power(mX, orderX)
            currentY = numpy.power(mY, orderY)
            if (orderX == 0) and (orderY == 0):
                design = numpy.multiply(currentX, currentY)
            else:
                design = numpy.concatenate((design,
                                        numpy.multiply(currentX, currentY)))
    design = design.T
    dependentA = numpy.asmatrix(fX)
    dependentB = numpy.asmatrix(fY)
    dependent = numpy.concatenate((dependentA, dependentB))
    dependent = dependent.T

    coefficients = (design.T * design).I * design.T * dependent

    rows = numpy.zeros(fixedIm.shape)
    rows[:,:] = numpy.arange(fixedIm.shape[0]).reshape([fixedIm.shape[0], 1])
    columns = numpy.zeros(fixedIm.shape)
    columns[:,:] = numpy.arange(fixedIm.shape[1])

    rows = numpy.asmatrix(rows.flatten(), dtype=numpy.float64)
    columns = numpy.asmatrix(columns.flatten(), dtype=numpy.float64)

    for orderY in range(order+1):
        for orderX in range(order+1):
            currentX = numpy.power(columns, orderX)
            currentY = numpy.power(rows, orderY)
            if (orderX == 0) and (orderY == 0):
                independent = numpy.multiply(currentX, currentY)
            else:
                independent = numpy.concatenate((independent,
                                      numpy.multiply(currentX, currentY)))
    independent = independent.T
    srcMap = independent * coefficients
    srcMapX = srcMap[:,0].reshape(fixedIm.shape).astype('float32')
    srcMapY = srcMap[:,1].reshape(fixedIm.shape).astype('float32')

    warpedImage = cv2.remap(movingIm, srcMapX, srcMapY, cv2.INTER_NEAREST )


    # fixedMatch = numpy.asarray(fixedCoordXY, dtype=numpy.float32)
    # movingMatch = numpy.asarray(movingCoordXY, dtype=numpy.float32)
    # if len(fixedMatch) != 0 and len(fixedMatch) != 0:
    #     M = cv2.estimateRigidTransform(fixedMatch, movingMatch, False)
    #     if M is not None:
    #         print("warping")
    #         warpedImage = cv2.warpAffine(movingIm, M, (fixedIm.shape[1], fixedIm.shape[0]))


    return warpedImage

if __name__ == "__main__":
    import cv2
    import numpy
    from mapGCP import mapGCP

    imageDirectory = "/research/imgs589/imageLibrary/DIRS/20171102/Missions/1400/micasense/processed/"
    green = imageDirectory + "IMG_0120_2.tif"
    red = imageDirectory + "IMG_0120_3.tif"
    re = imageDirectory + "IMG_0120_5.tif"

    green = cv2.imread(green, cv2.IMREAD_UNCHANGED)
    red = cv2.imread(red, cv2.IMREAD_UNCHANGED)
    re = cv2.imread(re, cv2.IMREAD_UNCHANGED)

    fixedCoordXY, movingCoordXY = selectGCPoints(red, re)
    warpedImage = mapGCP(red, re, fixedCoordXY, movingCoordXY)

    if warpedImage is not None:
        stackedImage = cv2.addWeighted(red, .5, warpedImage, .5, 0)
        cv2.imshow("Stacked", stackedImage)

        warpMatrix = numpy.eye(2,3, dtype=numpy.float32)
        cc, warpMatrix = cv2.findTransformECC(red.astype(numpy.float32), green.astype(numpy.float32), warpMatrix, cv2.MOTION_EUCLIDEAN)
        warpedGreen = cv2.warpAffine(green, warpMatrix, (red.shape[1], red.shape[0]),
                        flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

        falseRE = numpy.dstack((warpedGreen, red, warpedImage))
        cv2.imshow("False", falseRE)
        cv2.waitKey(0)
