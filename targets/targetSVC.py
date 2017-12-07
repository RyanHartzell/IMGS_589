"FINDS ALL OF THE SVC DATASETS"

import glob
from operator import add
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from svcReader import svcGrabber
from ROIExtraction import fieldData
from ROIExtraction import bestSVC
from ROIExtraction import targetStrtoNum
from ROIExtraction import targetNumtoStr


svcSIG = glob.glob('/cis/otherstu/gvs6104/DIRS/**/*.sig', recursive=True)
tsvList = glob.glob('/cis/otherstu/gvs6104/DIRS/**/Flight_Notes.tsv', recursive=True)

target0 = ["Just for indexing"]
target1 = [[],[],[]]
target2 = [[],[],[]]
target3 = [[],[],[]]
target4 = [[],[],[]]
target5 = [[],[],[]]
target6 = [[],[],[]]
target7 = [[],[],[]]
target8 = [[],[],[]]
target9 = [[],[],[]]
target10 = [[],[],[]]
target11 = [[],[],[]]
target12 = [[],[],[]]
target13 = [[],[],[]]
target14 = [[],[],[]]
target15 = [[],[],[]]
target16 = [[],[],[]]
target17 = [[],[],[]]
target18 = [[],[],[]]

targets = [target0, target1, target2, target3, target4, target5, target6, target7,
            target8, target9, target10, target11, target12, target13, target14,
            target15, target16, target17, target18]
dayAverage = False

for tsvFile in tsvList:
    day = (tsvFile.split('/'))[5]
    times, fileNumbers, targetDescriptor = fieldData(tsvFile)
    for r in range(len(times)):
        if "Bad" not in targetDescriptor[r] and "Ref" not in targetDescriptor[r] \
            and "Target" not in targetDescriptor[r] and "BAD" not in targetDescriptor[r]\
            and "Unknown" not in targetDescriptor[r]:

            if targetDescriptor[r] == "White Cal Panel (Shaded)":
                targetDescriptor[r] = "White Cal Panel (Shadow)"
            if targetDescriptor[r] == "Black Cal Panel (Shaded)":
                targetDescriptor[r] = "Black Cal Panel (Shadow)"
            #elif targetDescriptor[r] == "Concrete Dark":
            #    targetDescriptor[r] = "Concrete"
            #elif targetDescriptor[r] == "Concrete Medium":
            #    targetDescriptor[r] = "Concrete"
            #elif targetDescriptor[r] == "Concrete Light":
            #    targetDescriptor[r] = "Concrete"
            elif targetDescriptor[r] == "Asphalt (Dark)":
                targetDescriptor[r] = "Asphalt"
            elif targetDescriptor[r] == "Asphalt (Light)":
                targetDescriptor[r] = "Asphalt"

            targetNumber = targetStrtoNum(targetDescriptor[r])
            if targetNumber != None:
                cT = str(fileNumbers[r]).zfill(3)
                svcFile = '/'.join((tsvFile.split('/'))[:6])
                svcFile = glob.glob(svcFile + '/SVC/*_T' + cT + '.sig')
                wL, reF, tgT, sR = svcGrabber(svcFile[0])
                if day == '20171102':
                    targets[targetNumber][0].append(sR/100)
                elif day == '20171108':
                    targets[targetNumber][1].append(sR/100)
                elif day == '20171109':
                    targets[targetNumber][2].append(sR/100)

if dayAverage:
    for i in range(1, len(targets)):
        for d in range(2):
            #dayMeasure = len(targets[i][d])
            targets[i][d] = [sum(e)/len(e) for e in zip(*targets[i][d])]

blue_patch = mpatches.Patch(color='blue', label='November 2, 2017')
green_patch = mpatches.Patch(color='green', label='November 8, 2017')
red_patch = mpatches.Patch(color='red', label='November 9, 2017')

for i in range(1,len(targets)):
    plt.figure(i)
    plt.title("Target {0}".format(targetNumtoStr(str(i))))
    for t in range(len(targets[i][0])):
        plt.plot(wL, targets[i][0][t], 'b')
    for t in range(len(targets[i][1])):
        plt.plot(wL, targets[i][1][t], 'g')
    for t in range(len(targets[i][2])):
        plt.plot(wL, targets[i][2][t], 'r')
    plt.xlim(350,1100)
    plt.ylim(0,1)
    plt.legend(handles=[blue_patch,green_patch,red_patch])
    plt.xlabel("Wavelength [nm]")
    plt.ylabel("Normalized Reflectance")
plt.show()
