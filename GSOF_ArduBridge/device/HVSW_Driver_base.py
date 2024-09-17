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
        
    def assignPinRange(self, startPin, endPin):
        self.startPin = startPin
        self.endPin = endPin

    def getPinRange(self) -> list:
        return (self.startPin, self.endPin)

    def isPinInRange(self, pin) -> bool:
        return (pin >= self.startPin) and (pin <= self.endPin)

    def init(self, v=None) -> bool:
        return False
    
    def _checkPin(self, pin) -> int:
        if self.isPinInRange(pin):
            return pin -self.startPin
        return -1
    
    def setPin(self, pin, val=0) -> int:
        return self._checkPin(pin)

    def getPin(self, pin) -> int:
        return self._checkPin(pin)

    def pulsePin(self, pin, onTime=1.0) -> None:
        """Pulse the the specific pin# on the Electrode-Driver-Stack of onTime (sec)"""
        if self._checkPin(pin):
            self.setPin(pin, 1)
            time.sleep(onTime)
            self.setPin(pin, 0)
