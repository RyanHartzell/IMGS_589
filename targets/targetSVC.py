"FINDS ALL OF THE SVC DATASETS"

import glob
import cv2
from svcReader import svcGrabber
from ROIExtraction import fieldData
from ROIExtraction import bestSVC
from ROIExtraction import targetStrtoNum


svcSIG = glob.glob('/cis/otherstu/gvs6104/DIRS/**/*.sig', recursive=True)
tsvList = glob.glob('/cis/otherstu/gvs6104/DIRS/**/Flight_Notes.tsv', recursive=True)


for tsvFile in tsvList:
    times, fileNumbers, targetDescriptor = fieldData(tsvFile)
    for r in range(len(times)):
        if targetDescriptor[r] != "Bad" and targetDescriptor[r] != 'Ref':
            targetNumber = targetStrtoNum(targetDescriptor[r])
            if targetNumber != None:
                cT = str(fileNumbers[r]).zfill(3)
                svcFile = '/'.join((tsvFile.split('/'))[:6])
                svcFile = glob.glob(svcFile + '/SVC/*_T' + cT + '.sig')
                wL, reF, tgT, sR = svcGrabber(svcFile[0])


                cv2.waitKey(0)
