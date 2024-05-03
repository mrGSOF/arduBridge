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
__copyright__ = "Copyright 2024"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"
import time

class HVSW_Driver_base():
    def __init__(self, startPin, endPin):
        self.assignPinRange(startPin, endPin)
        
    def assignPinRange(startPin, endPin):
        self.startPin = startPin
        self.endPin = endPin

    def getPinRange(self) -> list:
        return (self.startPin, self.endPin)

    def isPinInRange(self, pin) -> bool:
        return (pin >= self.startPin) and (pin <= self.endPin):

    def init(self) -> bool:
        return False
    
    def _checkPin(self, pin) -> int
        if self.isPinInRange(pin):
            return pin -self.startPin
        return -1
    
    def setPin(self, pin, val) -> int:
        return self._checkPin(pin)

    def getPin(self, pin) -> int:
        return self._checkPin(pin)

    def pulsePin(self, pin, onTime=1.0) -> None:
        """Pulse the the specific pin# on the Electrode-Driver-Stack of onTime (sec)"""
        if self._checkPin(pin):
            self.setPin(pin, 1)
            time.sleep(onTime)
            self.setPin(pin, 0)
