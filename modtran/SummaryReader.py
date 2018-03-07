import csv
import os

#os.chdir('/cis/ugrad/kxk8298/src/python/modules/IMGS_589/modtran')
os.chdir('/research/imgs589/temp/')
with open('bgm6575_summary.csv', newline='') as myFile:
	reader = csv.reader(myFile)
	newFile = open('bgm6575_execsummary.csv', 'w+')
	writer = csv.writer(newFile)
	n = 0
	keys = []
	writeoutDict = {}
	for row in reader:
		if len(row) > 18:
			if n == 0:
				runParams = row
			if n == 2:
				runOutput = row
			if n % 2 == 1:
				if (n-1) % 4 == 0:
					params = row
				if (n-3) % 4 == 0:
					outputs = row
					setVals = params + outputs
					writeoutDict[n] =  setVals
					keys.append(n)
			n += 1
	newheaders = ['Modtran NDVI' , 'Blue Error', 'Green Error', 'NIR Error', 'Red Error', 'Red Edge Error', 'NDVI Error']
	headers = runParams + runOutput + newheaders
	#print(headers[40])
	#print(headers)
	#print(writeoutDict)
	writer.writerow(headers)
	for n in keys:
		lineout = writeoutDict[n]
		bluSVC = float(lineout[34])
		greSVC = float(lineout[35])
		nirSVC = float(lineout[36])
		redSVC =float(lineout[37])
		edgSVC =float(lineout[38])
		if lineout[40] != 'nan':
			#Check and grab of modtran data
			NDVIval = float(lineout[40])
			bluRef = float(lineout[41])
			greRef = float(lineout[42])
			nirRef = float(lineout[43])
			redRef = float(lineout[44])
			edgRef = float(lineout[45])
			#Calculation of values
			modNDVI = (edgRef - redRef) / (edgRef + redRef)
			bluError = abs((bluRef - bluSVC)/ bluSVC)
			greError = abs((greRef - greSVC)/ greSVC)
			nirError = abs((nirRef - nirSVC)/ nirSVC)
			redError = abs((redRef - redSVC)/ redSVC)
			edgError = abs((edgRef - edgSVC)/ edgSVC)
			NDVIError = abs((modNDVI - NDVIval)/ NDVIval)
			newdata = [str(modNDVI),str(bluError),str(greError),str(nirError),str(redError),str(edgError),str(NDVIError)]
			lineout = lineout + newdata
		writer.writerow(lineout)

