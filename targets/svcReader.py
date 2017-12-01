import numpy as np

def svcGrabber(filename):
    #Simple load in of spectrometer data in arrays
    data = np.loadtxt(filename,unpack = True, skiprows = 25,dtype = float)
    wavelength = data[0]
    reference = data[1]
    target = data[2]
    spectral_response = data[3]
    return wavelength,reference,target,spectral_response

def normal_gaussian(domain, mean, stddev, height = 1):
    gaussian = height * np.exp(-((domain-mean)/stddev)**2)
    return gaussian

def Gamma2sigma(Gamma):
    #Function to convert FWHM (Gamma) to standard deviation (sigma)
    return Gamma * np.sqrt(2) / (np.sqrt(2 * np.log(2)) * 2 )

def reflectance(wavelengths,spectral_response,cameraband,FWHM):
    stddev = Gamma2sigma(FWHM)
    RSRcurve = normal_gaussian(wavelengths,cameraband,stddev)
    camera_adjusted_spectral_response = spectral_response * RSRcurve
    reflectance = np.sum(camera_adjusted_spectral_response)/(np.max(wavelengths)-np.min(wavelengths))
    return reflectance


if __name__ == '__main__':
    import svcReader
    filename = '/cis/ugrad/kxk8298/src/python/modules/IMGS_589/general_toolbox/sampledatafiles/svc_sample.sig'
    wavelength,reference,target,spectral_response = svcReader.svcGrabber(filename)

    #For Green Band
    cameraband = 560
    FWHM = 20

    reflectance = reflectance(wavelength,spectral_response,cameraband,FWHM)

    print(reflectance)
