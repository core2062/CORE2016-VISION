import constants
import os
from threading import Thread
import cv2

class SUDO(object):
    def __init__(self, cameraInput):
        cv2.setMouseCallback("Image", self.mouse_event)
        self.capture = cameraInput
        self.image = self.capture.read()
        self.stop = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.imageNumber = 1
        self.value1 = 0
        self.value2 = 0
        self.value3 = 0
        #self.widthRatio = self.capture.getWidth()/
        self.rightButtonDown = False
        self.mode = "BGR"
        self.captureType = self.capture.getCameraType()
        if self.captureType == "Dummy_Tower" or self.captureType == "Dummy_Boulder":
            if(self.captureType == "Dummy_Tower"):
                path = ('towerImages/' + constants.TOWERIMAGESOURCE)
            elif(self.captureType == "Dummy_Boulder"):
                path = ('boulderImages/' + constants.BOULDERIMAGESOURCE)
            self.file_count = int(sum(os.path.isfile(os.path.join(path, f)) for f in os.listdir(path))/2)-1
            cv2.createTrackbar("Image #", "Image", 0, self.file_count, self.imageSlider_event)
        Thread(target=self.update, args=()).start()
    def update(self):
        while not self.stop:
            self.image = self.capture.read(self.imageNumber)
            modeText = "MODE = " + self.mode + "; "
            locationText = "X: " + str(self.mouse_x) + "; Y: " + str(self.mouse_y) + "; "
            valueText = self.mode[0] + ": " + str(self.value1) + ", " + self.mode[1] + ": " + str(self.value2) + ", "  +  self.mode[2] + ": " + str(self.value3)
            cv2.putText(self.image, modeText + locationText + valueText, (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (50,255,50), 2, cv2.LINE_AA)
    def close(self):
        self.stop = True
    def imageSlider_event(self, num):
        self.imageNumber = num + 1
    def mouse_event(self, event, x, y, flags, param):
        updateValues = False
        if event == cv2.EVENT_MOUSEMOVE:
            self.mouse_x = x
            self.mouse_y = y
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.rightButtonDown = True
        elif event == cv2.EVENT_RBUTTONUP and self.rightButtonDown:
            self.rightButtonDown = False
            if self.mode == "BGR":
                self.mode = "HSV"
            elif self.mode == "HSV":
                self.mode = "HLS"
            else:
                self.mode = "BGR"
            updateValues = True
        if event == cv2.EVENT_LBUTTONDOWN or updateValues:
            if self.mode == "BGR":
                img = self.image
                self.value1 = img.item(self.mouse_y,self.mouse_x,0)
                self.value2 = img.item(self.mouse_y,self.mouse_x,1)
                self.value3 = img.item(self.mouse_y,self.mouse_x,2)
            elif self.mode == "HSV":
                img = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
                self.value1 = img.item(self.mouse_y,self.mouse_x,0)
                self.value2 = img.item(self.mouse_y,self.mouse_x,1)
                self.value3 = img.item(self.mouse_y,self.mouse_x,2)
            else:
                img = cv2.cvtColor(self.image, cv2.COLOR_BGR2HLS)
                self.value1 = img.item(self.mouse_y,self.mouse_x,0)
                self.value2 = img.item(self.mouse_y,self.mouse_x,1)
                self.value3 = img.item(self.mouse_y,self.mouse_x,2)
    def getImage(self):
        return self.image