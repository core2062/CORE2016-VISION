import time
import constants
import pollCamera
import networkTables
import platform
import os
import cv2
import sys
import numpy as np

class camera(object):
    networkTable = networkTables.networkTable()
    poll = pollCamera.poll()
    def __init__(self, noInit=False):
        if noInit:
            return
        global towerCamera, boulderCamera, frames, lastTime, cameraTime, pictureNumber
        if constants.TESTMODE and not constants.CAPTUREMODE:
            cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)
            if constants.MANUALIMAGEMODE:
                cv2.createTrackbar("Image #", "Image", 0, 54, self.changeImage)
                print ("ADJSADHALKDL")
        cameraTime = self.getTime()
        pictureNumber = 1
    def changeImage(self, img):
        self.imageNumber = img+1
    def capturePictures(self, picturesPerSecond, image = None):
        global pictureNumber, cameraTime
        print ("Capturing Tower Images to: " + camera.towerCaptureLocation)
        if not constants.SINGLECAMERAMODE:
            print ("Capturing Boulder Images to: " + camera.boulderCaptureLocation)
        if image is None:
            lastTime = self.getTime()
            if not os.path.exists(self.towerCaptureLocation):
                os.makedirs(self.towerCaptureLocation)
            if not constants.SINGLECAMERAMODE and not os.path.exists(self.boulderCaptureLocation):
                os.makedirs(self.boulderCaptureLocation)
            while(True):
                towerCameraImage = self.pollTower(True)
                boulderCameraImage = self.pollBoulder(True)
                while self.getTime() - lastTime < 1.0/picturesPerSecond:
                    time.sleep(0.1)
                lastTime = self.getTime()
                cv2.imwrite(self.towerCaptureLocation + 'tower (' + str(pictureNumber) + ').jpg', towerCameraImage)
                if not constants.SINGLECAMERAMODE:
                    cv2.imwrite(self.boulderCaptureLocation + 'boulder (' + str(pictureNumber) + ').jpg', boulderCameraImage)
                pictureNumber += 1
        else:
            if not self.getTime() - cameraTime < 1.0/picturesPerSecond:
                cameraTime = self.getTime()
                if not os.path.exists(self.outputCaptureLocation):
                    os.makedirs(self.outputCaptureLocation)
                cv2.imwrite(self.outputCaptureLocation + 'output (' + str(pictureNumber) + ').jpg', image)
                pictureNumber += 1
    def processTower(self):
        filteredContours = []
        originalImage = self.poll.pollTower()
        if constants.FILTERTYPE == "HSV": #Filter with the most accurate tower detection
            HSVImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HSV)
            ThresholdImage = cv2.inRange(HSVImage, np.array([66,64,225]), np.array([96, 255, 255]))
        elif constants.FILTERTYPE == "RGB": #Overall fastest filter
            ThresholdImage = cv2.inRange(originalImage, np.array([0,227,204]), np.array([194,255,255]))
            #ThresholdImage = cv2.inRange(originalImage, np.array([204,227,0]), np.array([255,255,194]))
        elif constants.FILTERTYPE == "HSL": #Filter with the most consistent tower detection
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
                    cameraPixels = (self.towerCameraRes[0]*self.towerCameraRes[1])
                    if (solidity < 0.4 and area/cameraPixels > 0.001714 and size[1]/cameraPixels > 0.00008573):
                        if area > largestArea:
                            largestContour = centroid,size,angle,x
                            largestArea = area
                        if constants.TESTMODE:
                            filteredContours.append(x)
            if constants.TESTMODE:
                if constants.DEBUGMODE:
                    cv2.drawContours(originalImage,contours,-1,(0,255,255),2)
                cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
        if largestContour is not None:
            self.networkTable.endNumber("goal_x", round(largestContour[0][0],1))
            self.networkTable.sendNumber("goal_y", round(largestContour[0][1],1))
            self.networkTable.sendNumber("goal_width", round(largestContour[1][0],1))
            self.networkTable.sendNumber("goal_height", round(largestContour[1][1],1))
            self.networkTable.sendNumber("goal_angle", round(largestContour[2],1))
            if constants.TESTMODE:
                cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 2, (0,255,0), 5, 2)
        else:
            self.networkTable.sendNumber("goal_x", -1)
            self.networkTable.sendNumber("goal_y", -1)
            self.networkTable.sendNumber("goal_width", -1)
            self.networkTable.sendNumber("goal_height", -1)
            self.networkTable.sendNumber("goal_angle", -1)
        if constants.TESTMODE:
            cv2.imshow("Image", originalImage)
        if constants.OUTPUTCAPTUREMODE:
            self.capturePictures(1, originalImage)
    def processBoulder(self):
        originalImage = self.poll.pollBoulder()
        ThresholdImage = cv2.inRange(originalImage, 60, 255)
        if constants.TESTMODE:    
            cv2.imshow("Image", ThresholdImage)
        if constants.OUTPUTCAPTUREMODE:
            self.capturePictures(1, originalImage)
    def getTime(self):
        if platform.system() == "Linux":
            return time.time()
        else:
            return time.clock()