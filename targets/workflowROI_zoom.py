


import cv2
import os
import numpy as np
from osgeo import gdal
import regionGrow
from ROIExtraction import *
import sys
sys.path.append("..")
import geoTIFF
import glob
import csv
import argparse
import getpass
from enterImage import enterImage
import tkinter
from tkinter import filedialog, ttk
root = tkinter.Tk()
root.withdraw()
root.update()
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
#print(screenWidth, screenHeight)
userName = getpass.getuser()



#example:
#python3 workflowROI.py -g /cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/ -t /cis/otherstu/gvs6104/DIRS/20171102/GroundDocumentation/datasheets/Flight_Notes.tsv -s 2 -f IMG_0180.tiff
#python3 workflowROI_zoom.py -g /research/imgs589/imageLibrary/DIRS/20171109/Missions/1230_150ft/micasense/geoTiff/ -t /research/imgs589/imageLibrary/DIRS/20171109/GroundDocumentation/datasheets/Flight_Notes.tsv -s 2 -f IMG_0000.tiff

# individual example inputs
# geotiffFolderName = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/1445/micasense/geoTiff/'
# tsvFilename = '/cis/otherstu/gvs6104/DIRS/20171102/GroundDocumentation/datasheets/Flight_Notes.tsv'
# #txtDestination = '/cis/otherstu/gvs6104/DIRS/20171102/Missions/Flight1445_' + userName + '.csv'
# stepNumber = 2 #do every other image, or every image, ...

# startFrameNumber = 0 #can equal int or filename as string
# startFrameNumber = 'IMG_0000.tiff'
# ##


parser = argparse.ArgumentParser(description='Collect user inputs for ROI extraction process')
parser.add_argument('-g', '--geotiffFolderName', type=str, help='The geotiff image directory')
parser.add_argument('-t', '--tsvFilename', type=str, help='The filename with the .tsv')
parser.add_argument('-s', '--stepNumber', type=int, help='How many images you want to skip')
parser.add_argument('-r', '--scaleFactor', type=float, help='How much would you like to resize the images by for viewing default: 2')
parser.add_argument('-a', '--angle', type=float, help='The angle away from nadir to crop the images to')
parser.add_argument('-f', '--startFrameNumber', help='Image to start at, can be string or index (int)')

args = parser.parse_args()
geotiffFolderName = args.geotiffFolderName
tsvFilename = args.tsvFilename
stepNumber = args.stepNumber
startFrameNumber = args.startFrameNumber
scaleFactor = args.scaleFactor
angle = args.angle

if geotiffFolderName is None:
    geotiffFolderName = filedialog.askdirectory(initialdir = "/research/imgs589/imageLibrary/DIRS/",
                                            title="Choose the geotiff image directory")
    if geotiffFolderName == "":
        sys.exit()
    else:
        geotiffFolderName = geotiffFolderName + os.path.sep

splitted = geotiffFolderName.split('/')
if tsvFilename is None:
    tsvDirectory = '/'.join(splitted[:6]) + os.path.sep + 'GroundDocumentation/datasheets/'
    if os.path.isfile(tsvDirectory + 'Flight_Notes.tsv'):
        tsvFilename = tsvDirectory + 'Flight_Notes.tsv'
    else:
        tsvFilename = filedialog.askopenfilename(initialdir = tsvDirectory, title="Choose the Flight Notes [.tsv]",
            filetypes=[("Tab Seperated Values", "*.tsv"), ("Comma Seperated Values", "*.csv"),("Excel Files", "*.xlsx *.xls")])
        if tsvFilename == "":
            sys.exit()

sampleImageDirectory = '/'.join(splitted[:6]) + os.path.sep + 'GroundDocumentation/images/'
sampleImage = sorted(glob.glob(sampleImageDirectory+'TargetNumbers*'))
if len(sampleImage) > 0:
    targetImage = cv2.imread(sampleImage[0], cv2.IMREAD_UNCHANGED)
    targetImage = cv2.resize(targetImage, None,
            fx=.75, fy=.75,interpolation=cv2.INTER_AREA)
    cv2.imshow("Sample Image", targetImage)


if stepNumber is None:
    stepNumber = 2
    #stepNumber = int(input('Type number for how many images you want to skip \n'))
if scaleFactor is None:
    scaleFactor = 1.5
if angle is None:
    angle = 20

if startFrameNumber is None:
    startFrameNumber = input('Type number (index) or filename (string) for which image to start at \n')
    try:
        startFrameNumber = int(startFrameNumber) #this will only work (convert to int) if it is an index
    except Exception:
        pass

flightNumber = os.path.basename(os.path.abspath(os.path.join(geotiffFolderName, '../..')))
flightDate = os.path.basename(os.path.abspath(os.path.join(geotiffFolderName, '../../../..')))
flightInfo = 'Flight_' + flightDate + 'T' + flightNumber + '_'
txtDestination = os.path.abspath(os.path.join(geotiffFolderName, os.pardir)) + os.path.sep + flightInfo + userName + '.csv'

# Get all filenames within this fliinterght directory
#fileNames = sorted(os.listdir(geotiffFolderName)) #Does not handle files that arn't *.tiff
listofFiles = sorted(glob.glob(geotiffFolderName + "*.tiff"))
fileNames = []
for name in listofFiles:
    fileNames.append(os.path.basename(name))

imageCount = len(fileNames)
imageNameDict = dict(enumerate(fileNames))
imageNameDict = {v:k for k,v in imageNameDict.items()}

try:
    startFrameNumber= int(startFrameNumber)
    if startFrameNumber > imageCount:
        startFrameNumber = 0
except Exception as e:
    pass

if type(startFrameNumber) == str:
    try:
        startFrameNumber = int(imageNameDict[startFrameNumber])
    except:
        startFrameNumber = 0

##Create windows outside of loop so they aren't constantly being deleted/created


#zoomName = 'Zoomed region for easier point selection.'
#cv2.namedWindow(zoomName, cv2.WINDOW_AUTOSIZE)
#zoom = cv2.imshow(zoomName, np.zeros((200,200)))

## Data to be read in once-per-flight
times,targets,targetdescriptor = fieldData(tsvFilename)
currentIm_tag = 'Current Geotiff'
cv2.namedWindow(currentIm_tag, cv2.WINDOW_AUTOSIZE) #resize and display the image

##Create the textfile that the data will be written out to
if os.path.isfile(txtDestination) == True:
    writeMode = 'a'
else:
    writeMode = 'w'

with open(txtDestination, writeMode) as currentTextFile:
    writer = csv.writer(currentTextFile, delimiter = ',')
    if writeMode == 'w':
        writer.writerow(['Target Number', 'Frame Number(s) [geoTiff]', 'ELM/Profile',
        'Pixel Resolution', 'Flight Altitude', 'Mean B', 'Mean G', 'Mean R', 'Mean RE',
         'Mean IR', 'Std B', 'Std G', 'Std R', 'Std RE', 'Std IR', 'Irradiance B',
         'Irradiance G', 'Irradiance R','Irradiance RE', 'Irradiance IR',
         'Centroid Coord X', 'Centroid Coord Y','Point X1','Point X2','Point X3','Point X4',
         'Point Y1','Point Y2','Point Y3', 'Point Y4', 'Nadir Angle','SVC filenumber'])

    ##START MAIN LOOP
    currentImIndex = startFrameNumber
    centroidList = []
    while True:
        if currentImIndex == imageCount:
            print('You have reached the end of the imagery. Nice job.')
            #print('You can find the csv file at:' + txtDestination)
            break

        currentFilename = geotiffFolderName + fileNames[currentImIndex]

        currentCroppedIm, displayImage = getDisplayImage(currentFilename, angle, scaleFactor)

        if len(centroidList) > 0:
            for t in range(len(centroidList)):
                #print(centroidList[t])
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(displayImage, centroidList[t][1], centroidList[t][0],
                    font, 1, (0, 165, 255), 1, cv2.LINE_AA)

        cv2.imshow(currentIm_tag, displayImage)

        print("Do you want to get ROIs in this frame? 'w' for yes, 'a' for back, 'd' for forward.")
        print(fileNames[currentImIndex], 'Index = ', currentImIndex,'/', imageCount)

        #userInput = cv2.waitKey(0)
        userInput, point = enterImage(currentIm_tag, scaleFactor)
        if userInput == ord('w'):
            print('Ready to accept points.')
            print("Once you are done, enter target number with 2 digits [04], 'n' to redo.")
            pointsX, pointsY, currentTargetNumber = selectROI(currentIm_tag, currentCroppedIm, displayImage, point, scaleFactor)
            if pointsX is None or pointsY is None or currentTargetNumber is None:
                continue
            partCenter = [int(np.around(np.mean(pointsX))) ,int(np.around(np.mean(pointsY)))]
            centroidList.append(((partCenter[0],partCenter[1]),currentTargetNumber))

            #RESIZE DISPLAY
            pointsX_resize = []
            pointsY_resize = []
            for i in pointsX:
                newX = i/scaleFactor
                pointsX_resize.append(newX)
            for i in pointsY:
                newY = i/scaleFactor
                pointsY_resize.append(newY)
            pointsX = pointsX_resize
            pointsY = pointsY_resize

            #compute the statistics that will be written out, from the ROI coords
            maskedIm, ROI_image, mean, stdev, centroid, pointsX, pointsY = computeStats(currentCroppedIm,
                                                                           currentFilename, pointsX, pointsY)
            #get metadata
            irradianceDict, frametime, altitude, resolution= micasenseRawData(currentFilename)
            filenumber = bestSVC(frametime,currentTargetNumber,times,targets,targetdescriptor)
            #writer.writerow([currentTargetNumber, fileNames[currentImIndex], '', 'Pixel Resolution', 'Flight Altitude', str(mean[0]), str(mean[1]), str(mean[2]), str(mean[3]), str(mean[4]), str(stdev[0]), str(stdev[1]), str(stdev[2]), str(stdev[3]), str(stdev[4]), str(centroid), 'Nadir Angle'])

            #'Target Number', 'Frame Number(s) [geoTiff]',
            #'ELM/Profile', 'Pixel Resolution', 'Flight Altitude', 'Mean B', 'Mean G', 'Mean R',
            #'Mean RE', 'Mean IR', 'Std B', 'Std G', 'Std R',
            #'Std RE', 'Std IR', 'Irradiance B','Irradiance G',
            #'Irradiance R','Irradiance RE', 'Irradiance IR',
            #'Centroid Coord X', 'Centroid Coord Y','Point X1','Point X2',
            #'Point X3','Point X4','Point Y1','Point Y2',
            #'Point YIncrementWheel3', 'Points Y4', 'Nadir Angle','SVC filenumber'

            writer.writerow([currentTargetNumber, fileNames[currentImIndex],
            '', resolution, altitude, str(mean[0]), str(mean[1]), str(mean[2]),
            str(mean[3]), str(mean[4]), str(stdev[0]), str(stdev[1]), str(stdev[2]),
            str(stdev[3]), str(stdev[4]), str(irradianceDict[1]), str(irradianceDict[2]),
            str(irradianceDict[3]), str(irradianceDict[4]), str(irradianceDict[5]),
            str(centroid[0]), str(centroid[1]), str(pointsX[0]), str(pointsX[1]),
            str(pointsX[2]), str(pointsX[3]), str(pointsY[0]), str(pointsY[1]),
            str(pointsY[2]), str(pointsY[3]), '', str(filenumber)])

            print('Line has been written to file.')
            #cv2.destroyWindow(currentIm_tag)

        elif userInput == ord('d') or userInput == 32:
            if currentImIndex + stepNumber > imageCount:
                stepNumber = 1
            currentImIndex += stepNumber
            centroidList =[]
        elif userInput == ord('a'):
            currentImIndex += -stepNumber
            centroidList = []
        elif userInput == ord('t'):
            newAngle = input("What is the new angle?")
            try:
                angle = float(newAngle)
            except:
                pass
        elif userInput == ord('r'):
            newScaleFactor = input("What is the new scale factor?")
            try:
                scaleFactor = float(newScaleFactor)
                centroidList = []
            except:
                pass
        elif userInput == 27:
            break
        else:
            continue

    cv2.destroyWindow(currentIm_tag)
    currentTextFile.close()
    os.chmod(txtDestination, 0o775)

    print('You can find the csv file at:' + txtDestination)
