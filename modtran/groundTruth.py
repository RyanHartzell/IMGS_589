import os
import numpy
import glob

def read_spec_alb(specAlbPath, target):
    specDict = {}
    with open(specAlbPath) as f:
        wLSpec = []
        wavelengths = []
        number, key = None, None

        for line in f:
            line = " ".join(line.split())
            if "!" in line:
                line = line[:line.index("!")]
            splitted = line.split()
            if len(splitted) > 0:
                if splitted[0].isdigit():
                    if len(wLSpec) > 0 and number != key != None:
                        specDict[(number, key)] = numpy.asarray(wLSpec)
                        wLSpec = []
                        wavelengths = []
                    number = int(splitted[0])
                    if number < 0:
                        msg = "Key index must be positive, {0}".format(number)
                        raise ValueError(msg)
                    key = ' '.join(splitted[1:])
                else:
                    wL = float(splitted[0])
                    wavelengths.append(wL)
                    sP = float(splitted[1])
                    if wavelengths == sorted(wavelengths) and 0 <= sP <= 1:
                        wLSpec.append([wL,sP])
                    else:
                        msg = "The spectral albedo must be between 0 and 1 and "
                        msg += "wavelengths must be in ascending order \n"
                        msg += " ".join((str(number), key, line))
                        raise ValueError(msg)

    specArray = next((v for k,v in specDict.items() if target in k), None)
    if specArray is None:
        print("The target key, '{0}' was not able to be found.".format(target))
        print("Spectral albedo file {0}.".format(specAlbPath))
        print("The function will return None.")
        print("These keys are available: {0}".format(list(specDict.keys())))

    return specArray



if __name__ == "__main__":

    import os
    import time

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    specAlbPath = currentDirectory + "/spec_alb.dat"

    target = "healthy grass"
    #target = 11
    specArray = read_spec_alb(specAlbPath, target)
    print(specArray[:,:])
