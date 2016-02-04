import cv2
import time
import os
import numpy as np
import networktables

TESTMODE = True
MANUALIMAGEMODE = True
towerCameraRes = [1280.0, 720.0]
ballCameraRes = [1280.0, 720.0]
imageNumber = 1
frameNumber = 0
frames = 0
#
def processTowerCamera(camera):
    filteredContours = []
    originalImage = pollCamera(camera)
    #blurredImage = cv2.blur(originalImage, (6, 6))
    #RGBImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2RGB)
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
            if (solidity < 0.5 and area > 500 and size[1] > 25):
                filteredContours.append(x)
                print str(size[0]) + "x" + str(size[1]) + "_"+str(angle)
    cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
    if(TESTMODE):
        cv2.imshow("Image", originalImage)
    #TODO publish contours to network tables
    #end def
def processBallCamera(camera):
    originalImage = pollCamera(camera)
    originalImage
#end def    
    
def pollCamera(camera):
    if MANUALIMAGEMODE == True:
        imgOriginal = cv2.imread('towerImages/tower (' + str(imageNumber) + ')_720x405.jpg',1)
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
    if MANUALIMAGEMODE == True:
        towerCamera = cv2.VideoCapture(0)
        #ballCamera = cv2.VideoCapture(1)
    #end if
    towerCamera.set(cv2.CAP_PROP_FRAME_WIDTH, towerCameraRes[0])
    towerCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, towerCameraRes[1])
    print "Tower Camera Resolution = " + str(towerCamera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "x" + str(towerCamera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    lastTime = time.clock()
    if towerCamera.isOpened() == False:
        print "error: Tower Camera not initialized"
        os.system("pause")
        return
    # end if
    if TESTMODE:
        cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar("Image #", "Image", 0, 37, changeImage)
    while cv2.waitKey(1) != 27 and towerCamera.isOpened(): #and ballCamera.isOpened()
        processTowerCamera(towerCamera)
        lastTime = calculateFPS(lastTime)
        #end if
    # end while
    cv2.destroyAllWindows()
    return

###################################################################################################
if __name__ == "__main__":
    main()
