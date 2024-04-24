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
This class is using the BridgeSerial class object to communicate over serial
with the GSOF-Arduino-Bridge firmware.
"""

"""
Class to manage external General Purpose Input-Output (GPIO) cards.
Defines a class ExtGpioStack, which has methods to initialize the connection to the external GPIO,
set the mode (input or output) of a specific pin, write a value to a specific pin, and read the value of a specific pin.
It also has a method pin2dev which maps a pin number to the device ID of the external GPIO to which it is connected.
"""
__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2024"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time
from GSOF_ArduBridge import CON_prn

class ExtGpioStack():
    self.RES = {1:'OK', 0:'ERR', -1:'ERR'}
    def __init__(self, extGpioStack=[], v=False):
        self.v = v
        self.extGpioStack = extGpioStack
        self.pin2pin = pin2pin

    def init(self):
        self.ExtGpio = []
        for board in self.extGpioStack:
            print('\nConfiguring port-extenderID 0x%02x'%(dev.devID))
            dev = board["dev"]
            dev.v = self.v
            dev.getAllPinsModes()
            dev.setAllPinsToOutput()
            dev.getAllPinsModes()
            dev.clearAllPins()
            self.ExtGpio.append( board )

    def setPin(self, pin, valList):
        """Set the state of the specific pin(s)# on the Electrode-Driver-Stack"""
        pin -= 1
        if type(valList) == int:
            valList = [valList]
        for pin, val in zip(range(pin, pin+len(valList)), valList):
            if (val != 0):
                val = 1
            _dev, _pin = self._pin2dev(pin)
            if _dev != None:
                reply = dev.setPin(_pin, val)
                CON_prn.printf('ExtPinSet%d: %d - %s', par=(pin, val, self.RES[reply]), v=self.v)
            else:
                CON_prn.printf('ExtPinSet%d: Out of range', par=(pin), v=self.v)
                return -1
        return 1

    def getPin(self, pinList) -> list:
        """Read the state of the specific pin(s)# on the Electrode-Driver-Stack"""
        if type(pinList) == int:
            pinList = [pinList]
        result = []
        for pin in pinList:
            _pin, _dev = self._pin2dev(pin)
            if dev != None:
                val = dev.getPin(_pin)
                CON_prn.printf('ExtPin%d: %d', par=(pin, val), v=self.v)
                result.append(val)
            else:
                CON_prn.printf('ExtPin%d: Out of range', par=(pin), v=self.v)
                return -1
        return result

    def pulsePin(self, pin, onTime) -> int:
        """Pulse the the specific pin# on the Electrode-Driver-Stack of onTime (sec)"""
        self.setPin(pin, 1)
        time.sleep(onTime)
        self.setPin(pin, 0)
        return 1

    def _pin2dev( self, pin ):
        """ """
        for board in self.extGpioStack:
            if (pin >= board["firstPin"]) and (pin <= board["lastPin"]):
                dev = board["dev"]
                pin = pin -board["firstPin"]
                return (pin, dev)
        return None
