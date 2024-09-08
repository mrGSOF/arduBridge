#!/usr/bin/env python
"""
    This file is part of GSOF_ArduBridge.

    GSOF_ArduBridge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GSOF_ArduBridge is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GSOF_ArduBridge.  If not, see <https://www.gnu.org/licenses/>.

Class to access the external-GPIO connected to the Arduino-Bridge via I2C.
This class is using the BridgeSerial class object to generate I2C-Bus cycles
over with the Arduino-Bridge hardware.
"""

"""
The Max3700 is an I2C General Purpose Input/Output (GPIO) device connected.
The class includes methods to control it over the I2C bus.
The __init__ method initializes the class with a reference to an I2C object and the
device ID of the external GPIO device. It also has some class variables for storing the
I2C register addresses for various functions of the device, such as setting the device
mode or reading/writing to the device ports.
The class has several methods for interacting with the external GPIO device.
The modeSet method can be used to set the operating mode of the device, either "normal" or "shutdown".
The modeGet method can be used to read the current operating mode of the device.
The bankModeSet and bankModeGet methods can be used to set and get the direction
(input or output) of the individual pins on the device. The portWrite and portRead methods
can be used to write values to and read values from the device ports, respectively.
The pinMode and pinRead methods can be used to set the direction and read the value
of an individual pin, respectively.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

class Max3700ExtGPIO():
    def __init__(self, i2c=False, devID=0x00, pinZeroOffset=8, logger=None):
        self.ID = 'MAX3700-ID 0x%02x'%(devID)
        self.logger = logger
        self.i2c = i2c
        self.devID = devID
        self.portRegOffset = 0x44
        self.pinRegOffset = 0x24
        self.bankModeOffset = 0x09
        self.pinZeroOffset = pinZeroOffset
        
        self.modeReg = 0x04
        self.RES = {1:'OK', 0:'ERR', -1:'ERR'}
        self.DIR = {0:'Active-Low', 1:'Active-High', 2:'Input without pullup', 3:'Input + pullup'}
        self.MODE = {0:'Shutdown', 1:'Normal'}
        self.tDet = {0:'Disable', 1:'Enable'}

    def modeSet(self, mode=1, transitionDetection=0) -> list:
        """mode: 0 - Shutdown; 1 - Normal operation. transitionDetection: 0 - Disable; 1 - Enable"""
        if mode != 0:
            mode = 1
        val = mode
        val |= (transitionDetection&0x1)<<7
        reply = self.i2c.writeRegister(self.devID, self.modeReg, [mode])
        if self.logger != None:
            self.logger.debug(f"{self.ID}: MODE-Set: {self.RES[reply[0]]}")
        return reply[0]

    def modeGet(self) -> list:
        """"""
        reply = self.i2c.readRegister(self.devID, self.modeReg, 1)
        if self.logger != None:
            if reply != -1:
                mode = reply[0]&1
                td = (reply[0]>>7)&1
                self.logger.debug(f"{self.ID}: MODE-Get: {self.MODE[mode]}, Transition-Detection: {self.tDet[td]}")
        return reply

    def bankModeSet(self, val=0x55, B=0, N=7) -> list:
        if (B+N) > 7:
            N = 7-B #Set upto 7 banks
        reply = self.i2c.writeRegister(self.devID, self.bankModeOffset+B, [val]*N)
        if self.logger != None:
            self.logger.debug( f"{self.ID}: bankMode Set: {self.RES[reply[0]]}")
        return reply

    def bankModeGet(self, B=0, N=7) -> list:
        if (B+N) > 7:
            N = 7-B #Get upto 7 banks
        reply = self.i2c.readRegister(self.devID, self.bankModeOffset+B, N)
        if self.logger != None:
            self.logger.debug( f"{self.ID}: bankMode: {str(reply)}")
        return reply

##    def pinMode(self, pin, mode):
##        """
##        Set the mode of the specific pin# on the MX3700
##        """
##        reg = pin/4 +self.pinModeOffset
##        bitField = pin%4
##        vDat = [ord('D'), pin, mode]
##        self.comm.send(vDat)
##        reply = self.comm.receive(1)
##        return reply[0]

    def pinWrite(self, pin, valList):
        """Set the state of the specific pin(s)# on the MX3700"""
        if type(valList) == int:
            valList = [valList]
        for val in valList:
            if (val != 0):
                val = 1
            pinReg = self.pinRegOffset +self.pinZeroOffset +pin
            reply = self.i2c.writeRegister(self.devID, pinReg, [val])
            if self.logger != None:
                self.logger.debug(f"{self.ID}: PIN{pin}-Set: {val} - {self.RES[reply[0]]}")
            pin += 1
        return reply[0]

    def portWrite(self, port, val):
        """Set the state of the specific port# on the MX3700"""
        portReg = self.portRegOffset +self.pinZeroOffset +port
        reply = self.i2c.writeRegister(self.devID, portReg, [val&0xff])
        if self.logger != None:
            self.logger.debug(f"{self.ID}: PORT{port}-Set: {self.RES[reply[0]]}")
        return reply[0]

    def pinRead(self, pinList):
        """Read the state of the specific pin(s)# on the MX3700"""
        if type(pinList) == int:
            pinList = [pinList]
        result = []
        for pin in pinList:
            pinReg = self.pinRegOffset +self.pinZeroOffset +pin
            reply = self.i2c.readRegister(self.devID, pinReg, 1)
            if reply != -1:
                if self.logger != None:
                    self.logger.debug(f"{self.ID}: PIN{pin} = {reply[0]}")
                result.append(reply[0])
            else:
                if self.logger != None:
                    self.logger.error(f"{self.ID}: PIN{pin}-Get: Error")
                result.append(-1)
        return result
        
    def portRead(self, port):
        """Read the state of the specific port# on the MX3700"""
        portReg = self.portRegOffset +self.pinZeroOffset +port
        reply = self.i2c.readRegister(self.devID, portReg, 1)
        if reply != -1:
            if self.logger != None:
                self.logger.debug("%s: PORT%d = 0x%02x (%s)" % (self.ID, port, reply[0], bin(reply[0])))
            return reply[0]
        if self.logger != None:
            self.logger.error(f"{self.ID}: PORT{port}-Get: Error")
        return -1
