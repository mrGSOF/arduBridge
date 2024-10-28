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

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2021"
__credits__ = []
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

class ArduBridgeWs2812():
    def __init__(self, bridge=False, logger=None):
        self.logger = logger
        self.comm = bridge

    def setConfig(self, pin, leds=0, red=0, green=0, blue=0):
        """Set the mode pin# to communicate with the WS2812 IC and RGB value of first N LEDS"""
        vDat = (ord('W'), pin, leds&0xff, (leds>>8)&0xff, red&0xff, green&0xff, blue&0xff)
        self.comm.send(vDat)
        return 1

    def ledWrite(self, vRGB):
        """Update LEDs in strip with 8-bit compressed RGB value (r3,g3,b2)"""
        vLED = [0]*len(vRGB)
        for i, rgb in enumerate(vRGB):
            r = int(rgb[0]*7/255)&0x7
            g = int(rgb[1]*7/255)&0x7
            b = int(rgb[2]*3/255)&0x3
            vLED[i] = (r<<5) +(g<<2) +b
        vDat = [ord('w')] +vLED
        self.comm.send(vDat)
        return 1
