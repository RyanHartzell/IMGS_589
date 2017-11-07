class SpectralImage():
	
	@property
	def image(self):
		return self.__image
	@image.setter
	def image(self, image):
		self.__image = image
	@property
	def metadata(self):
		return self.__metadata
	@metadata.setter
	def metadata(self, metadataDict)
		self.__metadata.update({'manufacturer': metadataDict['Exif.Image.Make']})
		self.__metadata.update({'sensorModel': metadataDict['Exif.Image.Model']})
		self.__metadata.update({'serialNumber': metadataDict['Exif.Photo.BodySerialNumber']})
		self.__metadata.update({'bitDepth': metadataDict['Exif.Image.BitsPerSample']})
		self.__metadata.update({'fNumber': metadataDict['Exif.Photo.FNumber']})
		self.__metadata.update({'focalLength': metadataDict['Exif.Photo.FocalLength']})
		self.__metadata.update({'iso': metadataDict['Exif.Photo.ISOSpeed']})
		self.__metadata.update({'integrationTime': metadataDict['Exif.Photo.ExposureTime']})
		self.__metadata.update({'width': metadataDict['Exif.Image.ImageWidth']})
		self.__metadata.update({'height': metadataDict['Exif.Image.ImageLength']})
		self.__metadata.update({'bandName': metadataDict['Xmp.Camera.BandName']})
		self.__metadata.update({'centralWavelength': metadataDict['Xmp.Camera.CentralWavelength']})
		self.__metadata.update({'timeStamp': metadataDict['timeStamp']})

	def __init__(self):
		self.image = None
		self.metadata = {'manufacturer': 'None',
						 'sensorModel': 'None',
						 'serialNumber': 'None',
						 'bitDepth': None,
						 'fNumber': None,
						 'focalLength': None
						 'iso': None,
						 'integrationTime': None
						 'width': None,
						 'height': None,
						 'numberBands': None,
						 'bandName' : 'None',
						 'centralWavelength': None,
						 'wktProjection': '',
						 'originX': 0.0,
						 'originY': 0.0,
						 'pixelWidth': 1.0,
						 'pixelHeight': 1.0,
						 'timeStamp': None}
