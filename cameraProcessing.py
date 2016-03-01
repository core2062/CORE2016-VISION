import time
import platform
import os
import cv2
import sys
import numpy as np

class camera(object):
    #Possible Wide Screen Resolutions: 1280x720(921,600), 960x544(522,240), 800x448(358,400), 640x360(230,400)
    towerCameraRes = [960, 544]
    boulderCameraRes = [800, 448]
    global towerCamera, boulderCamera
    towerCamera = cv2.VideoCapture(0)
    boulderCamera = cv2.VideoCapture(1)
    TOWERIMAGESOURCE = 'idealTower'
    BOULDERIMAGESOURCE = 'boulderLaserFilter'
    imageNumber = 1
    dateTime = str(time.strftime("%m-%d_%H-%M", time.gmtime()))
    towerCaptureLocation = 'capturedImages/tower '  + dateTime+ '/'
    boulderCaptureLocation = 'capturedImages/boulder '  + dateTime + '/'
    outputCaptureLocation = 'capturedImages/output '  + dateTime + '/'
    def __init__(self, Filtertype, Testmode, Manualimagemode, Debugmode, Capturemode, Outputcapturemode, VisionNetworkTable):
        global towerCamera, boulderCamera, frames, lastTime, cameraTime
        global SINGLECAMERAMODE, FILTERTYPE, TESTMODE, MANUALIMAGEMODE, DEBUGMODE, CAPTUREMODE, OUTPUTCAPTUREMODE, visionNetworkTable, pictureNumber
        FILTERTYPE = Filtertype
        TESTMODE = Testmode
        MANUALIMAGEMODE = Manualimagemode
        DEBUGMODE = Debugmode
        CAPTUREMODE = Capturemode
        OUTPUTCAPTUREMODE = Outputcapturemode
        visionNetworkTable = VisionNetworkTable
        if TESTMODE and not CAPTUREMODE:
            cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)
            if MANUALIMAGEMODE:
                cv2.createTrackbar("Image #", "Image", 0, 54, self.changeImage)
        cameraTime = self.getTime()
        pictureNumber = 1
        towerCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.towerCameraRes[0])
        towerCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.towerCameraRes[1])
        #towerCamera.set(cv2.CAP_PROP_FPS, 60)
        #towerCamera.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_RGB)
        self.towerCameraRes[0] = towerCamera.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.towerCameraRes[1] = towerCamera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print ("Tower Camera Resolution = " + str(self.towerCameraRes[0]) + "x" + str(self.towerCameraRes[1]))
        boulderCamera.set(cv2.CAP_PROP_FRAME_WIDTH, self.boulderCameraRes[0])
        boulderCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.boulderCameraRes[1])
        boulderCamera.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_GRAY)
        self.boulderCameraRes[0] = boulderCamera.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.boulderCameraRes[1] = boulderCamera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if (self.boulderCameraRes[0] == 0 and self.boulderCameraRes[1] == 0) or self.boulderCameraRes[1] < 1:
            print ("Only one camera plugged in!")
            SINGLECAMERAMODE = True
        else:
            print ("Boulder Camera Resolution = " + str(self.boulderCameraRes[0]) + "x" + str(self.boulderCameraRes[1]))
            SINGLECAMERAMODE = False
        lastTime = self.getTime()
        if not towerCamera.isOpened():
            print ("error: Tower Camera not initialized")
            os.execl(sys.executable, sys.executable, *sys.argv)
    def sendNumber(self, name, value):
        if DEBUGMODE:
            print (name + ": " + str(value))
        visionNetworkTable.putNumber(name,value)
    def changeImage(self, img):
        self.imageNumber = img+1
    def capturePictures(self, picturesPerSecond, image = None):
        global pictureNumber, cameraTime
        print ("Capturing Tower Images to: " + camera.towerCaptureLocation)
        if not SINGLECAMERAMODE:
            print ("Capturing Boulder Images to: " + camera.boulderCaptureLocation)
        if image is None:
            lastTime = self.getTime()
            if not os.path.exists(self.towerCaptureLocation):
                os.makedirs(self.towerCaptureLocation)
            if not SINGLECAMERAMODE and not os.path.exists(self.boulderCaptureLocation):
                os.makedirs(self.boulderCaptureLocation)
            while(True):
                towerCameraImage = self.pollTower(True)
                boulderCameraImage = self.pollBoulder(True)
                while self.getTime() - lastTime < 1.0/picturesPerSecond:
                    time.sleep(0.1)
                lastTime = self.getTime()
                cv2.imwrite(self.towerCaptureLocation + 'tower (' + str(pictureNumber) + ').jpg', towerCameraImage)
                if not SINGLECAMERAMODE:
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
        originalImage = self.pollTower()
        if FILTERTYPE == "HSV": #Filter with the most accurate tower detection
            HSVImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HSV)
            ThresholdImage = cv2.inRange(HSVImage, np.array([66,64,225]), np.array([96, 255, 255]))
        elif FILTERTYPE == "RGB": #Overall fastest filter
            ThresholdImage = cv2.inRange(originalImage, np.array([0,227,204]), np.array([194,255,255]))
            #ThresholdImage = cv2.inRange(originalImage, np.array([204,227,0]), np.array([255,255,194]))
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
                    cameraPixels = (self.towerCameraRes[0]*self.towerCameraRes[1])
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
            self.sendNumber("goal_x", round(largestContour[0][0],1))
            self.sendNumber("goal_y", round(largestContour[0][1],1))
            self.sendNumber("goal_width", round(largestContour[1][0],1))
            self.sendNumber("goal_height", round(largestContour[1][1],1))
            self.sendNumber("goal_angle", round(largestContour[2],1))
            if TESTMODE:
                cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 2, (0,255,0), 5, 2)
        else:
            self.sendNumber("goal_x", -1)
            self.sendNumber("goal_y", -1)
            self.sendNumber("goal_width", -1)
            self.sendNumber("goal_height", -1)
            self.sendNumber("goal_angle", -1)
        if TESTMODE:
            cv2.imshow("Image", originalImage)
        if OUTPUTCAPTUREMODE:
            self.capturePictures(1, originalImage)
    def processBoulder(self):
        originalImage = self.pollBoulder()
        ThresholdImage = cv2.inRange(originalImage, 60, 255)
        if TESTMODE:    
            cv2.imshow("Image", ThresholdImage)
        if OUTPUTCAPTUREMODE:
            self.capturePictures(1, originalImage)
    def pollTower(self, forceActualCamera = False):
        if MANUALIMAGEMODE and not forceActualCamera:
            imgOriginal = cv2.imread('towerImages/' + self.TOWERIMAGESOURCE + '/' + self.TOWERIMAGESOURCE + ' (' + str(self.imageNumber) + ')_960x540.jpg',1)
            if imgOriginal is None:
                print ("Error: towerCamera frame not read from file")
                return
        else:
            blnFrameReadSuccessfully, imgOriginal = towerCamera.read()
            if not blnFrameReadSuccessfully or imgOriginal is None:
                print ("Error: frame not read from towerCamera")
                return
        return imgOriginal
    def pollBoulder(self, forceActualCamera = False):
        if MANUALIMAGEMODE and not forceActualCamera:
            imgOriginal = cv2.imread('boulderImages/' + self.BOULDERIMAGESOURCE + '/' + self.BOULDERIMAGESOURCE + ' (' + str(self.imageNumber) + ').jpg',1)
            if imgOriginal is None:
                print ("Error: boulderCamera frame not read from file")
                return
        else:
            if SINGLECAMERAMODE:
                blnFrameReadSuccessfully, imgOriginal = towerCamera.read()
            else:
                blnFrameReadSuccessfully, imgOriginal = boulderCamera.read()
            if not blnFrameReadSuccessfully or imgOriginal is None:
                print ("Error: frame not read from boulderCamera")
                return
        imgOriginal = imgOriginal[(int(self.boulderCameraRes[1]/6-self.boulderCameraRes[1])):self.boulderCameraRes[1], 0:self.boulderCameraRes[0]]
        #Area to Keep: [Top Y Value:Bottom Y Value, Top X Value:Bottom X Value]
        return imgOriginal    
    def isTowerCameraOpen(self):
        return towerCamera.isOpened()
    def isBoulderCameraOpen(self):
        return boulderCamera.isOpened()
    def closeCameras(self):
        boulderCamera.release()
        towerCamera.release()
    def getTime(self):
        if platform.system() == "Linux":
            return time.time()
        else:
            return time.clock()