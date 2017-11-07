import numpy as np
import cv2
import math

# write as series of functions instead, read data in and create RSRs in class
class spectralReflectance(object):
	def __init__(self, lambdas, widths, useRSR = True):
		self.lambdas = np.asarray(lambdas)
		self.widths = np.asarray(widths)

		if useRSR == True:
			self.RSRs = self.RSR()

		self.p_calc()
		self.p_be_calc()

	def read_spectra(self):
		#read in
		#set x
		pass

	def RSR(self, x):
		# x is a linspace vector of wavelength domain and sampling
		# mu is shift to center wavelength
		# sig is full width half max???
		sig = self.widths / (2 * math.sqrt(2 * math.log(2)))
		
		gaussians = np.exp(-((x - self.lambdas) * (x - self.lambdas)) / (2 * sig * sig))

	def p_calc(self):
		pass

	def p_be_calc(self):
		for self.RSRs:
			#do stuff
			pass