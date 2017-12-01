"""
['Exif.GPSInfo.GPSAltitude', 'Exif.GPSInfo.GPSAltitudeRef', 
'Exif.GPSInfo.GPSDOP', 'Exif.GPSInfo.GPSLatitude', 
'Exif.GPSInfo.GPSLatitudeRef', 'Exif.GPSInfo.GPSLongitude', 
'Exif.GPSInfo.GPSLongitudeRef', 'Exif.GPSInfo.GPSVersionID', 
'Exif.Image.0xbb94', 'Exif.Image.0xbb95', 'Exif.Image.0xbb96', 
'Exif.Image.BitsPerSample', 'Exif.Image.BlackLevel', 
'Exif.Image.BlackLevelRepeatDim', 'Exif.Image.DateTime', 'Exif.Image.ExifTag', 
'Exif.Image.GPSTag', 'Exif.Image.ImageLength', 'Exif.Image.ImageWidth', 
'Exif.Image.Make', 'Exif.Image.Model', 'Exif.Image.NewSubfileType', 
'Exif.Image.OpcodeList3', 'Exif.Image.Orientation', 
'Exif.Image.PhotometricInterpretation', 'Exif.Image.PlanarConfiguration', 
'Exif.Image.RowsPerStrip', 'Exif.Image.SamplesPerPixel', 'Exif.Image.Software', 
'Exif.Image.StripByteCounts', 'Exif.Image.StripOffsets', 'Exif.Image.XMLPacket', 
'Exif.Photo.BodySerialNumber', 'Exif.Photo.DateTimeDigitized', 
'Exif.Photo.DateTimeOriginal', 'Exif.Photo.ExifVersion', 
'Exif.Photo.ExposureProgram', 'Exif.Photo.ExposureTime', 
'Exif.Photo.FNumber', 'Exif.Photo.FocalLength', 
'Exif.Photo.FocalPlaneResolutionUnit', 'Exif.Photo.FocalPlaneXResolution', 
'Exif.Photo.FocalPlaneYResolution', 'Exif.Photo.ISOSpeed', 
'Exif.Photo.MeteringMode', 'Exif.Photo.SubSecTime', 'Xmp.Camera.BandName', 
'Xmp.Camera.BandSensitivity', 'Xmp.Camera.CentralWavelength', 
'Xmp.Camera.Irradiance', 'Xmp.Camera.IrradianceExposureTime', 
'Xmp.Camera.IrradianceGain', 'Xmp.Camera.IrradiancePitch', 
'Xmp.Camera.IrradianceRoll', 'Xmp.Camera.IrradianceYaw', 
'Xmp.Camera.RigCameraIndex', 'Xmp.Camera.WavelengthFWHM', 'Xmp.DLS.Bandwidth', 
'Xmp.DLS.CenterWavelength', 'Xmp.DLS.Exposure', 'Xmp.DLS.Gain', 
'Xmp.DLS.OffMeasurement', 'Xmp.DLS.Pitch', 'Xmp.DLS.RawMeasurement', 
'Xmp.DLS.Roll', 'Xmp.DLS.SensorId', 'Xmp.DLS.Serial', 
'Xmp.DLS.SpectralIrradiance', 'Xmp.DLS.SwVersion', 'Xmp.DLS.TimeStamp', 
'Xmp.DLS.Yaw', 'Xmp.MicaSense.BootTimestamp', 'Xmp.MicaSense.CaptureId', 
'Xmp.MicaSense.DarkRowValue', 'Xmp.MicaSense.FlightId', 
'Xmp.MicaSense.PressureAlt', 'Xmp.MicaSense.TriggerMethod']

<GExiv2.Metadata object at 0x7fa6cb983168 
(GExiv2Metadata at 0x564151217280)>
{'Xmp.Camera.IrradianceGain': 16.0, 'Exif.Image.ImageWidth': 1280.0, 
'Exif.Image.Model': 'RedEdge', 'Exif.Photo.FNumber': 2.8, 
'Xmp.Camera.BandName': 'Blue', 'Xmp.Camera.CentralWavelength': 475.0, 
'Xmp.Camera.IrradianceRoll': -0.3043803784501027, 
'Exif.Image.BitsPerSample': 16.0, 'Exif.Photo.ExposureProgram': 2.0, 
'Exif.Image.ImageLength': 960.0, 
'Exif.GPSInfo.GPSLongitude': (77.0, 1.0, 39.963), 
'Exif.Photo.DateTimeDigitized': '2017:07:26 16:12:57', 
'Exif.Photo.SubSecTime': '-279654', 
'Exif.Photo.ExifVersion': '48 50 51 48', 
'Exif.Photo.ExposureTime': 0.00135, 
'Exif.GPSInfo.GPSAltitude': 272.152, 'Xmp.Camera.WavelengthFWHM': 20.0, 
'Xmp.Camera.IrradianceYaw': -157.14660934524608, 
'Xmp.Camera.IrradianceExposureTime': 0.10100000351667404, 
'Exif.Image.DateTime': '2017:07:26 16:12:57', 
'Xmp.Camera.BandSensitivity': 1702040981.6335442, 
'Exif.Photo.DateTimeOriginal': '2017:07:26 16:12:57', 
'Exif.Image.SamplesPerPixel': 1.0, 
'Exif.GPSInfo.GPSLatitude': (42.0, 52.0, 26.92812), 
'Exif.Photo.FocalPlaneYResolution': 266.666667, 
'Xmp.Camera.Irradiance': 0.7153738737106323, 
'Exif.Photo.FocalPlaneXResolution': 266.666667, 
'Xmp.DLS.TimeStamp': '121456', 'Exif.Photo.ISOSpeed': 100.0, 
'Exif.Image.Make': 'MicaSense', 'Exif.Photo.FocalLength': 5.5, 
'Xmp.Camera.IrradiancePitch': -2.0375641618928038}
"""

'https://git.gnome.org/browse/gexiv2/tree/GExiv2.py'

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2
import collections

def metadataGrabber(filename):
    #sampleimage = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'

    imagemetadata = GExiv2.Metadata(filename)
    #print(imagemetadata.sort())
    taglist = imagemetadata.get_tags()
    #print(taglist)

    indexlist = (0,3,5,11,14,17,18,19,20,27,33,34,35,36,37,38,39,41,42,43,45,46,47,48,49,50,51,52,53,54,56,69)
    metadatadict = {}

    for index in range(len(taglist)):
        specification = taglist[index]
        entry = imagemetadata.get(specification)

        #Single Fractions to Float Case
        if index in ( 0,37,38,39,41,42):
            split = entry.index('/')
            entry = float(entry[:split])/float(entry[split+1:])

        #Three Fractions to Floats Case for GPS Coordinates
        elif index in (3,5):
            firstsplit = entry.index('/')
            secondsplit = entry.index('/',firstsplit+1)
            thirdsplit = entry.index('/',secondsplit+1)
            firstspace = entry.index(' ')
            secondspace = entry.index(' ',firstspace+1)

            divisor = float(entry[firstsplit+1:firstspace])
            degrees = float(entry[:firstsplit])/divisor
            minutes = float(entry[firstspace+1:secondsplit])/divisor
            seconds = float(entry[secondspace+1:thirdsplit])/divisor

            entry = (degrees,minutes,seconds)

        #String to string case for names,date,time
        elif index in (4,6,19,20,34,45,46,66,68,69,72,73,74):
            #print(index, specification, entry)
            pass
        elif index in (2,7,8,9,10,12,13,14,22,28,29,30,31,33,35):
            #These Suck
            continue

        #All other cases, no integers used for ease later
        else:
            #print(index)
            #print(entry)
            #print(index, specification, entry)
            #print(entry)
            entry = float(entry)

        metadatadict[specification] = entry

    dateTime = metadatadict['Exif.Photo.DateTimeOriginal']
    dateTime = dateTime.replace(' ', 'T')
    dateTime = dateTime.replace(':','-',2)
    subSec = metadatadict['Exif.Photo.SubSecTime']
    timeStamp = dateTime + '.' + subSec[1:]
    metadatadict['timeStamp'] = timeStamp

    return metadatadict
    
if __name__ == '__main__':
    import metadataReader
    filename = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'
    metadatadict = metadataReader.metadataGrabber(filename)
    #print(metadatadict)
    print(metadatadict['Exif.Photo.FocalPlaneXResolution'])
    print(metadatadict['Exif.Photo.FocalPlaneYResolution'])
    print(metadatadict['Exif.Photo.FocalPlaneResolutionUnit'])
    print(metadatadict['Exif.Photo.FocalLength'])
    
    #print(metadatadict['Exif.Photo.SubSecTime'])
    #print(metadatadict['Exif.Image.DateTime'])
    #print(metadatadict['Exif.Image.BitsPerSample'])
    #print(metadatadict['Exif.Image.DateTime'])
    #print(metadatadict['Exif.GPSInfo.GPSAltitude'])
    #print(metadatadict['Exif.GPSInfo.GPSLongitude'])
    #print(metadatadict['Exif.GPSInfo.GPSLatitude'])
    #longitude = metadatadict['Exif.GPSInfo.GPSLongitude']
    #longitude = longitude[0] + longitude[1]/60 + longitude[2]/3600
    #print(longitude)
    #print(metadatadict['Exif.Photo.DateTimeDigitized'])
    #print(metadatadict['Xmp.DLS.TimeStamp'])
