import metadataReader
import glob
from matplotlib import pyplot as plt
import numpy as np
import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2
import collections

folderlocation = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/processed/'
imagelist = glob.glob(folderlocation+'*.tif')

#print(imagelist)
exposureList = []
isoList = []


n = 1
for image in imagelist:
	print('{} out of {}'.format(n,len(imagelist)))

	imagemetadata = GExiv2.Metadata(image)
	taglist = imagemetadata.get_tags()

	exposure = imagemetadata.get('Exif.Photo.ExposureTime')
	exposureNum = int(exposure.split('/')[0])
	exposureList.append(exposureNum)

	iso = imagemetadata.get('Exif.Photo.ISOSpeed')
	isoList.append(int(iso))

	n += 1

fig1 = plt.figure()
ax1 = fig1.add_subplot(121)
ax1.hist(exposureList,bins=500)
fig1.suptitle('Exposure Histogram on {}'.format(folderlocation.split('Missions/')[1]))
ax1.set_xlabel('Exposure Numerator (Exposure = Exposure Numerator/1000000)')
ax1.set_ylabel('Image Count')
#plt.show()

#fig2 = plt.figure()
ax2 = fig1.add_subplot(122)
ax2.hist(isoList,bins=100)
#ax2.set_title('ISO Histogram on {}'.format(folderlocation.split('Missions/')[1]))
ax2.set_xlabel('ISO')
ax2.set_ylabel('Image Count')

plt.show()
