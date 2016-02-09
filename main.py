import cv2
import time
from time import gmtime, strftime
import os
import sys
import numpy as np
import platform
from networktables import NetworkTable
from cv2 import circle

TESTMODE = True
MANUALIMAGEMODE = True
towerCameraRes = [960.0, 544.0]
ballCameraRes = [1280.0, 720.0]
imageNumber = 1
frameNumber = 0
frames = 0
visionNetworkTable = None
hostname = "roboRIO-2062-FRC.local"

#######################
# Temp
min_dist = 100
param_1 = 100
param_2 = 100
min_radius = 20
max_radius = 0
#######################

def processTowerCamera(camera):
    filteredContours = []
    originalImage = pollCamera(camera)
    RBGThresholdImage = cv2.inRange(originalImage, np.array([197,122,69]), np.array([255, 255, 255]))
    _,contours,_ = cv2.findContours(RBGThresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largestArea = 0
    largestContour = None
    for x in contours:
        centroid,size,angle = cv2.minAreaRect(x)
        area = abs(size[0]*size[1])
        hull = cv2.convexHull(x)
        contourArea = cv2.contourArea(x)
        if area != 0:
            hull_area = cv2.contourArea(hull)
            solidity = float(contourArea)/hull_area
            if (solidity < 0.4 and area/(towerCameraRes[0]*towerCameraRes[1]) > 0.001714 and size[1]/(towerCameraRes[0]*towerCameraRes[1]) > 0.00008573):
                if(area > largestArea):
                    largestContour = centroid,size,angle,x
                filteredContours.append(x)
    cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
    sendNumber("goal_x", round(largestContour[0][0],1))
    sendNumber("goal_y", round(largestContour[0][1],1))
    sendNumber("goal_width", round(largestContour[1][0],1))
    sendNumber("goal_height", round(largestContour[1][1],1))
    sendNumber("goal_angle", round(largestContour[2],1))
    cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 2, np.array([0,255,0]), 5, 2);
    if(TESTMODE):
        cv2.imshow("Image", originalImage)
#end def
def processBallCamera(camera):
    greyImage = None
    circles = None
    originalImage = pollCamera(camera)
    greyImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    greyImage = cv2.blur(greyImage, (15, 15))
    circles = cv2.HoughCircles(greyImage,cv2.HOUGH_GRADIENT,1,min_dist,param_1,param_2,min_radius,max_radius)
    circles = np.uint16(np.around(circles))
    if len(circles) != 0:
        for i in circles[0,:]:
            cv2.circle(originalImage,(i[0],i[1]),i[2],(0,255,0),2)
            cv2.circle(originalImage,(i[0],i[1]),2,(0,0,255),3)
    if(TESTMODE):
        cv2.imshow("Image", originalImage)
    return originalImage
#end def
def sendNumber(name, value):
    if(TESTMODE):
        print name + ": " + str(value)
    visionNetworkTable.putNumber(name,value)
#end def
def pollCamera(camera):
    if MANUALIMAGEMODE == True:
        #imgOriginal = cv2.imread('towerImages/tower (' + str(imageNumber) + ')_960x540.jpg',1)
        imgOriginal = cv2.imread('boulderImages/boulder (' + str(imageNumber) + ').jpg',1)
    else:
        blnFrameReadSuccessfully, imgOriginal = camera.read()
        if not blnFrameReadSuccessfully or imgOriginal is None:
            print "error: frame not read from towerCamera"
            return
        #end if
    #end else
    return imgOriginal
#end def

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
#end def

def changeImage(img):
    global imageNumber
    imageNumber = img+1
def change_min_dist(img):
    global min_dist
    min_dist = img
def change_param_1(img):
    global param_1
    param_1 = img
def change_param_2(img):
    global param_2
    param_2 = img
def change_min_radius(img):
    global min_radius
    min_radius = img
def change_max_radius(img):
    global max_radius
    max_radius = img
#min_dist,param_1,param_2,min_radius,max_radius
def main():
    if platform.system() == "Linux":
        global TESTMODE
        TESTMODE = False
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
    print "Tower Camera Resolution = " + str(towerCamera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "x" + str(towerCamera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    visionNetworkTable.putString("debug", (strftime("%H:%M:%S", gmtime())+": Camera Res = " + str(towerCamera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "x" + str(towerCamera.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    lastTime = time.clock()
    if towerCamera.isOpened() == False:
        print "error: Tower Camera not initialized"
        visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Tower Camera not initialized")
        os.execl(sys.executable, sys.executable, *sys.argv)
    if TESTMODE:
        cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar("Image #", "Image", 0, 37, changeImage)
        cv2.createTrackbar("min_dist", "Image", 50, 100, change_min_dist)
        cv2.createTrackbar("param_1", "Image", 100, 200, change_param_1)
        cv2.createTrackbar("param_2", "Image", 100, 100, change_param_2)
        cv2.createTrackbar("min_radius", "Image", 1, 100, change_min_radius)
        cv2.createTrackbar("max_radius", "Image", 0, 100, change_max_radius)
    while cv2.waitKey(1) != 27 and towerCamera.isOpened(): #and ballCamera.isOpened()
        #processTowerCamera(towerCamera)
        processBallCamera(towerCamera)
        lastTime = calculateFPS(lastTime)
    cv2.destroyAllWindows()
    visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Program End")
    return

###################################################################################################
if __name__ == "__main__":
    main()