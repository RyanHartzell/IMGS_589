import cv2

#_x = []
#_y = []
_verbose = False

class PointsSelected(object):

   def __init__(self, windowName, windowID=0, verbose=False):
      global _verbose
      self._windowName = windowName
      self._windowID = windowID
      _verbose = verbose
      self._x = []
      self._y = []
      self._points = []
      self._rclick = False
      self._mclick = False

      #cv.SetMouseCallback(self._windowName, self._on_mouse, 0)
      cv2.setMouseCallback(self._windowName, self.select_point, (self._windowID, self))

   @property
   def windowName(self):
      return self._windowName

   @windowName.setter
   def windowName(self, windowName):
      self._windowName = windowName
      #cv.SetMouseCallback(self._windowName, self._on_mouse, 0)
      cv2.setMouseCallback(self._windowName, self.select_point, (self._windowID, self))

   @property
   def verbose(self):
      global _verbose
      return _verbose

   @verbose.setter
   def verbose(self, verbose):
      global _verbose
      _verbose = verbose

   @staticmethod
   def x(self):
      return self._x

   @staticmethod
   def y(self):
      return self._y

   @staticmethod
   def points(self):
       return self._points

   @staticmethod
   def rclick(self):
       return self._rclick

   @staticmethod
   def resetRclick(self):
      self._rclick = False

   @staticmethod
   def mclick(self):
       return self._mclick

   @staticmethod
   def resetMclick(self):
      self._mclick = False

   @staticmethod
   def number(self):
      if len(self._x) != len(self._y):
          msg = "Length of x and y not equal!"
          raise ValueError(msg)
      return len(self._x)

   @staticmethod
   def restrict_len(self, bound):
       self._x = self._x[:bound]
       self._y = self._y[:bound]
       self._points = self._points[:bound]

   @staticmethod
   def select_point(event,currentX,currentY,flags, params):
      global _verbose
      if event == cv2.EVENT_LBUTTONDOWN:
         if _verbose:
            print('Window: %i - (x,y) = (%d,%d)' %
               (params[0], currentX, currentY))
         params[1]._points.append((currentX,currentY))
         params[1]._x.append(currentX)
         params[1]._y.append(currentY)
      elif event == cv2.EVENT_RBUTTONDOWN:
         params[1]._rclick = True
      elif event == cv2.EVENT_MBUTTONDOWN:
         params[1]._mclick = True
      #USE FOR ERROR CHECKING
      #elif event == cv2.EVENT_MOUSEMOVE:
         #print(currentX, currentY)



   @staticmethod
   def clearPoints(self):
      self._x = []
      self._y = []
      self._points = []
