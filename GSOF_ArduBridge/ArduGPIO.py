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

import time, math
from GSOF_ArduBridge import S_Curve

class ArduBridgeGPIO():
    OUTPUT = 0 #< To set the pin to digital output mode
    INPUT = 1  #< To set the pin to digital input mode
    SERVO = 2  #< To set the pin to servo mode
    LAST_MODE = SERVO
    
    def __init__(self, bridge=False, logger=None):
        self.logger = logger
        self.comm = bridge
        self.RES = {1:'OK', 0:'ERR' , -1:'ERR'}
        self.DIR = {1:'IN', 0:'OUT', 2:'SERVO'}

    def setMode(self, pin, mode, init=0):
        """Set the mode of a digital pin on the Arduino (INPUT, OUTPUT, SERVO)"""
        self.pinMode(pin, mode, init=0)

    def pinMode(self, pin, mode, init=0):
        """Set the mode of a digital pin on the Arduino (INPUT, OUTPUT, SERVO)"""
        if (mode > self.LAST_MODE):
            raise ValueError("Invalid mode value, exceeded maximum value")
        if (pin < 112):
            vDat = [ord('D'), pin, mode]
            #print(str(vDat))
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        #print(reply)
        if self.logger != None:
            self.logger.debug('DIR%d: %s - %s', pin, self.DIR[mode], self.RES[reply[0]])
        return reply[0]

    def digitalWrite(self, pin, val):
        return self.setPin(pin, val)

    def setPin(self, pin, val):
        """Set the Arduino's pin state (either 0 or 1)"""
        val = int(val)
        if (val != 0):
            val = 1
        if (pin < 0x1b):
            vDat = [ord('O'), pin, val]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        if self.logger != None:
            self.logger.debug(f"DOUT{pin}: {val} - {self.RES[reply[0]]}")
        return reply[0]

    def digitalRead(self, pin):
        return self.getPin(pin)

    def getPin(self, pin):
        """Returns the Arduino's pin state (either 0 or 1)"""
        if (pin < 0x1b):
            vDat = [ord('I'), pin]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        if reply[0]:
            val = reply[1][0]
            if self.logger != None:
                self.logger.debug(f"DIN{pin}: {val}")
            return val
        if self.logger != None:
            self.logger.error(f"DIN{pin}: Error")
        return -1

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

    def servoScurve(self, pin, p0, p1, acc=200, dt=0.05) -> int:
        """Smooth transition from P0 to P1 at acceleration"""
        t = 0
        points = S_Curve.solve(p0=p0, p1=p1, acc=acc, dt=dt)
        for point in points:
            if point < 0:
                point = 0
            elif point > 255:
                point = 255

            self.servoWrite(pin, point)
            if self.logger != None:
                t += dt
                self.logger.debug("%1.2f, %1.3f" % (t, point))  
            time.sleep(dt)
        return 1

    def servoScurveDirect(self, pin, p0, p1, acc=200, dt=0.05, blocking=True) -> int:
        """Smooth transition from P0 to P1 at acceleration"""
        self.comm.send( (ord('s'), int(pin), int(p0), int(p1), int(acc/10), int(dt*1000)) )
        reply = [0] #self.comm.receive(1)
        sleepTime = 2*math.sqrt(abs(p1-p0)/acc)
        if self.logger != None:
            self.logger.debug(f"SERVO AT PIN<{pin}>: {p1} {sleepTime} sec")
        if (blocking == True) and (sleepTime > 0.02):
            time.sleep(sleepTime -0.01)
        return sleepTime
 
    def pinPulse(self, pin, onTime) -> int:
        """Pulse the the specific pin# on the arduino GPO"""
        self.digitalWrite(pin, 1)
        time.sleep(onTime)
        self.digitalWrite(pin, 0)
        return 1
