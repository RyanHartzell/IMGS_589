


import argparse
import os
import numpy as np
from interp1 import interp1
from update_tape5 import update_tape5
from read_tape7 import read_tape7
import cv2
import matplotlib.pyplot as plt



parser = argparse.ArgumentParser(description='Collect files for Modtran4 Runs')
parser.add_argument('-r', '--relativeSpectralResponse', type=str, help='The camera RSR excel file path')
parser.add_argument('-s', '--svcFiles', type=str, help='The SVC .sig Files')

args = parser.parse_args()
rsrPath = args.relativeSpectralResponse
svcPath = args.svcFiles
