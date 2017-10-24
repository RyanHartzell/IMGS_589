import cv2

def dimensions(im):
    dimensions = im.shape
    numberRows = dimensions[0]
    numberColumns = dimensions[1]
    if len(dimensions) == 3:
        numberChannels = dimensions[2]
    else:
        numberChannels = 1
    dataType = im.dtype
    return numberRows, numberColumns, numberChannels, dataType

if __name__ == '__main__':
    import ipcv
    import cv2 
    filename = 'lenna.tif'
    im = cv2.imread(filename,cv2.IMREAD_UNCHANGED)
    numberRows, numberColumns, numberChannels, dataType = ipcv.dimensions(im)
    print("The file, {0}, has {1} Rows, {2} Columns, {3} Channels, and is {4} Data Type.".format(filename, numberRows, numberColumns, numberChannels, dataType))
