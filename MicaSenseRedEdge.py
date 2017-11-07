from IMGS_589 import SpectralImage
from IMGS_589.geoTIFF.metadataReader import metadataGrabber
from os.path import isfile

class MicaSenseRedEdge(IMGS_589.SpectralImage):
	def __init__(self):
		SpectralImage.__init__(self)
		self.readFile(fileName)

	@property
	def image(self):
		return self.__image
	
	@image.setter
	def image(self, image):
		self.__image = image
	
	@property
	def metadata(self):
		return self.__metadata

	def readFile(fileName):
		if os.path.isfile(fileName):
			self.metadata = metadataGrabber(fileName)
