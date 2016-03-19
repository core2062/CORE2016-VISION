from OLD import cameraProcessing
from OLD import constants
from OLD import pollCamera
from OLD import networkTables
import cv2
try:
    import RPi.GPIO as GPIO
    constants.RUNNINGONPI = True
except ImportError:
    constants.RUNNINGONPI = False
import time
import argparse

camera = cameraProcessing.camera()
poll = pollCamera.poll()
networkTable = networkTables.networkTable()

def calculateFPS(lastTime):
    currentTime = camera.getTime()
    global frames
    deltaTime = (currentTime - lastTime)
    if(deltaTime>=1):
        fps = round(frames/(currentTime - lastTime),1)
        print ("FPS: " + str(fps))
        networkTable.putNumber("fps", fps)
        frames = 1.0
        return currentTime
    else:
        frames += 1.0
        return lastTime
def main():
    global frames, pictureNumber, towerCaptureLocation, boulderCaptureLocation, outputCaptureLocation, cameraTime, visionNetworkTable, camera
    if constants.RUNNINGONPI:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(11, GPIO.IN)
        GPIO.setup(12, GPIO.OUT)
        GPIO.output(12, GPIO.HIGH)
        if GPIO.input(11):
            constants.CAPTUREMODE = True
        GPIO.output(12, GPIO.LOW)
        constants.TESTMODE = False
        constants.MANUALIMAGEMODE = False
        constants.DEBUGMODE = False
    parser = argparse.ArgumentParser(description='CORE 2062\'s 2016 Vision Processing System - Developed by Andrew Kempen')
    parser.add_argument('-c', action='store', dest="picturesPerSecond", help='Capture images from all cameras at a rate given by the parameter in pictures/second', type=int)
    args = parser.parse_args()
    pictureNumber = 0
    lastFPSTime = camera.getTime()
    frames = 0
    if args.picturesPerSecond or constants.CAPTUREMODE:
        if constants.CAPTUREMODE:
            picturesPerSec = 1
        else:
            picturesPerSec = args.picturesPerSecond
        camera.capturePictures(picturesPerSec)
    else:
        while cv2.waitKey(1) != 27 and poll.isTowerCameraOpen(): #and camera.isBoulderCameraOpen()
            if True:
                print("POINT 1")
                camera.processTower()
            elif visionNetworkTable.getString("mode", "tower") == "boulder":
                camera.processBoulderCamera()
            lastFPSTime = calculateFPS(lastFPSTime)
        cv2.destroyAllWindows()
        camera.closeCameras()
    visionNetworkTable.putString("debug", time.strftime("%H:%M:%S", time.gmtime())+": Program End")
    return

###################################################################################################
if __name__ == "__main__":
    main()