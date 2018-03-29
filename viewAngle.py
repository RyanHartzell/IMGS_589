"""
title::
   Create detector view angle mask for sUAS imagery

description::
   Takes the dimensions (height,width) for the mask, and uses sensor parmeters (sensor pixel width, sensor mm width, focal length mm, and sensor height m) to
    calculate GSD, relate that to each location in the mask, and calclate the sensor view angles for each pixel location. 

author::
   Ryan Connal

copyright::
   Copyright (C) 2017, Rochester Institute of Technology

"""



def viewAngle(arrayHeight, arrayWidth, sensorPixWidth, sensorWidth, focalLength, sensorHeight):
   # # Image Parameters
   # arrayHeight = 960 #pix
   # arrayWidth = 1280 #pix

   # #Camera Parameters
   # sensorPixWidth = 4000 #pixels
   # sensorWidth = 4.8 #mm
   # focalLength = 5.5 #mm
   # sensorHeight = 390 #m

   import numpy as np
   import math
   import cv2


   y, x = np.indices((arrayHeight, arrayWidth))
   centered_indices_y = (y - arrayHeight//2).reshape(((arrayHeight * arrayWidth)))
   centered_indices_x = (x - arrayWidth//2).reshape(((arrayHeight * arrayWidth)))

   #setup arrays
   iterating_range = range(len(centered_indices_x))
   distance_array = np.zeros((arrayHeight, arrayWidth))
   theta_array = np.zeros((arrayHeight, arrayWidth))
   rad_array = np.zeros((arrayHeight, arrayWidth))
   detectorViewAngleArray = np.zeros((arrayHeight, arrayWidth))


   for i in iterating_range:
      x = centered_indices_x[i]
      y = centered_indices_y[i]

      #Euclidean Distance
      distance = np.sqrt((y-0)**2 + (x-0)**2)
      distance_array[y + arrayHeight//2,x + arrayWidth//2] = distance
      
      #Circular array for angles
      angle = np.degrees(math.atan2((y.astype(np.float32)), (x.astype(np.float32)))) * -1
      if angle < 0:
         angle = 360 + angle
      elif angle == -0:
          angle = 0   
      theta_array[y + arrayHeight//2,x + arrayWidth//2] = angle
      rad_array[y + arrayHeight//2,x + arrayWidth//2]  = np.radians(angle)
      
      #calculate drone view angle
      groundSampleDistance = 0.01 * ((sensorWidth*sensorHeight*100)/(focalLength*sensorPixWidth)) #m/pix
      viewAngle = np.tan((distance*groundSampleDistance) / sensorHeight) #(m/pix) * (1/m)
      detectorViewAngleArray[y + arrayHeight//2,x + arrayWidth//2] = viewAngle

   return detectorViewAngleArray
      


#PYTHON TEST HARNESS
if __name__ == '__main__':

   import numpy as np
   import math
   import cv2


   # Image Parameters
   arrayHeight = 960 #mm
   arrayWidth = 1280 #mm

   #Camera Parameters
   sensorPixWidth = 4000 #pixels
   sensorWidth = 4.8 #mm
   focalLength = 5.5 #mm
   sensorHeight = 390 #m

   viewAngleMask = viewAngle(arrayHeight, arrayWidth, sensorPixWidth, sensorWidth, focalLength, sensorHeight)
   cv2.imwrite('/cis/ugrad/rjc6465/sUAS/IMGS_589/viewAngleMask.tif', viewAngleMask)