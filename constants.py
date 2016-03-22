import numpy as np

'''
Settings
'''
DEBUGLEVEL = 3 #0 = No output, 2 = FPS output, 3 = Found contours drawn, 4 = Network table value output, 5 = Super User
MANUALIMAGEMODE = False
FILTERTYPE = "HSV" #"HSV", "BGR", "HLS"
CAPTUREMODE = False
SINGLECAMERAMODE = False
FPSLIMIT = 18
PITYPE = "Tower" #"Tower", "Boulder"
RUNNINGONPI = False
try:
    import RPi.GPIO as GPIO
    RUNNINGONPI = True
except ImportError:
    if DEBUGLEVEL >= 1:
        print ("Not running on Raspberry Pi")

'''
Vision Processing Constants
'''
HSV_UPPER = np.array([96, 255, 255])
HSV_LOWER = np.array([66, 64, 225])
BGR_UPPER = np.array([255, 255, 194])
BGR_LOWER = np.array([204, 227, 0])
HLS_UPPER = np.array([99, 235, 255])
HLS_LOWER = np.array([70, 128, 163])

'''
Camera Settings
'''
#Possible Wide Screen Resolutions: 1280x720(921,600), 960x544(522,240), 800x448(358,400), 640x360(230,400)
TOWERCAMERA_RESOLUTION=[960, 544]
TOWERCAMERA_FPS=30
TOWERCAMERA_BRIGHTNESS=0.458
TOWERCAMERA_SATURATION=0.5
TOWERCAMERA_CONTRAST=0.415

BOULDERCAMERA_RESOLUTION=[800, 448]
BOULDERCAMERA_FPS=30
BOULDERCAMERA_BRIGHTNESS=0.458
BOULDERCAMERA_SATURATION=0.5
BOULDERCAMERA_CONTRAST=0.415

'''
Network Tables
'''
roboRioHostname = "roboRIO-2062-FRC.local"

'''
Image Directories
'''
TOWERIMAGESOURCE = 'idealTower'
BOULDERIMAGESOURCE = 'boulderLaserFilter'
towerCaptureLocation = ""
boulderCaptureLocation = ""
outputCaptureLocation = ""

'''
Classes
'''
visionTable = None
towerCamera = None
SU = None
recorder = None