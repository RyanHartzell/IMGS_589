""" Radon Transform as described in Birkfellner, Wolfgang. Applied Medical Image Processing: A Basic Course. [p. 344] """
from scipy import misc
import numpy as np
import matplotlib.pyplot as plt
import os.path
import cv2

def discrete_radon_transform(x, y, stack, R, steps):
	# x and y are vectors of length four, coordinates of template
    for s in range(steps):
		# generate x' and y' for every step
		

		# sum lines of values within x' y' bounding box
		R[:,s] = sum(rotation)

	return R

def pre_radon_transform(src, steps):
	R_empty = np.zeros((steps, len(image)), dtype='float64')
	n, m = src.shape
	rotation_stack = np.zeros(n, m, steps)

	for s in range(steps):
		rotation = misc.imrotate(src, -s*180/steps).astype('float64')
		rotation_stack[:,:,s] = rotation 

	return R_empty, rotation_stack

home = os.path.expanduser('~')
# Read image as 64bit float gray scale
# filenameLenna = home + os.path.sep + 'src/python/examples/data/lenna.tiff'
# filenameLennaFace = home + os.path.sep + 'src/pythpn/examples/data/lennaface.png'

filenameLenna = 'lenna.tif'
filenameLennaFace = 'lennaface.tiff'

#filename = np.zeros_like(filename)
#cv2.imwrite('sqaure_like_lenna.tif',filename)
#image = (filename.flatten)
#print(image.shape)

kernel = misc.imread(filenameLennaFace, flatten=True).astype('float64')
radon_kernel = discrete_radon_transform(kernel, 54)

full = misc.imread(filenameLenna, flatten=True).astype('float64')
m = kernel.shape[0]
n = kernel.shape[1]
size = kernel.size

rmse_map = np.zeros_like(full)

#broken at the moment ... data type issue

for row in range(full.shape[0] - m):
	for col in range(full.shape[1] - n):
		sub_full_radon = discrete_radon_transform(full[row:row+m, col:col+n], 54)
		rmse = np.sqrt(((radon_kernel - sub_full_radon) * (radon_kernel - sub_full_radon)).mean())

		rmse_map[col, row] = rmse

minimum = np.where(rmse_map == np.min(rmse_map))
print(minimum)

# Plot the original and the radon transformed image
plt.subplot(1, 3, 1), plt.imshow(kernel, cmap='gray')
plt.xticks([]), plt.yticks([])
plt.subplot(1, 3, 2), plt.imshow(radon_kernel, cmap='gray')
plt.xticks([]), plt.yticks([])
plt.subplot(1, 3, 3), plt.imshow(rmse_map, cmap='gray')
plt.xticks([]), plt.yticks([])
plt.show()