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
"""

'https://git.gnome.org/browse/gexiv2/tree/GExiv2.py'

import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2

def metadataGrabber(filename):
    sampleimage = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'

    imagemetadata = GExiv2.Metadata(sampleimage)

    taglist = imagemetadata.get_tags()

    indexlist = (0,3,5,17,18,19,20,27,33,37,38,39,41,42,43,46,47,48,49,50,51,52,53,54,56)
    metadatadict = {}

    for index in indexlist:
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
        elif index in (19,20,33,46):
            pass

        #All other cases, no integers used for ease later
        else:
            entry = float(entry)

        metadatadict[specification] = entry
    return(metadatadict)
    
if __name__ == '__main__':
    import metadataReader
    filename = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'
    metadatadict = metadataReader.metadataGrabber(filename)

    print(metadatadict['Exif.Photo.ExposureTime'])
