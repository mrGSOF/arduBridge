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
Class to manage a stack of GPIO boards connected to an Arduino microcontroller.
"""
__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2024"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

from GSOF_ArduBridge import ExtGpio_base as BASE

class ExtGpioStack(BASE):
    def __init__(self, extGpioStack=[], v=False):
        self.v = v
        self.stack = extGpioStack

    def init(self) -> None:
        for dev in self.stack:
            print('\nConfiguring %s ID:%s [st:end]=%s'%(dev.ID, str(dev.getDevID()), , str(dev.getpinRange())))
            dev.v = self.v
            dev.init()

    def _getBoard(self, pin):
        for board in self.stack:
            if board.isInRange(pin):
                return board
        return None

    def setPin(self, pin, valList) -> int:
        for val in valList:
            board = self._getBoard(pin)
            board.setPin(pin, val)
            pin += 1
        return 1

    def getPin(self, pinList) -> int:
        vals = [0]*len(pinList)
        for i,pin in enumerate(pinList):
            board = self._getBoard(pin)
            vals[i] = board.getPin(pin)
        return vals

    def pulsePin(self, pin, onTime) -> None:
        board = self._getBoard(pin)
        board.pulsePin(pin, onTime)
