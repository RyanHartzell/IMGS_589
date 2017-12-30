
def userMove(fixedIm, movingIm, matrix=False, resize=False):
    import cv2
    import numpy

    if len(fixedIm.shape) == 3:
        fixedImage = fixedIm[:,:,0]
    else:
        fixedImage = fixedIm
    if len(movingIm.shape) == 3:
        movingImage = movingIm[:,:,0]
    else:
        movingImage = movingIm

    warpedImage = None
    affineMatrix = None
    transX = 0
    transY = 0

    while True:
        stackedImage = cv2.addWeighted(fixedImage, .5, movingImage, .5, 0)
        if resize > 0:
            radius = int(5.5*266.66667*numpy.tan(numpy.deg2rad(numpy.abs(10)/2)))
            center = (stackedImage.shape[0]//2, stackedImage.shape[1]//2)
            stackedImage = stackedImage[center[0]-radius:center[0]+radius,center[1]-radius:center[1]+radius]
            stackedImage = cv2.resize(stackedImage, None, fx=resize, fy=resize, interpolation=cv2.INTER_LANCZOS4)

        cv2.imshow("Stacked Image: WASD (SHIFT x5) | ' ' to accept | ESC to skip", stackedImage)
        resp = cv2.waitKey(100)
        if resp == ord('a'):
            movingImage = numpy.pad(movingImage,((0,0),(0,1)), mode='constant')[:,1:]
            transX -= 1
        elif resp == ord('A'):
            movingImage = numpy.pad(movingImage,((0,0),(0,5)), mode='constant')[:,5:]
            transX -= 5
        elif resp == ord('d'):
            movingImage = numpy.pad(movingImage,((0,0),(1,0)), mode='constant')[:,:-1]
            transX += 1
        elif resp == ord('D'):
            movingImage = numpy.pad(movingImage,((0,0),(5,0)), mode='constant')[:,:-5]
            transX += 5
        elif resp == ord('s'):
            movingImage = numpy.pad(movingImage,((1,0),(0,0)), mode='constant')[:-1,:]
            transY += 1
        elif resp == ord('S'):
            movingImage = numpy.pad(movingImage,((5,0),(0,0)), mode='constant')[:-5,:]
            transY += 5
        elif resp == ord('w'):
            movingImage = numpy.pad(movingImage,((0,1),(0,0)), mode='constant')[1:,:]
            transY -= 1
        elif resp == ord('W'):
            movingImage = numpy.pad(movingImage,((0,5),(0,0)), mode='constant')[5:,:]
            transY -= 5
        elif resp == ord(' '):
            warpedImage = movingImage
            break
        elif resp == 27:
            warpedImage = movingIm
            break
    if matrix == True:
        affineMatrix = numpy.matrix([[1, 0, transX],
                                     [0, 1, transY]]).astype(numpy.float32)
        return movingImage, affineMatrix

    cv2.destroyWindow("Stacked Image: WASD (SHIFT x5) | ' ' to accept | ESC to skip")
    return movingImage

if __name__ == "__main__":
    import cv2
    import numpy

    imageDirectory = "/research/imgs589/imageLibrary/DIRS/20171102/Missions/1400/micasense/processed/"
    green = imageDirectory + "IMG_0120_2.tif"
    red = imageDirectory + "IMG_0120_3.tif"
    re = imageDirectory + "IMG_0120_5.tif"

    green = cv2.imread(green, cv2.IMREAD_UNCHANGED)
    red = cv2.imread(red, cv2.IMREAD_UNCHANGED)
    re = cv2.imread(re, cv2.IMREAD_UNCHANGED)

    warpedRE = userMove(red, re)
    warpedGreen = userMove(red, green)

    if warpedRE is not None and warpedGreen is not None:
        stackedImage = numpy.dstack((warpedGreen, red, warpedRE))
        cv2.imshow("False RE", stackedImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
