import cv2
import time
from time import gmtime, strftime
import os
import sys
import numpy as np
import platform
from networktables import NetworkTable
import argparse

TESTMODE = True
DEBUGMODE = False
MANUALIMAGEMODE = True
FILTERTYPE = "HSV" #"HSV", "RGB", "HSL"
SINGLECAMERAMODE = True
TOWERIMAGESOURCE = 'idealTower'
BOULDERIMAGESOURCE = 'boulderLaserFilter'

#Possible Wide Screen Resolutions: 1280x720(921,600), 960x544(522,240), 800x448(358,400), 640x360(230,400)
towerCameraRes = [960, 544]
boulderCameraRes = [800, 448]
imageNumber = 1
visionNetworkTable = None
hostname = "roboRIO-2062-FRC.local"

def capturePictures(picturesPerSecond, image = None):
    global pictureNumber, cameraTime
    if image is None:
        lastTime = time.clock()
        if not os.path.exists(towerCaptureLocation):
            os.makedirs(towerCaptureLocation)
        if not SINGLECAMERAMODE and not os.path.exists(boulderCaptureLocation):
            os.makedirs(boulderCaptureLocation)
        while(True):
            towerCameraImage = pollTowerCamera(True)
            boulderCameraImage = pollBoulderCamera(True)
            while time.clock() - lastTime < 1.0/picturesPerSecond:
                time.sleep(0.001)
            lastTime = time.clock()
            cv2.imwrite(towerCaptureLocation + 'tower (' + str(pictureNumber) + ').jpg', towerCameraImage)
            cv2.imwrite(boulderCaptureLocation + 'boulder (' + str(pictureNumber) + ').jpg', boulderCameraImage)
            pictureNumber += 1
    else:
        if not time.clock() - cameraTime < 1.0/picturesPerSecond:
            cameraTime = time.clock()
            if not os.path.exists(outputCaptureLocation):
                os.makedirs(outputCaptureLocation)
            cv2.imwrite(outputCaptureLocation + 'output (' + str(pictureNumber) + ').jpg', image)
            pictureNumber += 1
def processTowerCamera(camera):
    filteredContours = []
    originalImage = pollTowerCamera()
    if FILTERTYPE == "HSV": #Filter with the most accurate tower detection
        HSVImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HSV)
        ThresholdImage = cv2.inRange(HSVImage, np.array([66,64,225]), np.array([96, 255, 255]))
    elif FILTERTYPE == "RGB": #Overall fastest filter
        ThresholdImage = cv2.inRange(originalImage, np.array([204,227,0]), np.array([255, 255, 194])) #np.array([B,G,R])
    elif FILTERTYPE == "HSL": #Filter with the most consistent tower detection
        HSLImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HLS)
        ThresholdImage = cv2.inRange(HSLImage, np.array([70,128,163]), np.array([99, 235, 255]))
    _,contours,_ = cv2.findContours(ThresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largestArea = 0
    largestContour = None
    if contours is not None:
        for x in contours:
            centroid,size,angle = cv2.minAreaRect(x)
            area = abs(size[0]*size[1])
            if area != 0:
                hull = cv2.convexHull(x)
                contourArea = cv2.contourArea(x)
                hull_area = cv2.contourArea(hull)
                solidity = float(contourArea)/hull_area
                cameraPixels = (towerCameraRes[0]*towerCameraRes[1])
                if (solidity < 0.4 and area/cameraPixels > 0.001714 and size[1]/cameraPixels > 0.00008573):
                    if area > largestArea:
                        largestContour = centroid,size,angle,x
                        largestArea = area
                    if TESTMODE:
                        filteredContours.append(x)
        if TESTMODE:
            if DEBUGMODE:
                cv2.drawContours(originalImage,contours,-1,(0,255,255),2)
            cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
    if largestContour is not None:
        sendNumber("goal_x", round(largestContour[0][0],1))
        sendNumber("goal_y", round(largestContour[0][1],1))
        sendNumber("goal_width", round(largestContour[1][0],1))
        sendNumber("goal_height", round(largestContour[1][1],1))
        sendNumber("goal_angle", round(largestContour[2],1))
        if TESTMODE:
            cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 2, np.array([0,255,0]), 5, 2)
    else:
        sendNumber("goal_x", -1)
        sendNumber("goal_y", -1)
        sendNumber("goal_width", -1)
        sendNumber("goal_height", -1)
        sendNumber("goal_angle", -1)
    if TESTMODE:
        cv2.imshow("Image", originalImage)
    capturePictures(1, originalImage)
def processBoulderCamera(camera):
    originalImage = pollBoulderCamera()
    greyImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    ThresholdImage = cv2.inRange(greyImage, 60, 255)
    if TESTMODE:    
        cv2.imshow("Image", ThresholdImage)
    capturePictures(1, originalImage)
def sendNumber(name, value):
    if DEBUGMODE:
        print name + ": " + str(value)
    visionNetworkTable.putNumber(name,value)
def pollTowerCamera(forceActualCamera = False):
    if MANUALIMAGEMODE  and not forceActualCamera:
        imgOriginal = cv2.imread('towerImages/' + TOWERIMAGESOURCE + '/' + TOWERIMAGESOURCE + ' (' + str(imageNumber) + ')_960x540.jpg',1)
        if imgOriginal is None:
            print "Error: towerCamera frame not read from file"
            return
    else:
        blnFrameReadSuccessfully, imgOriginal = towerCamera.read()
        if not blnFrameReadSuccessfully or imgOriginal is None:
            print "Error: frame not read from towerCamera"
            return
    return imgOriginal
def pollBoulderCamera(forceActualCamera = False):
    if MANUALIMAGEMODE and not forceActualCamera:
        imgOriginal = cv2.imread('boulderImages/' + BOULDERIMAGESOURCE + '/' + BOULDERIMAGESOURCE + ' (' + str(imageNumber) + ').jpg',1)
        if imgOriginal is None:
            print "Error: boulderCamera frame not read from file"
            return
    else:
        if SINGLECAMERAMODE:
            blnFrameReadSuccessfully, imgOriginal = towerCamera.read()
        else:
            blnFrameReadSuccessfully, imgOriginal = boulderCamera.read()
        if not blnFrameReadSuccessfully or imgOriginal is None:
            print "Error: frame not read from boulderCamera"
            return
    imgOriginal = imgOriginal[(int(boulderCameraRes[1]/6-boulderCameraRes[1])):boulderCameraRes[1], 0:boulderCameraRes[0]]
    #Area to Keep: [Top Y Value:Bottom Y Value, Top X Value:Bottom X Value]
    return imgOriginal
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
def changeImage(img):
    global imageNumber
    imageNumber = img+1
def main():
    global towerCamera, boulderCamera, frames, pictureNumber, towerCaptureLocation, boulderCaptureLocation, outputCaptureLocation, visionNetworkTable, cameraTime
    if platform.system() == "Linux":
        global TESTMODE, MANUALIMAGEMODE, DEBUGMODE
        TESTMODE = False
        MANUALIMAGEMODE = False
        DEBUGMODE = False
    parser = argparse.ArgumentParser(description='CORE 2062\'s 2016 Vision Processing System - Developed by Andrew Kempen')
    parser.add_argument('-c', action='store', dest="picturesPerSecond", help='Capture images from all cameras at a rate given by the parameter in pictures/second', type=int)
    args = parser.parse_args()
    pictureNumber = 0
    frames = 0
    cameraTime = time.clock()
    NetworkTable.setIPAddress(hostname)
    NetworkTable.setClientMode()
    NetworkTable.initialize()
    visionNetworkTable = NetworkTable.getTable('Vision')
    visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Network Table Initialized")
    towerCamera = cv2.VideoCapture(0)
    towerCamera.set(cv2.CAP_PROP_FRAME_WIDTH, towerCameraRes[0])
    towerCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, towerCameraRes[1])
    towerCameraRes[0] = towerCamera.get(cv2.CAP_PROP_FRAME_WIDTH)
    towerCameraRes[1] = towerCamera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print "Tower Camera Resolution = " + str(towerCameraRes[0]) + "x" + str(towerCameraRes[1])
    if not SINGLECAMERAMODE:
        boulderCamera = cv2.VideoCapture(1)
        boulderCamera.set(cv2.CAP_PROP_FRAME_WIDTH, boulderCameraRes[0])
        boulderCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, boulderCameraRes[1])
        boulderCameraRes[0] = boulderCamera.get(cv2.CAP_PROP_FRAME_WIDTH)
        boulderCameraRes[1] = boulderCamera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print "Boulder Camera Resolution = " + str(boulderCameraRes[0]) + "x" + str(boulderCameraRes[1])
    visionNetworkTable.putString("debug", (strftime("%H:%M:%S", gmtime())+": Camera Res = " + str(towerCameraRes[0]) + "x" + str(towerCameraRes[1])))
    lastTime = time.clock()
    dateTime = str(strftime("%m-%d_%H-%M", gmtime()))
    towerCaptureLocation = 'capturedImages/tower '  + dateTime+ '/'
    boulderCaptureLocation = 'capturedImages/boulder '  + dateTime + '/'
    outputCaptureLocation = 'capturedImages/output '  + dateTime + '/'
    if towerCamera.isOpened() == False:
        print "error: Tower Camera not initialized"
        visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Tower Camera not initialized")
        os.execl(sys.executable, sys.executable, *sys.argv)
    if args.picturesPerSecond:
        print "Capturing Tower Images to: " + towerCaptureLocation
        if not SINGLECAMERAMODE:
            print "Capturing Boulder Images to: " + boulderCaptureLocation
        capturePictures(args.picturesPerSecond)
    else:
        if TESTMODE:
            cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)
            if MANUALIMAGEMODE:
                cv2.createTrackbar("Image #", "Image", 0, 54, changeImage)
        while cv2.waitKey(1) != 27 and towerCamera.isOpened(): #and boulderCamera.isOpened()
            if visionNetworkTable.getString("mode", "tower") == "tower":
                processTowerCamera(towerCamera)
            elif visionNetworkTable.getString("mode", "tower") == "boulder":
                processBoulderCamera(towerCamera)
            lastTime = calculateFPS(lastTime)
        cv2.destroyAllWindows()
    visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Program End")
    return

###################################################################################################
if __name__ == "__main__":
    main()