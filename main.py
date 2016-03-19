import pollCamera
import constants
import cv2
import networkTableManager
from time import sleep

def init():
    constants.visionTable = networkTableManager.networkTable()
    constants.towerCamera = pollCamera.camera(0, "Tower")
    cv2.namedWindow("Image",cv2.WINDOW_AUTOSIZE)
def deInit():
    constants.towerCamera.close()
    cv2.destroyAllWindows()
def main():
    sleep(1)
    while cv2.waitKey(1) != 27:
        cv2.imshow("Image", constants.towerCamera.read())
        pass
    deInit()
if __name__ == '__main__':
    init()
    main()