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
"""

"""
The PCA9505 is an I2C General Purpose Input/Output (GPIO) device.
The class includes methods to control it over the I2C bus.
The __init__ method initializes the class with a reference to an I2C object and the
device ID of the external GPIO device. It also has some class variables for storing the
I2C register addresses for various functions of the device, such as reading/writing to the device ports.
The class has several methods for interacting with the external GPIO device.
The modeSet and modeGet methods are present for software competability with the MAX3700 class.
The bankModeSet and bankModeGet methods can be used to set and get the direction
(input or output) of the individual pins on the device. The portWrite and portRead methods
can be used to write values to and read values from the device ports, respectively.
The pinMode and pinRead methods can be used to set the direction and read the value
of an individual pin, respectively.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2024"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

from GSOF_ArduBridge import CON_prn

def pinPortMask(pin):
    port  = int(pin/8)
    pin   = int(pin%8)
    mask  = int(1<<pin)
    return (pin, port, mask)

class PCA9505():
    maxPorts = 5 #< But only 5 are used
    IP_base  = 0x0
    OP_base  = 0x08
    PI_base  = 0x10
    IOC_base = 0x18
    MSK_base = 0x20
    AUTO_INC = 0x80
    RES = {1:'OK', 0:'ERR', -1:'ERR'}
    DIR = {0:'Output', 1:'Input'}
    POL = {0:'Active-High', 1:'Active-Low'}
    MODE = {0:'Shutdown', 1:'Normal'}
    
    def __init__(self, i2c=False, devID=0x20, pinZeroOffset=8, v=False):
        self.ID = 'PCA9505-ID 0x%02x'%(devID)
        self.v = v
        self.i2c = i2c
        self.devID = devID
        self.portOut = [0]*self.maxPorts

    def _getRegisters(self, reg, N):
        return self.i2c.readRegister(self.devID, self.AUTO_INC|reg, N)

    def _setRegisters(self, reg, vals):
        return self.i2c.writeRegister(self.devID, self.AUTO_INC|reg, vals)
        
    def modeSet(self, mode=1, transitionDetection=0) -> list:
        return -1

    def modeGet(self) -> list:
        return -1
        
    def setPortMode(self, port=0, val=[0xff]) -> list:
        if (type(val) == int) or (type(val) == float):
            val = [val]
        N = len(val)
        if (port+N) > self.maxPorts:
            N = self.maxPorts-port
            val = val[0:N+1]
        reply = self._setRegisters(self.IOC_base+port, val)
        CON_prn.printf( '%s: port direction Set: %s', par=(self.ID, str(self.RES[reply[0]])) )
        return reply

    def bankModeSet(self, port=0, N=5) -> list:
        return setPortMode(val, port, N)
    
    def getPortMode(self, port=0, N=5) -> list:
        if (port+N) > self.maxPorts:
            N = self.maxPorts-port
        reply = self._getRegisters(self.IOC_base+port, N)
        CON_prn.printf( '%s: port direction: %s {bit: 0-%s}', par=(self.ID, str(reply), self.MODE[0]) )
        return reply

    def bankModeGet(self, B=0, N=5) -> list:
        return self.getBankMode(B, N)

##    def pinMode(self, pin, mode):
##        """
##        Set the mode of the specific pin#
##        """
##        reg = pin/4 +self.pinModeOffset
##        bitField = pin%4
##        vDat = [ord('D'), pin, mode]
##        self.comm.send(vDat)
##        reply = self.comm.receive(1)
##        if self.v:
##            CON_prn.printf('DIR%d: %s - %s', par=(pin, self.DIR[mode], self.RES[reply[0]]), v=True)
##        return reply[0]

    def getPort(self, port):
        """Read the state of the specific port#"""
        portReg = self.IP_base +port
        reply = self._getRegisters(portReg, 1)
        if reply != -1:
            CON_prn.printf('%s: PORT%d = 0x%02x (%s)', par=(self.ID, port, reply[0], bin(reply[0])), v=self.v)
            return reply[0]
        CON_prn.printf('%s: PORT%d-Get: Error', par=(self.ID, port), v=self.v)
        return -1

    def portRead(self, port):
        return self.getPort(port)

    def setPort(self, port, val):
        """Set the state of the specific port#"""
        if port < self.maxPorts:
            self.portOut[port] = val
            portReg = self.OP_base +port
            reply = self._setRegisters(portReg, [val&0xff])
            if self.v:
                CON_prn.printf('%s: POPT%d-Set: %s', par=(self.ID, port, self.RES[reply[0]]), v=True)
            return reply[0]
        return -1

    def portWrite(self, port, val):
        return self.setPort(port, val)

    def getPin(self, pinList):
        """Read the state of the specific pin(s)#"""
        if type(pinList) == int:
            pinList = [pinList]
        result = []
        for pin in pinList:
            _pin, _port, _mask = pinPortMask(pin)
            reply = self.getPort(_port, 1)
            if reply != -1:
                reply[0] = (reply[0]>>_pin)&1
                CON_prn.printf('%s: PIN%d = %d', par=(self.ID, pin, reply[0]), v=self.v)
                result.append(reply[0])
            else:
                CON_prn.printf('%s: PIN%d-Get: Error', par=(self.ID, pin), v=self.v)
                result.append(-1)
        return result

    def pinRead(self, pin):
        return self.getPin(pin)

    def _setPin(self, pin, val) -> int:
        _pin, port, mask = pinPortMask(pin)
        print(_pin, port, hex(mask))
        pVal = self.portOut[port]
        if (val != 0):
            pVal |= mask        #< Set bit
        else:
            pVal &= (mask^0xff) #< Clear bit
        return (port, pVal)

    def setPin(self, pin, valList):
        """Set the state of the specific pin(s)#"""
        if type(valList) == int:
            valList = [valList]

        for val in valList:
            port, pVal = self._setPin(pin, val)
            reply = self.setPort(port, [pVal])
            CON_prn.printf('%s: PIN%d-Set: %d - %s', par=(self.ID, pin, val, self.RES[reply[0]]), v=self.v)
            pin += 1
        return reply[0]

    def pinWrite(self, pin, val):
        return self.setPin(pin, valList)

if __name__ == "__main__":
    gpio = PCA9505()
    gpio.portOut[1] = 0
    print(gpio.portOut[1])
    gpio.portOut[1] = gpio._setPin(10, 1)
    print(gpio.portOut[1])

    gpio.portOut[2] = 0xff
    print(gpio.portOut[2])
    gpio.portOut[2] = gpio._setPin(22, 0)
    print(gpio.portOut[2])
