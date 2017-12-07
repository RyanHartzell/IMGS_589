'https://git.gnome.org/browse/gexiv2/tree/GExiv2.py'
"""
0 Exif.GPSInfo.GPSAltitude 272152000/1000000
1 Exif.GPSInfo.GPSAltitudeRef 0
2 Exif.GPSInfo.GPSDOP 1410000/1000000
3 Exif.GPSInfo.GPSLatitude 42000000/1000000 52000000/1000000 26928120/1000000
4 Exif.GPSInfo.GPSLatitudeRef N
5 Exif.GPSInfo.GPSLongitude 77000000/1000000 1000000/1000000 39963000/1000000
6 Exif.GPSInfo.GPSLongitudeRef W
7 Exif.GPSInfo.GPSVersionID 2 2 0 0
8 Exif.Image.0xbb94 1 1 1 7 0 0 1 4 1 48022 21 0 2 48022 21 21 3 48021 1 0 4 48022 16 42 5 48021 8 1 6 48021 2 9
9 Exif.Image.0xbb95 189.466033935547 0.715373873710632 121456 475 20 0.101000003516674 130 16 2781 120 0
10 Exif.Image.0xbb96 euRDiVz2THP0zQ7DaNyo|ntSQ5rGwEzn4lkZ6smUy|DL03-1711272-SC|
11 Exif.Image.BitsPerSample 16
12 Exif.Image.BlackLevel 4800 4800 4800 4800
13 Exif.Image.BlackLevelRepeatDim 2 2
14 Exif.Image.DateTime 2017:07:26 16:12:57
15 Exif.Image.ExifTag 2457704
16 Exif.Image.GPSTag 2457942
17 Exif.Image.ImageLength 960
18 Exif.Image.ImageWidth 1280
19 Exif.Image.Make MicaSense
20 Exif.Image.Model RedEdge
21 Exif.Image.NewSubfileType 0
22 Exif.Image.OpcodeList3 0 0 0 1 77 12 198 137
23 Exif.Image.Orientation 1
24 Exif.Image.PhotometricInterpretation 1
25 Exif.Image.PlanarConfiguration 1
26 Exif.Image.RowsPerStrip 100
27 Exif.Image.SamplesPerPixel 1
28 Exif.Image.Software v2.0.5
29 Exif.Image.StripByteCounts 256000 256000 256000
30 Exif.Image.StripOffsets 8 256008 512008 768008 1024008 1280008 1536008 1792008 2048008 2304008
31 Exif.Image.XMLPacket 32 32 32 32 32 32 32 32 32 32 32 32
32 Exif.Photo.BodySerialNumber 1713165
33 Exif.Photo.DateTimeDigitized 2017:07:26 16:12:57
34 Exif.Photo.DateTimeOriginal 2017:07:26 16:12:57
35 Exif.Photo.ExifVersion 48 50 51 48
36 Exif.Photo.ExposureProgram 2
37 Exif.Photo.ExposureTime 1350/1000000
38 Exif.Photo.FNumber 2800000/1000000
39 Exif.Photo.FocalLength 5500000/1000000
40 Exif.Photo.FocalPlaneResolutionUnit 4
41 Exif.Photo.FocalPlaneXResolution 266666667/1000000
42 Exif.Photo.FocalPlaneYResolution 266666667/1000000
43 Exif.Photo.ISOSpeed 100
44 Exif.Photo.MeteringMode 1
45 Exif.Photo.SubSecTime -279654
46 Xmp.Camera.BandName Blue
47 Xmp.Camera.BandSensitivity 1702040981.6335442
48 Xmp.Camera.CentralWavelength 475
49 Xmp.Camera.Irradiance 0.71537387371063232
50 Xmp.Camera.IrradianceExposureTime 0.10100000351667404
51 Xmp.Camera.IrradianceGain 16
52 Xmp.Camera.IrradiancePitch -2.0375641618928038
53 Xmp.Camera.IrradianceRoll -0.30438037845010268
54 Xmp.Camera.IrradianceYaw -157.14660934524608
55 Xmp.Camera.RigCameraIndex 0
56 Xmp.Camera.WavelengthFWHM 20
57 Xmp.DLS.Bandwidth 20
58 Xmp.DLS.CenterWavelength 475
59 Xmp.DLS.Exposure 0.10100000351667404
60 Xmp.DLS.Gain 16
61 Xmp.DLS.OffMeasurement 2781
62 Xmp.DLS.Pitch -0.035562203345668203
63 Xmp.DLS.RawMeasurement 130
64 Xmp.DLS.Roll -0.0053124397824206868
65 Xmp.DLS.SensorId 0
66 Xmp.DLS.Serial DL03-1711272-SC
67 Xmp.DLS.SpectralIrradiance 0.71537387371063232
68 Xmp.DLS.SwVersion v0.3.32
69 Xmp.DLS.TimeStamp 121456
70 Xmp.DLS.Yaw -2.7427257414198345
71 Xmp.MicaSense.BootTimestamp 120
72 Xmp.MicaSense.CaptureId euRDiVz2THP0zQ7DaNyo
73 Xmp.MicaSense.DarkRowValue 4919, 4921, 4918, 4915
74 Xmp.MicaSense.FlightId ntSQ5rGwEzn4lkZ6smUy
75 Xmp.MicaSense.PressureAlt 189.46603393554688
76 Xmp.MicaSense.TriggerMethod 4
"""



import gi
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2
import collections

badSpecification = ["Exif.Image.BlackLevel","Exif.Image.BlackLevelRepeatDim",
"Exif.Image.Software","Exif.Image.StripByteCounts","Exif.Image.StripOffsets","Exif.Photo.ExifVersion",
"Xmp.Camera.PerspectiveDistortion","Xmp.Camera.PrincipalPoint","Xmp.Camera.VignettingCenter",
"Xmp.Camera.VignettingPolynomial","Xmp.DLS.Serial","Xmp.DLS.SwVersion","Xmp.MicaSense.CaptureId",
"Xmp.MicaSense.DarkRowValue","Xmp.MicaSense.FlightId","Xmp.MicaSense.RadiometricCalibration"]

skipSpecification = ["Exif.Image.0xbb94","Exif.Image.0xbb95","Exif.Image.0xbb96",
    "Exif.Image.NewSubfileType","Exif.Image.OpcodeList3","Exif.Image.XMLPacket",]

slashSplitSpecification = ["Exif.GPSInfo.GPSAltitude","Exif.GPSInfo.GPSDOP",
"Exif.Photo.ExposureTime",
"Exif.Photo.FNumber","Exif.Photo.FocalLength","Exif.Photo.FocalPlaneXResolution",
"Exif.Photo.FocalPlaneYResolution",]

floatSpecification = ["Exif.GPSInfo.GPSAltitudeRef","Exif.Image.BitsPerSample",
"Exif.Image.ExifTag","Exif.Image.GPSTag","Exif.Image.ImageLength","Exif.Image.ImageWidth",
"Exif.Image.Orientation","Exif.Image.PhotometricInterpretation",
"Exif.Image.PlanarConfiguration","Exif.Image.RowsPerStrip","Exif.Image.SamplesPerPixel",
"Exif.Photo.BodySerialNumber","Exif.Photo.ExposureProgram",
"Exif.Photo.FocalPlaneResolutionUnit","Exif.Photo.ISOSpeed","Exif.Photo.MeteringMode",
"Xmp.Camera.BandSensitivity","Xmp.Camera.CentralWavelength","Xmp.Camera.Irradiance",
"Xmp.Camera.IrradianceExposureTime","Xmp.Camera.IrradianceGain","Xmp.Camera.IrradiancePitch",
"Xmp.Camera.IrradianceRoll","Xmp.Camera.IrradianceYaw","Xmp.Camera.PerspectiveFocalLength",
"Xmp.Camera.RigCameraIndex","Xmp.Camera.WavelengthFWHM","Xmp.DLS.Bandwidth",
"Xmp.DLS.CenterWavelength","Xmp.DLS.Exposure","Xmp.DLS.Gain","Xmp.DLS.OffMeasurement",
"Xmp.DLS.Pitch","Xmp.DLS.RawMeasurement","Xmp.DLS.Roll","Xmp.DLS.SensorId",
"Xmp.DLS.SpectralIrradiance","Xmp.DLS.Yaw","Xmp.MicaSense.BootTimestamp",
"Xmp.MicaSense.PressureAlt","Xmp.MicaSense.TriggerMethod"]

dateTimeSpecification = ["Exif.Image.DateTime","Exif.Photo.DateTimeDigitized",
"Exif.Photo.DateTimeOriginal","Exif.Photo.SubSecTime","Xmp.DLS.TimeStamp"]

def metadataGrabber(filename, RAW=False):
    #sampleimage = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'

    imagemetadata = GExiv2.Metadata(filename)
    #print(imagemetadata, type(imagemetadata))
    #print(imagemetadata.sort())
    taglist = imagemetadata.get_tags()
    #print(taglist)

    indexlist = (0,3,5,11,14,17,18,19,20,27,33,34,35,36,37,38,39,41,42,43,45,46,47,48,49,50,51,52,53,54,56,69)
    metadatadict = {}
    for index in range(len(taglist)):
        specification = taglist[index]
        entry = imagemetadata.get(specification)
        #print(index, specification, entry)

        if specification == "Exif.Image.0xa480":
            continue
        if specification in skipSpecification:
            continue
        if specification in badSpecification:
            continue
        if specification in slashSplitSpecification:
            #print(entry)
            numerator, denominator = entry.split('/')
            entry = float(numerator)/float(denominator)

        if specification in floatSpecification:
            try:
                entry = float(entry)
            except:
                pass

        if specification == 'Exif.GPSInfo.GPSLatitude' or specification == 'Exif.GPSInfo.GPSLongitude':
            gps = entry.split()
            dms = 0
            for i in range(len(gps)):
                numerator, denominator = gps[i].split('/')
                value = float(numerator)/float(denominator)
                if i == 1:
                    value /= 60
                if i == 2:
                    value /= (60*60)
                dms += value
            entry = dms

            #Single Fractions to Float Case
            # if index in ( 0,37,38,39,41,42):
            #     split = entry.index('/')
            #     entry = float(entry[:split])/float(entry[split+1:])
            #
            # #Three Fractions to Floats Case for GPS Coordinates
            # elif index in (3,5):
            #     firstsplit = entry.index('/')
            #     secondsplit = entry.index('/',firstsplit+1)
            #     thirdsplit = entry.index('/',secondsplit+1)
            #     firstspace = entry.index(' ')
            #     secondspace = entry.index(' ',firstspace+1)
            #
            #     divisor = float(entry[firstsplit+1:firstspace])
            #     degrees = float(entry[:firstsplit])/divisor
            #     minutes = float(entry[firstspace+1:secondsplit])/divisor
            #     seconds = float(entry[secondspace+1:thirdsplit])/divisor
            #
            #     entry = (degrees,minutes,seconds)
            #
            # #String to string case for names,date,time
            # elif index in (4,6,14,19,20,34,45,46,66,68,69,72,73,74):
            #     #print(index, specification, entry)
            #     pass
            # elif index in (2,7,8,9,10,12,13,22,28,29,30,31,33,35):
            #     #These Suck
            #     #print(index, specification, entry)
            #     continue
            # elif specification == "Xmp.Camera.PerspectiveDistortion":
            #     pass
            # elif specification == "Xmp.Camera.ModelType":
            #     pass
            # elif specification == "Xmp.Camera.PrincipalPoint":
            #     pass
            # elif specification == "Xmp.Camera.VignettingCenter":
            #     pass
            # elif specification == "Xmp.Camera.VignettingPolynomial":
            #     pass
            # elif specification == "Xmp.MicaSense.CaptureId":
            #     pass
            # elif specification == "Xmp.MicaSense.DarkRowValue":
            #     pass
            # elif specification == "Xmp.MicaSense.FlightId":
            #     pass
            # elif specification == "Xmp.MicaSense.RadiometricCalibration":
            #     pass

            #All other cases, no integers used for ease later
            #else:
                #try:
                #    entry = float(entry)
                #except:
                #    pass

        metadatadict[specification] = entry

    dateTime = metadatadict['Exif.Photo.DateTimeOriginal']
    dateTime = dateTime.replace(' ', 'T')
    dateTime = dateTime.replace(':','-',2)
    subSec = metadatadict['Exif.Photo.SubSecTime']
    #print(subSec, type(subSec))
    timeStamp = dateTime# + '.' + subSec[1:]
    metadatadict['timeStamp'] = timeStamp

    return metadatadict

if __name__ == '__main__':
    import metadataReader
    filename = '/dirs/home/faculty/cnspci/micasense/rededge/20170726/0005SET/raw/000/IMG_0000_1.tif'
    filename = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1400/micasense/geoTiff/IMG_0272.tiff'
    metadatadict = metadataReader.metadataGrabber(filename)

    import time
    print(metadatadict['Xmp.DLS.TimeStamp'], type(metadatadict['Xmp.DLS.TimeStamp']) )
    print(metadatadict['timeStamp'], type(metadatadict['timeStamp']))
    print(metadatadict['timeStamp'][-8:])
    t = time.strptime(metadatadict['timeStamp'][-8:],'%H:%M:%S')

    minutes = (t.tm_hour - 5) * 60 + t.tm_min

    #print(metadatadict)
    #print(metadatadict)
    #print(metadatadict['Exif.Photo.FocalPlaneXResolution'])
    #print(metadatadict['Exif.Photo.FocalPlaneYResolution'])
    #print(metadatadict['Exif.Photo.FocalPlaneResolutionUnit'])
    #print(metadatadict['Exif.Photo.FocalLength'])

    #print(metadatadict['Exif.Photo.DateTimeOriginal'])
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
