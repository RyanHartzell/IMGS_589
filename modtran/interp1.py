import numpy
import scipy.interpolate

def interp1(x, y, xp, order=1, extrapolate=False):
   """
   title::
      interp1

   description::
      This method will compute linear interpolants (and extrapolants if
      desired) for a provided set of locations.  This method wraps the
      scipy.interpolate.splrep and scipy.interpolate.splev B-spline
      interpolation routines into a more compact (but more limited)
      calling syntax.

   attributes::
      x, y
         Array-like objects defining the sampled function y = f(x)
      xp
         A scalar or an array-like object defining the locations to
         interpolate/extrapolate at
      order
         The order of the B-splines to use to fit the original function
         [default is 1 (linear interpolation/extrapolation)]
      extrapolate
         A boolean indicating whether extrapolation should be carried
         out, if not desired, NaN will be returned corresponding to the
         locations that fall outside the original data range along the
         horizontal axis [default is False]

   returns::
      A scalar or array-like object (matching the object type for y)
      containing the interpolant(s)/extrapolant(s)

   author::
      Carl Salvaggio

   copyright::
      Copyright (C) 2015, Rochester Institute of Technology

   license::
      GPL

   version::
      1.0.0

   disclaimer::
      This source code is provided "as is" and without warranties as to
      performance or merchantability. The author and/or distributors of
      this source code may have made statements about this source code.
      Any such statements do not constitute warranties and shall not be
      relied on by the user in deciding whether to use this source code.

      This source code is provided without any express or implied warranties
      whatsoever. Because of the diversity of conditions and hardware under
      which this source code may be used, no warranty of fitness for a
      particular purpose is offered. The user is advised to test the source
      code thoroughly before relying on it. The user must assume the entire
      risk of using the source code.
   """

   # Make sure that the provided data set consists of numpy ndarrays, if
   # not, convert them for use within the scope of this method
   if type(x).__module__ != numpy.__name__:
      xN = numpy.asarray(x, dtype=float)
   else:
      xN = x

   if type(y).__module__ != numpy.__name__:
      yN = numpy.asarray(y, dtype=float)
   else:
      yN = y

   # Make sure the elements of the provided data set are the same length
   if xN.size != yN.size:
      raise ValueError('Provided datasets must have the same size')

   # Compute the vector of knots and the B-spline coefficients for the
   # provided data
   tck = scipy.interpolate.splrep(xN, yN, k=order, s=0)

   # Given the knots and B-spline coefficients, evaluate the ordinate
   # value(s) of the spline at the provided abscissa location(s)
   yp = scipy.interpolate.splev(xp, tck)

   # If extrapolation is not desired, return NaN for abscissa value(s)
   # outside the range of the original data provided
   if extrapolate is False:
      index = numpy.where(xp < xN[0])
      if len(index[0]) > 0:
         yp[index[0]] = float('NaN')

      index = numpy.where(xp > xN[-1])
      if len(index[0]) > 0:
         yp[index[0]] = float('NaN')

   # Return the interpolated/extrapolated ordinate value(s) using the same
   # array-like structure as the provided data
   if type(y).__module__ != numpy.__name__:
      return yp.tolist()
   else:
      return yp


if __name__ == '__main__':

   #import numerical.interpolate
   from interp1 import interp1
   import numpy
   import time

   #x = [1, 2, 3, 4, 5]
   #y = [12, 16, 31, 10, 6]

   #xp = [0, 0.5, 1.5, 5.5, 6]
   fsp = 'FullSpectralResponse.csv'
   array = numpy.genfromtxt(fsp, delimiter=',',skip_header=1)
   sRWl = array[:,0]
   cols = array[:,12:17]
   #print(cols)


   specAlb = 'spec_alb.dat'
   #array = numpy.genfromtxt(specAlb, delimiter = '   ', skip_header=77)
   #print(array[0])
   specDict = {}
   headderLine = 76
   with open(specAlb) as f:
       lineCount = 0
       wLSpec = []
       for line in f:
           lineCount += 1
           if lineCount < headderLine:
               continue

           #splitted = line.lstrip().split('   ')
           splitted = line.lstrip().split()

           try:
               des = str(' '.join(splitted[1:]))
               if '!' in des:
                   des1 = des.split('!')
                   des = des1[0].rstrip()
               if '\n' in des:
                   des = des.rstrip('\n')
               split2 = True
           except:
               split2 = False

           if splitted[0].isdigit() and split2:
               currentKey = (int(splitted[0]), des)
               specDict[currentKey] = None

           try:
               wL = float(splitted[0])
               sP = float(splitted[1])
               wLSpec.append([wL,sP])
           except:
               specDict[currentKey] = numpy.asarray(wLSpec)
               wLSpec = []

   target = 'healthy grass'
   #specKey = [k for k in specDict.keys() if target in k][0]
   specArray = [v for k,v in specDict.items() if target in k][0]
   wL, sP = specArray[:,0], specArray[:,1]

   x = sRWl
   xp = wL

   interpSR = []
   for col in range(len(cols[0])):
       y = cols[:,col]
       yp = interp1(x, y, xp, extrapolate=True)
       interpSR.append([xp, yp])

   print('x = {0}'.format(x))
   print('y = {0}'.format(y))
   print('xp = {0}'.format(xp))
   print('yp = {0}'.format(yp))
