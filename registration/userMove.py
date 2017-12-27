
def userMove(fixedIm, movingIm):
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

    while True:
        stackedImage = cv2.addWeighted(fixedImage, .5, movingImage, .5, 0)
        cv2.imshow("Stacked Image", stackedImage)
        resp = cv2.waitKey(100)
        if resp == ord('a'):
            movingImage = numpy.pad(movingImage,((0,0),(0,1)), mode='constant')[:,1:]
        elif resp == ord('A'):
            movingImage = numpy.pad(movingImage,((0,0),(0,5)), mode='constant')[:,5:]
        elif resp == ord('d'):
            movingImage = numpy.pad(movingImage,((0,0),(1,0)), mode='constant')[:,:-1]
        elif resp == ord('D'):
            movingImage = numpy.pad(movingImage,((0,0),(5,0)), mode='constant')[:,:-5]
        elif resp == ord('s'):
            movingImage = numpy.pad(movingImage,((1,0),(0,0)), mode='constant')[:-1,:]
        elif resp == ord('S'):
            movingImage = numpy.pad(movingImage,((5,0),(0,0)), mode='constant')[:-5,:]
        elif resp == ord('w'):
            movingImage = numpy.pad(movingImage,((0,1),(0,0)), mode='constant')[1:,:]
        elif resp == ord('W'):
            movingImage = numpy.pad(movingImage,((0,5),(0,0)), mode='constant')[5:,:]
        elif resp == ord(' '):
            warpedImage = movingImage
            break
        elif resp == 27:
            warpedImage = movingIm
            break
    cv2.destroyAllWindows()

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
