import numpy as np

def svcGrabber(filename):
    #Simple load in of spectrometer data in arrays
    data = np.loadtxt(filename,unpack = True, skiprows = 25,dtype = float)
    wavelength = data[0]
    reference = data[1]
    target = data[2]
    spectral_reflectance = data[3] #2/5/2018, this was changed from 'spectral_response' to 'spectral reflectance'. Functions below this were also adjusted
    return wavelength,reference,target,spectral_reflectance

def normal_gaussian(domain, mean, stddev, height = 1):
    gaussian = height * np.exp(-((domain-mean)/stddev)**2)
    return gaussian

def Gamma2sigma(Gamma):
    #Function to convert FWHM (Gamma) to standard deviation (sigma)
    return Gamma * np.sqrt(2) / (np.sqrt(2 * np.log(2)) * 2 )

def reflectance(wavelengths,spectral_reflectance,cameraband,FWHM):
    stddev = Gamma2sigma(FWHM)
    RSRcurve = normal_gaussian(wavelengths,cameraband,stddev)
    camera_adjusted_spectral_reflectance = spectral_reflectance * RSRcurve
    reflectance = np.sum(camera_adjusted_spectral_reflectance)/(np.max(wavelengths)-np.min(wavelengths))
    return reflectance



if __name__ == '__main__':
    import svcReader
    filename = '/research/imgs589/imageLibrary/DIRS/20171108/SVC/000000_0000_R108_T110.sig' #000000_0000_R108_T110.sig #000000_0000_R108_T111.sig
    wavelength,reference,target,spectral_reflectance = svcReader.svcGrabber(filename)

    #For Green Band
    cameraband = 560
    FWHM = 20
    print(spectral_reflectance)
    #reflectance = reflectance(wavelength,spectral_reflectance,cameraband,FWHM)

    #print(reflectance)
