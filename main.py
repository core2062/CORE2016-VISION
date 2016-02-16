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
FILTERTYPE = "HSV" #"RGB" "HSL"
IMAGESOURCE = 'idealTower'

#Possible Wide Screen Resolutions: 1280x720(921,600), 960x544(522,240), 800x448(358,400), 640x360(230,400)
towerCameraRes = [960, 544]
ballCameraRes = [800, 448]
imageNumber = 1
frameNumber = 0
frames = 0
visionNetworkTable = None
hostname = "roboRIO-2062-FRC.local"

def recordVideo(cap):
    video = cv2.VideoWriter(('towerVideos/towerCamera'+str(strftime("%m-%d_%H.%M", gmtime()))+'.avi'), cv2.VideoWriter_fourcc('X','V','I','D'), 14.0, (int(towerCameraRes[0]), int(towerCameraRes[1])))
    global lastTime
    lastTime = time.clock()
    while True:
        _,img = cap.read()
        video.write(img)
        cv2.imshow("towerCamera",img)
        if (cv2.waitKey(1) != -1):
            break
    video.release()
    cv2.destroyAllWindows()
def processTowerCamera(camera):
    filteredContours = []
    originalImage = pollCamera(camera)
    if FILTERTYPE == "HSV":
        HSVImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HSV)
        ThresholdImage = cv2.inRange(HSVImage, np.array([66,64,225]), np.array([91, 255, 255]))
    elif FILTERTYPE == "RGB":
        #np.array([B,G,R])
        ThresholdImage = cv2.inRange(originalImage, np.array([204,227,0]), np.array([255, 255, 194]))
    elif FILTERTYPE == "HSL":
        HSLImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HLS)
        ThresholdImage = cv2.inRange(HSLImage, np.array([70,128,163]), np.array([99, 235, 255]))
    _,contours,_ = cv2.findContours(ThresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largestArea = 0
    largestContour = None
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
                if(area > largestArea):
                    largestContour = centroid,size,angle,x
                    largestArea = area
                filteredContours.append(x)
    cv2.drawContours(originalImage,contours,-1,(0,255,255),2)
    cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
    if largestContour is not None:
        sendNumber("goal_x", round(largestContour[0][0],1))
        sendNumber("goal_y", round(largestContour[0][1],1))
        sendNumber("goal_width", round(largestContour[1][0],1))
        sendNumber("goal_height", round(largestContour[1][1],1))
        sendNumber("goal_angle", round(largestContour[2],1))
        cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 2, np.array([0,255,0]), 5, 2)
    if(TESTMODE):
        cv2.imshow("Image", originalImage)
def processBallCamera(camera):
    originalImage = pollCamera(camera)
    return originalImage
def sendNumber(name, value):
    if DEBUGMODE == True:
        print name + ": " + str(value)
    visionNetworkTable.putNumber(name,value)
def pollCamera(camera):
    if MANUALIMAGEMODE == True:
        imgOriginal = cv2.imread('towerImages/' + IMAGESOURCE + '/' + IMAGESOURCE +' (' + str(imageNumber) + ')_960x540.jpg',1)
    else:
        blnFrameReadSuccessfully, imgOriginal = camera.read()
        if not blnFrameReadSuccessfully or imgOriginal is None:
            print "error: frame not read from towerCamera"
            return
    return imgOriginal
def calculateFPS(lastTime):
    currentTime = time.clock()
    global frameNumber
    global frames
    deltaTime = (currentTime - lastTime)
    if(deltaTime>=1):
        fps = round(frames/(currentTime - lastTime),1)
        print "FPS: " + str(fps)
        visionNetworkTable.putNumber("fps", fps)
        frameNumber = 0
        frames = 1.0
        return currentTime
    else:
        frames += 1.0
        frameNumber+=1
        return lastTime
def changeImage(img):
    global imageNumber
    imageNumber = img+1
def main():
    if platform.system() == "Linux":
        global TESTMODE
        TESTMODE = False
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--record", help="Record Video")
    args = parser.parse_args()
    towerCamera = cv2.VideoCapture(0)
    #ballCamera = cv2.VideoCapture(1)
    NetworkTable.setIPAddress(hostname)
    NetworkTable.setClientMode()
    NetworkTable.initialize()
    global visionNetworkTable
    visionNetworkTable = NetworkTable.getTable('Vision')
    visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Network Table Initialized")
    towerCamera.set(cv2.CAP_PROP_FRAME_WIDTH, towerCameraRes[0])
    towerCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, towerCameraRes[1])
    towerCameraRes[0] = towerCamera.get(cv2.CAP_PROP_FRAME_WIDTH)
    towerCameraRes[1] = towerCamera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print "Tower Camera Resolution = " + str(towerCameraRes[0]) + "x" + str(towerCameraRes[1])
    visionNetworkTable.putString("debug", (strftime("%H:%M:%S", gmtime())+": Camera Res = " + str(towerCameraRes[0]) + "x" + str(towerCameraRes[1])))
    lastTime = time.clock()
    if towerCamera.isOpened() == False:
        print "error: Tower Camera not initialized"
        visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Tower Camera not initialized")
        os.execl(sys.executable, sys.executable, *sys.argv)
    if args.record:
        recordVideo(towerCamera)
    else:
        if TESTMODE:
            cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)
            if MANUALIMAGEMODE:
                cv2.createTrackbar("Image #", "Image", 0, 54, changeImage)
        while cv2.waitKey(1) != 27 and towerCamera.isOpened(): #and ballCamera.isOpened()
            if visionNetworkTable.getString("mode", "tower") == "tower":
                processTowerCamera(towerCamera)
            elif visionNetworkTable.getString("mode", "tower") == "ball":
                processBallCamera(towerCamera)
            lastTime = calculateFPS(lastTime)
        cv2.destroyAllWindows()
    visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Program End")
    return

###################################################################################################
if __name__ == "__main__":
    main()