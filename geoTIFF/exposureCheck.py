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
	
plt.hist(exposureList,bins=500)
plt.title('Exposure Histogram on {}'.format(folderlocation.split('Missions/')[1]))
plt.xlabel('Exposure Numerator (Exposure = Exposure Numerator/1000000)')
plt.ylabel('Image Count')
plt.show()

plt.hist(isoList,bins=100)
plt.title('ISO Histogram on {}'.format(folderlocation.split('Missions/')[1]))
plt.xlabel('ISO')
plt.ylabel('Image Count')
plt.show()
