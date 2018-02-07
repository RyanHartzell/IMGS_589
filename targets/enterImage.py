
def enterImage(windowName, scaleFactor):
    import PointsSelected
    import cv2
    import numpy as np

    r = PointsSelected.PointsSelected(windowName)
    point = None
    acceptable = [ord('w'), ord('a'), ord('d'), ord('r'), ord('t'), ord(' '), 27]
    while True:
        resp = cv2.waitKey(10)
        if r.number(r) > 0:
            resp = ord('w')
            point = list(r.points(r)[0])
            for p in range(len(point)):
                point[p] = np.around(point[p]/scaleFactor).astype(int)

        elif r.rclick(r) is True:
            resp = ord('d')

        if resp in acceptable:
            break

    return resp, point


if __name__ == "__main__":
    import cv2

    imagePath = "/cis/otherstu/gvs6104/src/python/examples/data/lenna.tif"
    img = cv2.imread(imagePath, cv2.IMREAD_UNCHANGED)
    windowName = "Example"
    cv2.namedWindow(windowName, 1)
    cv2.imshow(windowName, img)
    resp, point = enterImage(windowName)
    print(resp, point)
