import constants
import os
from threading import Thread
import tkinter as tk
import cv2
import processing

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
        self.rightButtonDown = False
        self.mode = "BGR"
        self.captureType = self.capture.getCameraType()
        if self.captureType == "Dummy_Tower" or self.captureType == "Dummy_Boulder":
            if(self.captureType == "Dummy_Tower"):
                path = ('towerImages/' + constants.TOWERIMAGESOURCE)
            elif(self.captureType == "Dummy_Boulder"):
                path = ('boulderImages/' + constants.BOULDERIMAGESOURCE)
            self.file_count = int(sum(os.path.isfile(os.path.join(path, f)) for f in os.listdir(path)))-1
            cv2.createTrackbar("Image #", "Image", 0, self.file_count, self.imageSlider_event)
        Thread(target=self.update, args=()).start()
    def update(self):
        #self.gui = gui()
        while not self.stop:
            #self.gui.update(self.mode)
            if True:#self.gui.getProcessingRadio():
                self.image = processing.processTower(self.capture.read(self.imageNumber))
            else:
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
        
class gui():
    def __init__(self):
        self.value = 0
        self.value1UpperScale = tk.IntVar(value=255)
        self.value1LowerScale = tk.IntVar(value=0)
        self.value2UpperScale = tk.IntVar(value=255)
        self.value2LowerScale = tk.IntVar(value=0)
        self.value3UpperScale = tk.IntVar(value=255)           
        self.value3LowerScale = tk.IntVar(value=0)
        self.root = tk.Tk()
        self.root.title("Settings")
        self.processingRadio = tk.IntVar()
        self.value1UpperScale = tk.Scale(self.root, from_=0, to=255, length=200, orient=tk.HORIZONTAL,varible=self.value1UpperScale,showvalue=True,command=self.value1UpperScaleUpdate)
        self.value1UpperScale.grid(row=1,column=1)
        self.value2UpperScale = tk.Scale(self.root, from_=0, to=255, length=200, orient=tk.HORIZONTAL,varible=self.value2UpperScale,showvalue=True,command=self.value1LowerScaleUpdate)
        self.value2UpperScale.grid(row=1,column=2)
        self.value3UpperScale = tk.Scale(self.root, from_=0, to=255, length=200, orient=tk.HORIZONTAL,varible=self.value3UpperScale,showvalue=True,command=self.value2UpperScaleUpdate)
        self.value3UpperScale.grid(row=1,column=3)
        self.value1LowerScale = tk.Scale(self.root, from_=0, to=255, length=200, orient=tk.HORIZONTAL,varible=self.value1LowerScale,showvalue=True,command=self.value2LowerScaleUpdate)
        self.value1LowerScale.grid(row=2,column=1)
        self.value2LowerScale = tk.Scale(self.root, from_=0, to=255, length=200, orient=tk.HORIZONTAL,varible=self.value2LowerScale,showvalue=True,command=self.value3UpperScaleUpdate)
        self.value2LowerScale.grid(row=2,column=2)
        self.value3LowerScale = tk.Scale(self.root, from_=0, to=255, length=200, orient=tk.HORIZONTAL,varible=self.value3LowerScale,showvalue=True,command=self.value3LowerScaleUpdate)
        self.value3LowerScale.grid(row=2,column=3)
        self.value1Label = tk.Label(self.root, text="")
        self.value1Label.grid(row=0,column=1,sticky='W')
        self.value2Label = tk.Label(self.root, text="")
        self.value2Label.grid(row=0,column=2,sticky='W')
        self.value3Label = tk.Label(self.root, text="")
        self.value3Label.grid(row=0,column=3,sticky='W')
        self.upperLabel = tk.Label(self.root, text="Upper")
        self.upperLabel.grid(row=1,column=0)
        self.lowerLabel = tk.Label(self.root, text="Lower")
        self.lowerLabel.grid(row=2,column=0)
        self.processingOnRadio = tk.Radiobutton(self.root, text="Processing On", variable=self.processingRadio, value=1)
        self.processingOnRadio.grid(row=3,column=1)
        self.processingOffRadio = tk.Radiobutton(self.root, text="Processing Off", variable=self.processingRadio, value=2)
        self.processingOffRadio.grid(row=3,column=2)
        self.processingOffRadio.select()
    def update(self, mode):
        self.value1Label["text"] = mode[0]
        self.value2Label["text"] = mode[1]
        self.value3Label["text"] = mode[2]
        self.root.update()
        self.root.update_idletasks()
    def getProcessingRadio(self):
        if(self.processingRadio.get() == "Processing On"):
            return True
        else:
            return False