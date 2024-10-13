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

The class provides methods for interacting with the digital inputs and outputs of an Arduino via a serial connection.
It uses the BridgeSerial object to communicate over serial with the GSOF_ArduinoBridge firmware.
The packet has a binary byte based structure
byte0 - 'D' to set pin direction, 'I' to read pin state, 'O' to set pin state
        'S' to set the servo control value (firmwares above 1.5)
byte1 - pin number (binary-value)
byte2 - pin-value (binary-value) only for digital-out command
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2021"
__credits__ = []
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time
import S_Curve

class Servo():
    
    def __init__(self, gpio, ch, minPosition=0, maxPosition=255, logger=None):
        self.logger   = logger
        self.servoOut = gpio
        self.ch       = ch
        self.minPos   = minPosition
        self.maxPos   = maxPosition

    def servoWrite(self, pin, val):
        """Set the angle of a servo motor attached to a digital pin (an integer from 0 to 255)"""
        val = int(val)
        pin = int(pin)
        vDat = [ord('S'), pin, val]
        self.comm.send(vDat)
        reply = self.comm.receive(1)
        if self.logger != None:
            self.logger.debug(f"SERVO AT PIN<{pin}>: {val} - {self.RES[reply[0]]}")
        return reply[0]

    def servoScurve(self, p0, p1, acc=200, dt=0.05):
        """Smooth transition from P0 to P1 at acceleration"""
        t = 0
        points = S_Curve.solve(p0=p0, p1=p1, acc=acc, dt=dt)
        for point in points:
            if point < self.minPos:
                point = self.minPos
            elif point > self.maxPos:
                point = self.maxPos

            self.servoWrite(self.ch, point)
            if self.logger != None:
                t += dt
                self.logger.debug("%1.2f, %1.3f" % (t, point))  
            time.sleep(dt)
