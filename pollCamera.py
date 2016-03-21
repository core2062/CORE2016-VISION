import cv2
import constants
import numpy as np
from threading import Thread
from cv2 import VideoCapture

class camera(object):
    def __init__(self, videoCaptureID, cameraType):
        '''
        @param videoCaptureID: The ID of the video camera to use
        @param cameraType: The type of camera to initialize camera as. Can be either "Tower", "Boulder", "Dummy_Tower", or "Dummy_Boulder"
        '''
        self.mode = cameraType
        self.frameRead = False
        self.stop = False
        if(cameraType == "Dummy_Tower"):
            self.location = ('towerImages/' + constants.TOWERIMAGESOURCE + '/' + constants.TOWERIMAGESOURCE)
        elif(cameraType == "Dummy_Boulder"):
            self.location = ('boulderImages/' + constants.BOULDERIMAGESOURCE + '/' + constants.BOULDERIMAGESOURCE)
        elif(cameraType == "Boulder"):
            self.capture = cv2.VideoCapture(videoCaptureID)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, constants.BOULDERCAMERA_RESOLUTION[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, constants.BOULDERCAMERA_RESOLUTION[1])
            self.capture.set(cv2.CAP_PROP_FPS, constants.BOULDERCAMERA_FPS)
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, constants.BOULDERCAMERA_BRIGHTNESS)
            self.capture.set(cv2.CAP_PROP_SATURATION, constants.BOULDERCAMERA_SATURATION)
            self.capture.set(cv2.CAP_PROP_CONTRAST, constants.BOULDERCAMERA_CONTRAST)
            RESOLUTION = (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            FPS = round(self.capture.get(cv2.CAP_PROP_FPS),3)
            BRIGHTNESS = round(self.capture.get(cv2.CAP_PROP_BRIGHTNESS),3)
            SATURATION = round(self.capture.get(cv2.CAP_PROP_SATURATION),3)
            CONTRAST = round(self.capture.get(cv2.CAP_PROP_CONTRAST),3)
            if RESOLUTION[0] != constants.BOULDERCAMERA_RESOLUTION[0] or RESOLUTION[1] != constants.BOULDERCAMERA_RESOLUTION[1]:
                constants.visionTable.sendError("Boulder camera RESOLUTION not set to: " + str(constants.BOULDERCAMERA_RESOLUTION[0]) + "x" + 
                                                 str(constants.BOULDERCAMERA_RESOLUTION[1]) + ", currently is: " + str(RESOLUTION[0]) + "x" + str(RESOLUTION[1]))
            if FPS != constants.BOULDERCAMERA_FPS:
                constants.visionTable.sendError("Boulder camera FPS not set to: " + str(constants.BOULDERCAMERA_FPS) + ", currently is: " + str(FPS))
            if BRIGHTNESS != constants.BOULDERCAMERA_BRIGHTNESS:
                constants.visionTable.sendError("Boulder camera BRIGHTNESS not set to: " + str(constants.BOULDERCAMERA_BRIGHTNESS) + ", currently is: " + str(BRIGHTNESS))
            if SATURATION != constants.BOULDERCAMERA_SATURATION:
                constants.visionTable.sendError("Boulder camera SATURATION not set to: " + str(constants.BOULDERCAMERA_SATURATION) + ", currently is: " + str(SATURATION))
            if CONTRAST != constants.BOULDERCAMERA_CONTRAST:
                constants.visionTable.sendError("Boulder camera CONTRAST not set to: " + str(constants.BOULDERCAMERA_CONTRAST) + ", currently is: " + str(CONTRAST))
            self.frame = np.zeros((RESOLUTION[0],RESOLUTION[1],3), np.uint8) #Black Image
            Thread(target=self.update, args=()).start()
        else: #Assume tower camera by default in case of typo
            self.capture = cv2.VideoCapture(videoCaptureID)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, constants.TOWERCAMERA_RESOLUTION[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, constants.TOWERCAMERA_RESOLUTION[1])
            self.capture.set(cv2.CAP_PROP_FPS, constants.TOWERCAMERA_FPS)
            self.capture.set(cv2.CAP_PROP_BRIGHTNESS, constants.TOWERCAMERA_BRIGHTNESS)
            self.capture.set(cv2.CAP_PROP_SATURATION, constants.TOWERCAMERA_SATURATION)
            self.capture.set(cv2.CAP_PROP_CONTRAST, constants.TOWERCAMERA_CONTRAST)
            RESOLUTION = (self.capture.get(cv2.CAP_PROP_FRAME_WIDTH), self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            FPS = round(self.capture.get(cv2.CAP_PROP_FPS),3)
            BRIGHTNESS = round(self.capture.get(cv2.CAP_PROP_BRIGHTNESS),3)
            SATURATION = round(self.capture.get(cv2.CAP_PROP_SATURATION),3)
            CONTRAST = round(self.capture.get(cv2.CAP_PROP_CONTRAST),3)
            if RESOLUTION[0] != constants.TOWERCAMERA_RESOLUTION[0] or RESOLUTION[1] != constants.TOWERCAMERA_RESOLUTION[1]:
                constants.visionTable.sendError("Tower camera RESOLUTION not set to: " + str(constants.TOWERCAMERA_RESOLUTION[0]) + "x" + 
                                                 str(constants.TOWERCAMERA_RESOLUTION[1]) + ", currently is: " + str(RESOLUTION[0]) + "x" + str(RESOLUTION[1]))
            if FPS != constants.BOULDERCAMERA_FPS:
                constants.visionTable.sendError("Tower camera FPS not set to: " + str(constants.TOWERCAMERA_FPS) + ", currently is: " + str(FPS))
            if BRIGHTNESS != constants.BOULDERCAMERA_BRIGHTNESS:
                constants.visionTable.sendError("Tower camera BRIGHTNESS not set to: " + str(constants.TOWERCAMERA_BRIGHTNESS) + ", currently is: " + str(BRIGHTNESS))
            if SATURATION != constants.BOULDERCAMERA_SATURATION:
                constants.visionTable.sendError("Tower camera SATURATION not set to: " + str(constants.TOWERCAMERA_SATURATION) + ", currently is: " + str(SATURATION))
            if CONTRAST != constants.BOULDERCAMERA_CONTRAST:
                constants.visionTable.sendError("Tower camera CONTRAST not set to: " + str(constants.TOWERCAMERA_CONTRAST) + ", currently is: " + str(CONTRAST))
            self.frame = np.zeros((RESOLUTION[0],RESOLUTION[1],3), np.uint8) #Black Image
            Thread(target=self.update, args=()).start()
    def update(self):
        while True:
            if self.stop:
                return
            self.frameRead, self.frame = self.capture.read()
    def read(self, imageNumber = 1):
        if self.mode == "Boulder" or self.mode == "Tower":
            return self.frame
        elif self.mode == "Dummy_Boulder":
            self.frame = cv2.imread(self.location + ' (' + str(imageNumber) + ').jpg',1)
            if self.frame is None:
                constants.visionTable.sendError("Frame not read from dummy boulder camera file: " + self.location + ' (' + str(imageNumber) + ').jpg')
                return None
            return self.frame
        else:
            self.frame = cv2.imread(self.location + ' (' + str(imageNumber) + ').jpg',1)
            if self.frame is None:
                constants.visionTable.sendError("Frame not read from dummy tower camera file: " + self.location + ' (' + str(imageNumber) + ').jpg')
                return None
            return self.frame
    def close(self):
        self.stop = True
        if self.mode == "Boulder" or self.mode == "Tower":
            self.capture.release()
    def isOpen(self):
        if self.mode == "Boulder" or self.mode == "Tower":
            return self.capture.isOpened()
        else:
            return True
    def isFrameRead(self):
        if self.mode == "Boulder" or self.mode == "Tower":
            return self.frameRead
        else:
            return True
    def getCameraType(self):
        return self.mode
    def inputFileLocation(self):
        return self.location
    def getWidth(self):
        if self.mode == "Boulder" or self.mode == "Tower":
            return self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        else:
            return self.frame.shape[1]
    def getHeight(self):
        if self.mode == "Boulder" or self.mode == "Tower":
            return self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        else:
            return self.frame.shape[0]