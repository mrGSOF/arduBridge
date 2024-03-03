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
from GSOF_ArduBridge import BridgeSerial
from GSOF_ArduBridge import CON_prn

class ArduBridgeGPIO():
    OUTPUT = 0 #< To set the pin to digital output mode
    INPUT = 1  #< To set the pin to digital input mode
    SERVO = 2  #< To set the pin to servo mode
    
    def __init__(self, bridge=False, v=False):
        self.v = v
        self.comm = bridge
        self.RES = {1:'OK', 0:'ERR' , -1:'ERR'}
        self.DIR = {1:'IN', 0:'OUT', 2:'SERVO'}

    def setMode(self, pin, mode, init=0):
        """Set the mode of a digital pin on the Arduino (INPUT, OUTPUT, SERVO)"""
        self.pinMode(pin, mode, init=0)

    def pinMode(self, pin, mode, init=0):
        """Set the mode of a digital pin on the Arduino (INPUT, OUTPUT, SERVO)"""
        if (mode > 2):
            mode = 1
        if (pin < 112):
            vDat = [ord('D'), pin, mode]
            #print(str(vDat))
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        #print(reply)
        CON_prn.printf('DIR%d: %s - %s', par=(pin, self.DIR[mode], self.RES[reply[0]]), v=self.v)
        return reply[0]

    def digitalWrite(self, pin, val):
        """Set the Arduino's pin state (either 0 or 1)"""
        val = int(val)
        if (val != 0):
            val = 1
        if (pin < 0x1b):
            vDat = [ord('O'), pin, val]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        CON_prn.printf('DOUT%d: %d - %s', par=(pin, val, self.RES[reply[0]]), v=self.v)
        return reply[0]

    def digitalRead(self, pin):
        """Returns the Arduino's pin state (either 0 or 1)"""
        if (pin < 0x1b):
            vDat = [ord('I'), pin]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        if reply[0]:
            val = reply[1][0]
            CON_prn.printf('DIN%d: %d', par=(pin, val), v=self.v)
            return val
        CON_prn.printf('DIN%d: Error', par=(pin), v=self.v)
        return -1

    def servoWrite(self, pin, val):
        """Set the angle of a servo motor attached to a digital pin (an integer from 0 to 255)"""
        val = int(val)
        pin = int(pin)
        vDat = [ord('S'), pin, val]
        self.comm.send(vDat)
        reply = self.comm.receive(1)
        CON_prn.printf('SERVO AT PIN<%d>: %d - %s', par=(pin, val, self.RES[reply[0]]), v=self.v)
        return reply[0]

    def servoScurve(self, pin, P0, P1, acc=200, DT=0.05):
        """Smooth transition from P0 to P1 at acceleration"""
        acc = abs(acc)
        DP = abs(P1-P0)
        T = 2*math.sqrt(4*DP/acc)
        Vmax = acc*T/2

        p = 0
        v = 0
        t = 0
        while p < DP:
            if p < (DP/2):
                p += v*DT +0.5*acc*DT**2
                v += acc*DT
            else:
                p += v*DT -0.5*acc*DT**2
                v -= acc*DT
            t += DT
            srvP = P0 +p
            if P0 > P1:
                srvP = P0 -p
                
            self.servoWrite(pin, int(srvP))
            CON_prn.printf("%1.2f, %1.3f", par=(t, srvP), v=False)   
            time.sleep(DT)

    def pinPulse(self, pin, onTime):
        """Pulse the the specific pin# on the arduino GPO"""
        self.digitalWrite(pin, 1)
        time.sleep(onTime)
        self.digitalWrite(pin, 0)
        return 1
