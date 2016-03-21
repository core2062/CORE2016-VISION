import os
import constants
import cv2
import numpy as np
from time import sleep

def processTower(originalImage):
    filteredContours = []
    if constants.FILTERTYPE == "HSV": #Filter with the most accurate tower detection
        HSVImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HSV)
        ThresholdImage = cv2.inRange(HSVImage, constants.HSV_LOWER, constants.HSV_UPPER)
    elif constants.FILTERTYPE == "BGR": #Overall fastest filter
        ThresholdImage = cv2.inRange(originalImage, constants.BGR_LOWER, constants.BGR_UPPER)
    elif constants.FILTERTYPE == "HLS": #Filter with the most consistent tower detection
        HLSImage = cv2.cvtColor(originalImage,cv2.COLOR_BGR2HLS)
        ThresholdImage = cv2.inRange(HLSImage, constants.HLS_LOWER, constants.HLS_UPPER)
    _,contours,_ = cv2.findContours(ThresholdImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largestArea = 0
    largestContour = None
    secondLargestContour = None
    if contours is not None:
        for x in contours:
            centroid,size,angle = cv2.minAreaRect(x)
            area = abs(size[0]*size[1])
            if area != 0:
                hull = cv2.convexHull(x)
                contourArea = cv2.contourArea(x)
                hull_area = cv2.contourArea(hull)
                solidity = float(contourArea)/hull_area
                cameraPixels = (constants.TOWERCAMERA_RESOLUTION[0]*constants.TOWERCAMERA_RESOLUTION[1])
                if (solidity < 0.4 and area/cameraPixels > 0.001714 and size[1]/cameraPixels > 0.00008573):
                    if area > largestArea:
                        secondLargestContour = largestContour
                        largestContour = centroid,size,angle,x
                        largestArea = area
                    if constants.DEBUGLEVEL >= 3:
                        filteredContours.append(x)
        if constants.DEBUGLEVEL >= 3 and largestContour is not None and secondLargestContour is not None:
            cv2.drawContours(originalImage,contours,-1,(0,255,255),2)
            cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
            if largestContour[0][0] < secondLargestContour[0][0]:
                cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 3, (20,255,57), 5, 2)
                cv2.circle(originalImage, (int(secondLargestContour[0][0]),int(secondLargestContour[0][1])), 2, (0,100,255), 5, 2)
            else:
                cv2.circle(originalImage, (int(secondLargestContour[0][0]),int(secondLargestContour[0][1])), 3, (20,255,57), 5, 2)
                cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 2, (0,100,255), 5, 2)
        elif constants.DEBUGLEVEL >= 3 and largestContour is not None:
            cv2.drawContours(originalImage,contours,-1,(0,255,255),2)
            cv2.drawContours(originalImage,filteredContours,-1,(0,0,255),2)
            cv2.circle(originalImage, (int(largestContour[0][0]),int(largestContour[0][1])), 3, (20,255,57), 5, 2)
    if largestContour is not None and secondLargestContour is not None:
        if largestContour[0][0] < secondLargestContour[0][0]: #Find which contour is farther right
            constants.visionTable.sendNumber("leftGoal_x", round(largestContour[0][0],1))
            constants.visionTable.sendNumber("leftGoal_y", round(largestContour[0][1],1))
            constants.visionTable.sendNumber("leftGoal_width", round(largestContour[1][0],1))
            constants.visionTable.sendNumber("leftGoal_height", round(largestContour[1][1],1))
            constants.visionTable.sendNumber("leftGoal_angle", round(largestContour[2],1))
            constants.visionTable.sendNumber("rightGoal_x", round(secondLargestContour[0][0],1))       
            constants.visionTable.sendNumber("rightGoal_y", round(secondLargestContour[0][1],1))       
            constants.visionTable.sendNumber("rightGoal_width", round(secondLargestContour[1][0],1))   
            constants.visionTable.sendNumber("rightGoal_height", round(secondLargestContour[1][1],1))  
            constants.visionTable.sendNumber("rightGoal_angle", round(secondLargestContour[2],1))
        else:
            constants.visionTable.sendNumber("leftGoal_x", round(secondLargestContour[0][0],1))
            constants.visionTable.sendNumber("leftGoal_y", round(secondLargestContour[0][1],1))
            constants.visionTable.sendNumber("leftGoal_width", round(secondLargestContour[1][0],1))
            constants.visionTable.sendNumber("leftGoal_height", round(secondLargestContour[1][1],1))
            constants.visionTable.sendNumber("leftGoal_angle", round(secondLargestContour[2],1))
            constants.visionTable.sendNumber("rightGoal_x", round(largestContour[0][0],1))       
            constants.visionTable.sendNumber("rightGoal_y", round(largestContour[0][1],1))       
            constants.visionTable.sendNumber("rightGoal_width", round(largestContour[1][0],1))   
            constants.visionTable.sendNumber("rightGoal_height", round(largestContour[1][1],1))  
            constants.visionTable.sendNumber("rightGoal_angle", round(largestContour[2],1))
        if largestContour[1][0]*largestContour[1][1] < secondLargestContour[1][0]*secondLargestContour[1][1]:
            constants.visionTable.sendNumber("largestGoal_x", round(secondLargestContour[0][0],1))
            constants.visionTable.sendNumber("largestGoal_y", round(secondLargestContour[0][1],1))
            constants.visionTable.sendNumber("largestGoal_width", round(secondLargestContour[1][0],1))
            constants.visionTable.sendNumber("largestGoal_height", round(secondLargestContour[1][1],1))
            constants.visionTable.sendNumber("largestGoal_angle", round(secondLargestContour[2],1))
        else:
            constants.visionTable.sendNumber("largestGoal_x", round(largestContour[0][0],1))
            constants.visionTable.sendNumber("largestGoal_y", round(largestContour[0][1],1))
            constants.visionTable.sendNumber("largestGoal_width", round(largestContour[1][0],1))
            constants.visionTable.sendNumber("largestGoal_height", round(largestContour[1][1],1))
            constants.visionTable.sendNumber("largestGoal_angle", round(largestContour[2],1))
    elif largestContour is not None:
        constants.visionTable.sendNumber("leftGoal_x", round(largestContour[0][0],1))
        constants.visionTable.sendNumber("leftGoal_y", round(largestContour[0][1],1))
        constants.visionTable.sendNumber("leftGoal_width", round(largestContour[1][0],1))
        constants.visionTable.sendNumber("leftGoal_height", round(largestContour[1][1],1))
        constants.visionTable.sendNumber("leftGoal_angle", round(largestContour[2],1))
        constants.visionTable.sendNumber("rightGoal_x", round(largestContour[0][0],1))
        constants.visionTable.sendNumber("rightGoal_y", round(largestContour[0][1],1))
        constants.visionTable.sendNumber("rightGoal_width", round(largestContour[1][0],1))
        constants.visionTable.sendNumber("rightGoal_height", round(largestContour[1][1],1))
        constants.visionTable.sendNumber("rightGoal_angle", round(largestContour[2],1))
        constants.visionTable.sendNumber("largestGoal_x", round(largestContour[0][0],1))
        constants.visionTable.sendNumber("largestGoal_y", round(largestContour[0][1],1))
        constants.visionTable.sendNumber("largestGoal_width", round(largestContour[1][0],1))
        constants.visionTable.sendNumber("largestGoal_height", round(largestContour[1][1],1))
        constants.visionTable.sendNumber("largestGoal_angle", round(largestContour[2],1))
    else:
        constants.visionTable.sendNumber("leftGoal_x", -1)
        constants.visionTable.sendNumber("leftGoal_y", -1)
        constants.visionTable.sendNumber("leftGoal_width", -1)
        constants.visionTable.sendNumber("leftGoal_height", -1)
        constants.visionTable.sendNumber("leftGoal_angle", -1)
        constants.visionTable.sendNumber("rightGoal_x", -1)
        constants.visionTable.sendNumber("rightGoal_y", -1)
        constants.visionTable.sendNumber("rightGoal_width", -1)
        constants.visionTable.sendNumber("rightGoal_height", -1)
        constants.visionTable.sendNumber("rightGoal_angle", -1)
        constants.visionTable.sendNumber("largestGoal_x", -1)
        constants.visionTable.sendNumber("largestGoal_y", -1)
        constants.visionTable.sendNumber("largestGoal_width", -1)
        constants.visionTable.sendNumber("largestGoal_height", -1)
        constants.visionTable.sendNumber("largestGoal_angle", -1)
    if constants.DEBUGLEVEL >= 3:
        return originalImage
def processBoulder(originalImage):
    pass