import cv2
import os
import numpy as np
import networktables

TESTMODE = True
MANUALIMAGEMODE = True
towerCameraRes = [1280.0, 720.0]
ballCameraRes = [1280.0, 720.0]
imageNumber = 2

def processTowerCamera(camera):
    filteredContours = []
    originalImage = pollCamera(camera)
    blurredImage = cv2.blur(originalImage, (6, 6))
    RGBImage = cv2.cvtColor(blurredImage, cv2.COLOR_BGR2RGB)
    RBGThresholdImage = cv2.inRange(RGBImage, np.array([69,122,197]), np.array([255, 255, 255]))
    _,contours,hierarchy = cv2.findContours(RBGThresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for x in contours:
        if cv2.contourArea(x) < 2000 and cv2.contourArea(x) > 1200:
            filteredContours.append(x)
    cv2.drawContours(RBGThresholdImage,filteredContours,-1,(255,255,255),3)
    cv2.imshow("output", RBGThresholdImage)
    #end def

def processBallCamera(camera):
    originalImage = pollCamera(camera)
    originalImage
#end def    
    
def pollCamera(camera):
    if MANUALIMAGEMODE == True:
        imgOriginal = cv2.imread('towerImages/tower (' + str(imageNumber) + ').jpg',1)
    else:
        blnFrameReadSuccessfully, imgOriginal = camera.read()
        if not blnFrameReadSuccessfully or imgOriginal is None:
            print "error: frame not read from towerCamera"
            return
        #end if
    #end else
    return imgOriginal
#end def
        
def main():
    towerCamera = cv2.VideoCapture(0)
    #ballCamera = cv2.VideoCapture(1)
    towerCamera.set(cv2.CAP_PROP_FRAME_WIDTH, towerCameraRes[0])
    towerCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, towerCameraRes[1])
    print "Tower Camera Resolution = " + str(towerCamera.get(cv2.CAP_PROP_FRAME_WIDTH)) + "x" + str(towerCamera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if towerCamera.isOpened() == False:
        print "error: Tower Camera not initialized"
        os.system("pause")
        return
    # end if
    
    while cv2.waitKey(1) != 27 and towerCamera.isOpened(): #and ballCamera.isOpened()
        processTowerCamera(towerCamera)
        #end if
    # end while
    cv2.destroyAllWindows()
    return

###################################################################################################
if __name__ == "__main__":
    main()
