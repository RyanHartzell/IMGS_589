"""
A simple fft base phase correlator between two multispectral images.
Author: Geoffrey Sasaki
"""

def registerCorConv(image1, image2, ECC=False, test=False):
    import cv2
    import numpy as np

    if image1.shape != image2.shape:
        msg = "Image 1's shape: {0} cannot be different".format(image1.shape) +\
                " than Image 2's shape {0}".format(image2.shape)
        raise TypeError(msg)

    if ECC:
        warpMatrix = np.eye(2,3, dtype=np.float32)
        #criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
        #            5000,  1e-10)
        cc, warpMatrix = cv2.findTransformECC(image1.astype(np.float32),
                image2.astype(np.float32), warpMatrix, cv2.MOTION_EUCLIDEAN)
        im2reg = cv2.warpAffine(image2, warpMatrix, (image1.shape[1],
                image1.shape[0]),flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
        return im2reg
    #Compute's the optimal DFT size, typically a power of 2
    newWidth = cv2.getOptimalDFTSize(image1.shape[1] + image2.shape[1] - 1)
    newHeight = cv2.getOptimalDFTSize(image1.shape[0]+ image1.shape[0] - 1)

    #Finds the difference of which to pad the array with 0's
    rightDiff = newWidth-image1.shape[1]
    bottomDiff = newHeight-image1.shape[0]

    #Fill the image to the new optimal DFT size with 0's
    image1pad = cv2.copyMakeBorder(image1, 0, bottomDiff, 0, rightDiff,
                            cv2.BORDER_CONSTANT, value=0)
    image2pad = cv2.copyMakeBorder(image2, 0, bottomDiff, 0, rightDiff,
                            cv2.BORDER_CONSTANT, value=0)

    #Finds the complex fourier transform of image1 and image2
    im1fourier = cv2.dft(np.float32(image1pad), flags=cv2.DFT_COMPLEX_OUTPUT)
    im2fourier = cv2.dft(np.float32(image2pad), flags=cv2.DFT_COMPLEX_OUTPUT)

    #Computes both the convolution and correlation between the images
    conv = cv2.mulSpectrums(im1fourier, im2fourier, 0, conjB=False)
    corr = cv2.mulSpectrums(im1fourier, im2fourier, 0, conjB=True)

    regConv = cv2.idft(conv)
    regCorr = cv2.idft(corr)

    regConv = regConv[:im1.shape[0],:im1.shape[1],0]
    regCorr = regCorr[:im1.shape[0],:im1.shape[1],0]

    if test:
        #Computes the magnitude and phase angle in radians
        mag1, angle1 = cv2.cartToPolar(im1fourier[:,:,0],im1fourier[:,:,1])
        mag2, angle2 = cv2.cartToPolar(im2fourier[:,:,0],im2fourier[:,:,1])
        magConv, angleConv = cv2.cartToPolar(conv[:,:,0],conv[:,:,1])
        magCorr, angleCorr = cv2.cartToPolar(corr[:,:,0],corr[:,:,1])

        #shifts the fourier transform so that the center is the maximimum
        mag1shifted, mag2shifted = np.fft.fftshift(mag1), np.fft.fftshift(mag2)
        magConvShifted, magCorrShifted = np.fft.fftshift(magConv), np.fft.fftshift(magCorr)

        #Normalizes the magnitude spectum into a floating point 0-1 for viewing
        im1magDisp = cv2.log(mag1shifted)
        im2magDisp = mag2shifted/np.max(mag2shifted)
        convMagDisp = magConvShifted/np.max(magConvShifted)
        corrMagDisp = magCorrShifted/np.max(magCorrShifted)

        cv2.imshow("Image 1 Magnitude", cv2.normalize(im1magDisp, 0,1, cv2.NORM_MINMAX))
        cv2.imshow("Image 2 Magnitude", cv2.normalize(mag2shifted, 0,1, cv2.NORM_MINMAX))
        cv2.imshow("Convolution Magnitude", cv2.normalize(magConvShifted, 0,1, cv2.NORM_MINMAX))
        cv2.imshow("Cross Correlation Magnitude", cv2.normalize(magCorrShifted, 0,1, cv2.NORM_MINMAX))

    return regConv.astype(image1.dtype), regCorr.astype(image1.dtype)

if __name__ == '__main__':
    import ipcv
    import cv2
    import numpy

    imageDir = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1400/micasense/processed/'
    blue = cv2.imread(imageDir + 'IMG_0110_1.tif', cv2.IMREAD_UNCHANGED)
    green = cv2.imread(imageDir + 'IMG_0110_2.tif', cv2.IMREAD_UNCHANGED)
    red = cv2.imread(imageDir + 'IMG_0110_3.tif', cv2.IMREAD_UNCHANGED)
    ir = cv2.imread(imageDir + 'IMG_0110_4.tif', cv2.IMREAD_UNCHANGED)
    re = cv2.imread(imageDir + 'IMG_0110_5.tif', cv2.IMREAD_UNCHANGED)

    blue = cv2.resize(blue, None, fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA)
    green = cv2.resize(green, None, fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA)
    red = cv2.resize(red, None, fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA)
    ir = cv2.resize(ir, None, fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA)
    re = cv2.resize(re, None, fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA)

    height,width = blue.shape

    blue = blue.reshape(height,width)
    green = green.reshape(height,width)
    red = red.reshape(height,width)
    ir = ir.reshape(height,width)
    re = re.reshape(height,width)

    #im1 = cv2.resize(im1, None, fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA)
    #im2 = cv2.resize(im2, None, fx=0.5, fy=0.5,interpolation=cv2.INTER_AREA)

    #cv2.imshow("Image 1 Original", im1)
    #cv2.imshow("Image 2 Original", im2)
    registeredBlue = registerCorConv(green, blue, ECC=True, test=False)
    registeredRed = registerCorConv(green, red, ECC=True, test=False)
    registeredRE = registerCorConv(green, re, ECC=True, test=False)
    registeredIR = registerCorConv(green, ir, ECC=True, test=False)

    rgb = numpy.dstack((registeredBlue, green, registeredRed))
    falseIR = numpy.dstack((green, registeredRed, registeredIR))
    falseRE = numpy.dstack((green, registeredRed, registeredRE))
    cv2.imshow("RGB", rgb)
    cv2.imshow("False IR", falseIR)
    cv2.imshow("False RE", falseRE)


    #cv2.imshow("Convolution Registered", conv)
    #cv2.imshow("Cross Correlation Registered", corr)

    action = ipcv.flush()
