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
Class to access the High-Voltage-Switch Board (V1) that has two MAX3700AAI.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2024"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

from GSOF_ArduBridge import HVSW_Driver_base as BASE
from GSOF_ArduBridge import max7300_class as GPIO_IC

class HVSW_Driver(BASE.HVSW_Driver_base):
    def __init__(self, comm=False, devID=[0,1], startPin=0, endPin=39, v=False):
        super().__init__(startPin, endPin)
        devID[0] += GPIO_IC.MAX7300AAI.devID
        devID[1] += GPIO_IC.MAX7300AAI.devID
        self.ID = "HVSW_Driver-V1 ID 0x%02x,0x%02x"%(devID[0], devID[1])
        self.v = v
        self.comm = comm
        self.devs = [GPIO_IC.MAX7300AAI(comm=comm, devID=devID[0], v=v),
                     GPIO_IC.MAX7300AAI(comm=comm, devID=devID[1], v=v)]

    def init(self, v=None):
        """Clear all pins and set thier direction to output"""
        for dev in self.devs:
            if v == None:
                v = self.v
            dev.v = v
            dev.clearAllPins()
            dev.setAllPinsToOutput()

    def getDevID(self):
        return (self.devs[0].devID, self.devs[1].devID)
            
### Pin level API
##    def _setPinMode(self, pin, mode):
##        """Set the direction of an individual pin"""
##        if pin < devs[0].maxPins:
##            dev = dev[0]
##        else:
##            dev = dev[1]
##            pin -= devs[0].maxPins
##        return dev.setPinMode(pin, mode)

    def setPin(self, pin, val):
        """Set the state of the specific pin#"""
        pin = super().setPin(pin)
        if pin >= 0:
            if pin < self.devs[0].maxPins:
                dev = self.devs[0]
            else:
                dev = self.devs[1]
                pin -= self.devs[0].maxPins
            return dev.setPin(pin, val)
        return -1

    def getPin(self, pin):
        """Read the state of the specific pin#"""
        pin = super().setPin(pin)
        if pin >= 0:
            if pin < self.devs[0].maxPins:
                dev = self.devs[0]
            else:
                dev = self.devs[1]
                pin -= self.devs[0].maxPins
            return dev.getPin(pin)
        return -1
