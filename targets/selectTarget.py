
def displayTextImage(windowName, image, text, position=None, color=None):
    import cv2
    import numpy as np

    textIm = image.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    if position is None:
        position = (image.shape[1]//2, image.shape[0]//2)
    if color is None:
        maxCount = np.max(image)
        color = (0, .65*maxCount, maxCount)

    cv2.putText(textIm, text, position, font, 2, color, 4, cv2.LINE_AA)
    cv2.imshow(windowName, textIm)
    #cv2.imshow("Text Image", textIm)

def getNumber(validDict=None, confirmList=None, startNumber=None):
    import sys
    import cv2

    if confirmList is None:
        confirmList = [32,10,141] #ASKII Space, Return, Enter
    #denyList = [8, 255, 110] #ASKII Backspace, Delete, N

    #If the user does not input a dictionary then use default dictionary
    if validDict is None:
        validDict = {ord('0'):0, ord('1'):1,ord('2'):2, ord('3'):3, ord('4'):4,
                    ord('5'):5, ord('6'):6, ord('7'):7, ord('8'):8, ord('9'):9,
                    27:27, 176:0, 177:1, 178:2, 179:3, 180:4, 181:5, 182:6,
                    183:7, 184:8, 185:9}

    number = False
    if startNumber is not None and startNumber in validDict.keys():
        number = validDict[startNumber]

    while number is False:
        response = cv2.waitKey(10)
        #if response > 0:
            #print(response)
        if response in validDict.keys():
            number = validDict[response]
        if response == 8:
            break
        if response == 27:
            sys.exit(0)
        if response in confirmList:
            number = True

    return number

def chooseNumber(windowName, image, startNumber=None, confirm=False, text="",
                    validDict=None, confirmList=None, position=None, color=None):
    from selectTarget import getNumber
    from selectTarget import displayTextImage

    if startNumber == 27:
        sts.exit(0)

    if confirm is True or startNumber == ord('n'):
        return text.lstrip("0")
    else:
        displayTextImage(windowName,image,text,position,color)
        if startNumber is not None:
            number = getNumber(validDict, confirmList, startNumber)
            startNumber=None
        else:
            number = getNumber(validDict,confirmList)
        if number is True:
            confirm = True
        elif type(number) is int:
            text += str(number)
            displayTextImage(windowName, image,text)
        elif number is False:
            if len(text) > 0:
                text = text[:len(text)-1]


        return chooseNumber(windowName, image,startNumber, confirm, text)

if __name__ == "__main__":
    import cv2
    import numpy as np
    from osgeo import gdal

    geotiffFilename = '/research/imgs589/imageLibrary/DIRS/20171109/Missions/1345_375ft/micasense/geoTiff/IMG_0020.tiff'

    imageStack = gdal.Open(geotiffFilename).ReadAsArray()
    imageStack = np.moveaxis(imageStack, 0, -1)
    #imageStack = imageStack/np.max(imageStack)
    rgb = imageStack[:,:,:3]
    rgb = rgb/np.max(rgb)
    scaleFactor = .5
    rgb = cv2.resize(rgb, None,
			fx=scaleFactor, fy=scaleFactor,interpolation=cv2.INTER_AREA)
    mapName = "Test Image"

    tgtNum = chooseNumber(mapName, rgb)
    print(tgtNum)
