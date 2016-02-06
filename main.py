import cv2
import time
from time import gmtime, strftime
import os
import sys
import numpy as np
import platform
from networktables import NetworkTable

TESTMODE = True
MANUALIMAGEMODE = True
towerCameraRes = [960.0, 544.0]
ballCameraRes = [1280.0, 720.0]
imageNumber = 1
frameNumber = 0
frames = 0
visionNetworkTable = None
hostname = "roboRIO-2062-FRC.local"

def processTowerCamera(camera):
    filteredContours = []
    originalImage = pollCamera(camera)
    RBGThresholdImage = cv2.inRange(originalImage, np.array([197,122,69]), np.array([255, 255, 255]))
    _,contours,_ = cv2.findContours(RBGThresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for x in contours:
        centroid,size,angle = cv2.minAreaRect(x)
        area = abs(size[0]*size[1])
        hull = cv2.convexHull(x)
        contourArea = cv2.contourArea(x)
        if area != 0:
            hull_area = cv2.contourArea(hull)
            solidity = float(contourArea)/hull_area
            if (solidity < 0.4 and area/(towerCameraRes[0]*towerCameraRes[1]) > 0.001714 and size[1]/(towerCameraRes[0]*towerCameraRes[1]) > 0.00008573):
                filteredContours.append(x)
    cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
    i = 1
    for x in filteredContours:
        centroid,size,angle = cv2.minAreaRect(filteredContours[i-1])
        visionNetworkTable.putNumber("goal"+str(i)+"_x", centroid[0])
        visionNetworkTable.putNumber("goal"+str(i)+"_y", centroid[1])
        visionNetworkTable.putNumber("goal"+str(i)+"_width", size[0])
        visionNetworkTable.putNumber("goal"+str(i)+"_height", size[1])
        visionNetworkTable.putNumber("goal"+str(i)+"_angle", angle)
        cv2.circle(originalImage, (int(centroid[0]),int(centroid[1])), 2, np.array([0,255,0]), 2, 8 );
        i+=1
    for x in range(3-i):
        visionNetworkTable.putNumber("goal"+str(x+i)+"_x", -1)
        visionNetworkTable.putNumber("goal"+str(x+i)+"_y", -1)
        visionNetworkTable.putNumber("goal"+str(x+i)+"_width", -1)
        visionNetworkTable.putNumber("goal"+str(x+i)+"_height", -1)
        visionNetworkTable.putNumber("goal"+str(x+i)+"_angle", -1)
    if(TESTMODE):
        cv2.imshow("Image", originalImage)
#end def
def processBallCamera(camera):
    originalImage = pollCamera(camera)
    originalImage
#end def    
    
def pollCamera(camera):
    if MANUALIMAGEMODE == True:
        imgOriginal = cv2.imread('towerImages/tower (' + str(imageNumber) + ')_960x540.jpg',1)
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
        fps = frames/(currentTime - lastTime)
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
    while cv2.waitKey(1) != 27 and towerCamera.isOpened(): #and ballCamera.isOpened()
        processTowerCamera(towerCamera)
        lastTime = calculateFPS(lastTime)
    cv2.destroyAllWindows()
    visionNetworkTable.putString("debug", strftime("%H:%M:%S", gmtime())+": Program End")
    return

###################################################################################################
if __name__ == "__main__":
    main()