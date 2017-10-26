""" Radon Transform as described in Birkfellner, Wolfgang. Applied Medical Image Processing: A Basic Course. [p. 344] """
from scipy import misc
import numpy as np
import matplotlib.pyplot as plt
import os.path
import cv2

def discrete_radon_transform(image, steps):
    R = np.zeros((steps, len(image)), dtype='float64')
    for s in range(steps):
        rotation = misc.imrotate(image, -s*180/steps).astype('float64')
        R[:,s] = sum(rotation)
    return R


home = os.path.expanduser('~')
# Read image as 64bit float gray scale
filenameLenna = home + os.path.sep + 'src/python/examples/data/lenna.tiff'
filenameLennaFace = home + os.path.sep + 'src/pythpn/examples/data/lennaface.png'
#filename = np.zeros_like(filename)
#cv2.imwrite('sqaure_like_lenna.tif',filename)
#image = (filename.flatten)
#print(image.shape)
image = misc.imread(filename, flatten=True).astype('float64')
radon = discrete_radon_transform(image, 256)
# Plot the original and the radon transformed image
plt.subplot(1, 2, 1), plt.imshow(image, cmap='gray')
plt.xticks([]), plt.yticks([])
plt.subplot(1, 2, 2), plt.imshow(radon, cmap='gray')
plt.xticks([]), plt.yticks([])
plt.show()
