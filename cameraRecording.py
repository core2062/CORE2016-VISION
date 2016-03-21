import constants
import time
import cv2
import functions
import os

class recorder(object):
    def __init__(self, picturesPerSecond, name):
        '''
        @param picturesPerSecond: The number of pictures to capture each second. Set to 0 to remove limit to number of pictures per second.
        @param name: The name of the captured images.
        '''
        self.picturesPerSecond = picturesPerSecond
        self.pictureNumber = 1;
        self.name = name
        dateTime = str(time.strftime("%m-%d_%H-%M", time.gmtime()))
        self.captureLocation = 'capturedImages/'+ self.name + " " + dateTime + '/'
        constants.visionTable.sendInfo("Capturing " + self.name + " Images to: " + self.captureLocation)
        self.lastTime = functions.getTime()
        if not os.path.exists(self.captureLocation):
            os.makedirs(self.captureLocation)
    def captureImages(self, image):
        if self.picturesPerSecond != 0:
            while functions.getTime() - self.lastTime < 1.0/self.picturesPerSecond:
                time.sleep(0.1)
            self.lastTime = functions.getTime()
        cv2.imwrite(self.captureLocation + self.name + ' (' + str(self.pictureNumber) + ').jpg', image)
        self.pictureNumber += 1
        return image