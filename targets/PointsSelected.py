import cv2

_x = []
_y = []
_verbose = False

class PointsSelected(object):

   def __init__(self, windowName, verbose=False):
      global _verbose
      self._windowName = windowName
      _verbose = verbose
      #cv.SetMouseCallback(self._windowName, self._on_mouse, 0)
      cv2.setMouseCallback(self._windowName, self._on_mouse, 0)

   @property
   def windowName(self):
      return self._windowName

   @windowName.setter
   def windowName(self, windowName):
      self._windowName = windowName
      #cv.SetMouseCallback(self._windowName, self._on_mouse, 0)
      cv2.setMouseCallback(self._windowName, self._on_mouse, 0)

   @property
   def verbose(self):
      global _verbose
      return _verbose

   @verbose.setter
   def verbose(self, verbose):
      global _verbose
      _verbose = verbose

   @staticmethod
   def x():
      global _x
      return _x

   @staticmethod
   def y():
      global _y
      return _y

   @staticmethod
   def number():
      global _x
      return len(_x)

   @staticmethod
   def restrict_len(bound):
       global _x
       global _y
       _x = _x[:bound]
       _y = _y[:bound]

   @staticmethod
   def _on_mouse(event, currentX, currentY, flags, params):
      global _x
      global _y
      global _verbose
      #if event == cv.CV_EVENT_LBUTTONDOWN:
      if event == cv2.EVENT_LBUTTONDOWN:
         if _verbose:
            #print '(x,y) = (%d,%d)' % (currentX, currentY)
            print('(x,y) = (%d,%d)' % (currentX, currentY))
         _x.append(currentX)
         _y.append(currentY)

   @staticmethod
   def clearPoints():
      global _x
      global _y
      _x = []
      _y = []
