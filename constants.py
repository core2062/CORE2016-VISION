import numpy as np

'''
Settings
'''
DEBUGLEVEL = 5 #0 = No output, 2 = FPS output, 3 = Found contours drawn, 4 = Network table value output, 5 = Super User
MANUALIMAGEMODE = True
FILTERTYPE = "HLS" #"HSV", "BGR", "HLS"
CAPTUREMODE = False
SINGLECAMERAMODE = False
FPSLIMIT = 18
PITYPE = "Tower" #"Tower", "Boulder"
RUNNINGONPI = False
SENDTOSMARTDASHBOARD = False
try:
    import RPi.GPIO as GPIO
    RUNNINGONPI = True
except ImportError:
    if DEBUGLEVEL >= 1:
        print ("Not running on Raspberry Pi")

'''
Vision Processing Constants
'''
HSV_UPPER = np.array([91, 255, 255])
HSV_LOWER = np.array([68, 60, 99])
BGR_UPPER = np.array([255, 255, 151])
BGR_LOWER = np.array([123, 175, 0])
HLS_UPPER = np.array([92, 255, 255])
HLS_LOWER = np.array([66, 73, 111])

'''
Camera Settings
'''
#Possible Wide Screen Resolutions: 1280x720(921,600), 960x544(522,240), 800x448(358,400), 640x360(230,400)
TOWERCAMERA_RESOLUTION=[960, 544]
TOWERCAMERA_FPS=30
TOWERCAMERA_BRIGHTNESS=0#0.458
TOWERCAMERA_SATURATION=0.5
TOWERCAMERA_CONTRAST=0.415

BOULDERCAMERA_RESOLUTION=[800, 448]
BOULDERCAMERA_FPS=30
BOULDERCAMERA_BRIGHTNESS=1
BOULDERCAMERA_SATURATION=0.5
BOULDERCAMERA_CONTRAST=0.415

'''
Network Tables
'''
roboRioHostname = "10.20.62.2"

'''
Image Directories
'''
TOWERIMAGESOURCE = 'competitionTower'
BOULDERIMAGESOURCE = 'boulderLaserFilter'
towerCaptureLocation = ""
boulderCaptureLocation = ""
outputCaptureLocation = ""

'''
Classes
'''
visionTable = None
smartDashboard = None
towerCamera = None
SU = None
recorder = None