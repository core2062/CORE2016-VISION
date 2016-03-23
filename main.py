import cv2
import pollCamera
import constants
if constants.DEBUGLEVEL >= 5: 
    import superUser
import processing
import functions
import networkTableManager
import cameraRecording
import os
import sys
from time import sleep

def init():
    if constants.RUNNINGONPI:
        constants.DEBUGLEVEL = 2
        constants.MANUALIMAGEMODE = False
    constants.visionTable = networkTableManager.networkTable()
    if constants.MANUALIMAGEMODE:
        constants.towerCamera = pollCamera.camera(0, "Dummy_Tower")
    else:
        constants.towerCamera = pollCamera.camera(0, "Tower")
    if constants.CAPTUREMODE:
        constants.recorder = cameraRecording.recorder(1, "Tower")
    functions.lastTime = functions.getTime()
    if constants.DEBUGLEVEL >= 3 and not constants.RUNNINGONPI:
        cv2.namedWindow("Image", cv2.WINDOW_AUTOSIZE)
    global towerCamera, visionTable
    towerCamera = constants.towerCamera
    visionTable = constants.visionTable
    timeSpentWaiting = 0
    while not towerCamera.isFrameRead():
        sleep(0.1)
        if timeSpentWaiting > 5:
            visionTable.sendError("Could not open " + towerCamera.getCameraType() + " Camera within 5 seconds, restarting")
            restart()
        timeSpentWaiting += 0.1
    if constants.DEBUGLEVEL >= 5:
        constants.SU = superUser.SUDO(constants.towerCamera)
def deInit():
    constants.towerCamera.close()
    if constants.DEBUGLEVEL >= 5:
        constants.SU.close()
    cv2.destroyAllWindows()
def restart():
    print("Restarting program!")
    os.execl(sys.executable, sys.executable, *sys.argv)
def init_filter():
    constants.DEBUGLEVEL = 3
    return processing.processTower
def main():
    while cv2.waitKey(1) != 27:
        previousTime = functions.getTime()
        if constants.CAPTUREMODE:
            cv2.imshow("Image", constants.recorder.captureImages(towerCamera.read()))
        elif constants.DEBUGLEVEL >= 5:
            cv2.imshow("Image", constants.SU.getImage() and not constants.RUNNINGONPI)
        elif constants.DEBUGLEVEL >= 3 and not constants.RUNNINGONPI:
            cv2.imshow("Image", processing.processTower(towerCamera.read()))
        else:
            processing.processTower(towerCamera.read())
        deltaTime = (1/constants.FPSLIMIT) - (functions.getTime() - previousTime)
        if deltaTime > 0:  
            sleep(deltaTime)
        functions.calculateFPS()
    deInit()
if __name__ == '__main__':
    init()
    main()