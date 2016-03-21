import constants
import platform
import time

global lastTime, frames
lastTime = 0
frames = 0
def getTime():
    if platform.system() == "Linux":
        return time.time()
    else:
        return time.clock()
def calculateFPS():
    currentTime = getTime()
    global lastTime, frames
    deltaTime = (currentTime - lastTime)
    if(deltaTime >= 1):
        fps = round(frames/(currentTime - lastTime),1)
        constants.visionTable.sendNumber("FPS", fps)
        if 4 > constants.DEBUGLEVEL >= 1:
            print("FPS: " + str(fps))
        frames = 1.0
        lastTime = currentTime
    else:
        frames += 1.0