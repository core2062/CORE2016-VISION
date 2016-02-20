import cameraProcessing
import cv2
try:
    import RPi.GPIO as GPIO
except ImportError:
    print "Running on Windows"
import time
import platform
from networktables import NetworkTable
import argparse

TESTMODE = True
DEBUGMODE = False
MANUALIMAGEMODE = False
FILTERTYPE = "HSV" #"HSV", "RGB", "HSL"
SINGLECAMERAMODE = True
CAPTUREMODE = False
OUTPUTCAPTUREMODE = False

global visionNetworkTable
hostname = "roboRIO-2062-FRC.local"
NetworkTable.setIPAddress(hostname)
NetworkTable.setClientMode()
NetworkTable.initialize()

visionNetworkTable = NetworkTable.getTable("vision")

def calculateFPS(lastTime):
    currentTime = time.clock()
    global frames
    deltaTime = (currentTime - lastTime)
    if(deltaTime>=1):
        fps = round(frames/(currentTime - lastTime),1)
        print "FPS: " + str(fps)
        visionNetworkTable.putNumber("fps", fps)
        frames = 1.0
        return currentTime
    else:
        frames += 1.0
        return lastTime
def main():
    global frames, pictureNumber, towerCaptureLocation, boulderCaptureLocation, outputCaptureLocation, cameraTime, visionNetworkTable
    if platform.system() == "Linux":
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(11, GPIO.IN)
        GPIO.setup(12, GPIO.OUT)
        GPIO.output(12, GPIO.HIGH)
        if GPIO.input(11):
            global CAPTUREMODE
            CAPTUREMODE = True
        GPIO.output(12, GPIO.LOW)
        global TESTMODE, MANUALIMAGEMODE, DEBUGMODE
        TESTMODE = False
        MANUALIMAGEMODE = False
        DEBUGMODE = False
    camera = cameraProcessing.camera(SINGLECAMERAMODE, FILTERTYPE, TESTMODE, MANUALIMAGEMODE, DEBUGMODE, CAPTUREMODE, OUTPUTCAPTUREMODE, visionNetworkTable)
    visionNetworkTable.putString("debug", time.strftime("%H:%M:%S", time.gmtime())+": Network Table Initialized")
    visionNetworkTable.putString("debug", (time.strftime("%H:%M:%S", time.gmtime())+": Camera Res = " + str(camera.towerCameraRes[0]) + "x" + str(camera.towerCameraRes[1])))
    parser = argparse.ArgumentParser(description='CORE 2062\'s 2016 Vision Processing System - Developed by Andrew Kempen')
    parser.add_argument('-c', action='store', dest="picturesPerSecond", help='Capture images from all cameras at a rate given by the parameter in pictures/second', type=int)
    args = parser.parse_args()
    pictureNumber = 0
    lastFPSTime = time.clock()
    frames = 0
    if args.picturesPerSecond or CAPTUREMODE:
        if CAPTUREMODE:
            picturesPerSec = 0.5
        else:
            picturesPerSec = args.picturesPerSecond
        print "Capturing Tower Images to: " + camera.towerCaptureLocation
        if not SINGLECAMERAMODE:
            print "Capturing Boulder Images to: " + camera.boulderCaptureLocation
        camera.capturePictures(picturesPerSec)
    else:
        while cv2.waitKey(1) != 27 and camera.isTowerCameraOpen(): #and camera.isBoulderCameraOpen()
            if visionNetworkTable.getString("mode", "tower") == "tower":
                camera.processTower()
            elif visionNetworkTable.getString("mode", "tower") == "boulder":
                camera.processBoulderCamera()
            lastFPSTime = calculateFPS(lastFPSTime)
        cv2.destroyAllWindows()
    visionNetworkTable.putString("debug", time.strftime("%H:%M:%S", time.gmtime())+": Program End")
    return

###################################################################################################
if __name__ == "__main__":
    main()