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

Python class for interacting with the BH1750 ambient light sensor.
The device communicates with the Arduino-Bridge via I2C.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2024"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

class BH1750():
    RES  = {"4lux": 3, "1lux": 0, "0.5lux": 1}
    MODE = {"continuous": 16, "single": 32}
    
    def __init__(self, ardu, dev=0x23):
        self.ardu = ardu
        self.dev = dev
    
    def _calcLux(self, bytes) -> int:
        lightLevel = -1
        if bytes != -1:
            lightLevel = (bytes[0]*256 +bytes[1])/1.2  #< compute the light level in (lux)
        return lightLevel

    def reset(self):
        """This function resets the light sensor"""
        self.ardu.i2c.writeRaw(self.dev, [0x7])
    
    def setOn(self):
        """This function turns on the light sensor"""
        self.ardu.i2c.writeRaw(self.dev, [0x1])

    def setOff(self):
        """This function turns off the light sensor"""
        self.ardu.i2c.writeRaw(self.dev, [0x0])

    def measure(self, res="1lux", continuous=False):
        if continuous == True:
            mode = self.MODE["continuous"]
        else:
            mode = self.MODE["single"]
            
        cmd = self.RES[res] +mode
        self.ardu.i2c.writeRaw(self.dev, [cmd])
        bytes = self.ardu.i2c.readRaw(self.dev, 2)
        sf=1
        if res == "0.5lux":
            sf=0.5
        return self._calcLux(bytes)*sf
