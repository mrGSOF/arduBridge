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
Class to access the High-Voltage-Switch Board (V2) that has single PCA9505.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2024"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

from GSOF_ArduBridge.device import HVSW_Driver_base as BASE
from GSOF_ArduBridge.device import pca9505_class as GPIO_IC

class HVSW_Driver(BASE.HVSW_Driver_base):
    def __init__(self, comm=False, devID=0, startPin=0, endPin=39, v=False):
        super().__init__(startPin, endPin)
        devID += GPIO_IC.PCA9505.devID
        self.ID = "HVSW_Driver-V2 ID 0x%02x"%(devID)
        self.v = v
        self.comm = comm
        self.dev = GPIO_IC.PCA9505(comm=comm, devID=devID, v=v)

    def init(self, v=None):
        if v == None:
            v = self.v
        self.dev.v = v
        self.dev.clearAllPins()
        self.dev.setAllPinsToOutput()

    def getDevID(self):
        return self.dev.devID

    def setPin(self, pin, val):
        """Set the state of the specific pin#"""
        pin = super().setPin(pin)
        if (pin >= 0) and (pin < self.dev.maxPins):
            return self.dev.setPin(pin, val)
        return -1

    def getPin(self, pin):
        """Read the state of the specific pin#"""
        pin = super().setPin(pin)
        if (pin >= 0) and (pin < self.dev.maxPins):
            return self.dev.getPin(pin)
        return -1
