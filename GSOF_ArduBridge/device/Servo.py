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
__copyright__ = "Copyright 2024"
__credits__ = []
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time
from GSOF_ArduBridge import S_Curve

class Servo():
    
    def __init__(self, setServo, ch, minPosition=0, maxPosition=255, logger=None):
        self.logger    = logger
        self._setServo = setServo
        self.ch        = ch
        self.minPos    = minPosition
        self.maxPos    = maxPosition

    def setServo(self, val):
        """Set the angle of a servo motor attached to a digital pin"""
        if val < self.minPos:
            val = self.minPos
        elif val > self.maxPos:
            val = self.maxPos
        self._setServo(self.ch, val)

    def servoWrite(self, val):
        """Set the angle of a servo motor attached to a digital pin"""
        self.setServo(val)
        
    def servoScurve(self, p0, p1, acc=0.001, dt=0.05):
        """Smooth transition from P0 to P1 at acceleration"""
        t = 0
        points = S_Curve.solve(p0=p0, p1=p1, acc=acc, dt=dt)
        for point in points:
            self.setServo(point)
            if self.logger != None:
                t += dt
                self.logger.debug("%1.2f, %1.3f" % (t, point))  
            time.sleep(dt)
