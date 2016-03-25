from networktables import NetworkTable
import constants
import functions
import platform
import time

'''
Network Table Manager
'''
class networkTable(object):
    def __init__(self, ip, name):
        NetworkTable.setIPAddress(ip)
        NetworkTable.setClientMode()
        NetworkTable.initialize()
        self.visionNetworkTable = NetworkTable.getTable(name)
        if constants.SENDTOSMARTDASHBOARD:
            constants.smartDashboard = NetworkTable.getTable("SmartDashboard")
    def sendNumber(self, name, value):
        if constants.DEBUGLEVEL >= 4:
            print (name + ": " + str(value))
        self.visionNetworkTable.putNumber(name,value)
    def getString(self, name, default = ""):
        value = self.visionNetworkTable.getString(name, default)
        if value == "":
            self.sendError("Could not read: " + name + " from vision network table")
        return value
    def sendError(self, message):
        if True:
            print ("ERROR[" + str(round(functions.getTime(),3)) + "]: " + message)
        self.visionNetworkTable.putString("Debug", message)
    def sendInfo(self, message):
        if True:
            print ("INFO[" + str(round(functions.getTime(),3)) + "]: " + message)
        self.visionNetworkTable.putString("Debug", message)