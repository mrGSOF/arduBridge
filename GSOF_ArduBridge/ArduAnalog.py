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

Class to access the Arduino-Bridge Analog inputs and outputs.
This class is using the BridgeSerial class object to communicate over serial
with the GSOF_ArduinoBridge firmware.
The packet has a binary byte based structure
byte0 - 'P' for PWM-Out, 'A' for Analog-In
byte1 - pin bumber (binary-value)
byte2 - pwm-value (binary-value) only for analog-out command
"""


"""
This code defines a class called ArduBridgeAn that provides methods for interacting with the analog inputs and outputs of an Arduino board via a serial connection. The class is designed to work with the GSOF_ArduinoBridge firmware, which is responsible for managing the communication between the host computer and the Arduino board.

The ArduBridgeAn class has two methods: analogWrite and analogRead. The analogWrite method sends a command to the Arduino board to set the value of a specified PWM (pulse width modulation) output pin. The analogRead method sends a command to the Arduino board to read the value of a specified analog input pin and returns the result. Both methods use the BridgeSerial class to send and receive data over the serial connection.

The ArduBridgeAn class also has a number of other properties and methods, including a constructor method __init__ that initializes the object with a BridgeSerial object and an optional verbosity flag. The __init__ method also sets up a comm property that is used to store a reference to the BridgeSerial object.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

from GSOF_ArduBridge import BridgeSerial
from GSOF_ArduBridge import CON_prn

class ArduBridgeAn():
    def __init__(self, bridge=False, v=False):
        self.v = v
        self.comm = bridge

    def analogWrite(self, pin, val):
        val = int(val)
        if (val > 0xff):
            val = 0xff
        if (pin < 0x1b):
            vDat = [ord('P'), pin, val]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        if self.v:
            RES = 'OK'
            if reply[0] == -1:
                RES = 'ERR'
            CON_prn.printf('PWM%d: %d - %s', par=(pin, val, RES), v=True)
        return reply[0]

    def analogRead(self, pin):
        if (pin < 0x1b):
            vDat = [ord('A'), pin]
            self.comm.send(vDat)
        reply = self.comm.receive(2)
        if reply[0] != -1:
            val = (reply[1][0] +(reply[1][1])*256)
            CON_prn.printf('AN%d: %d', par=(pin, val), v=self.v)
            return val
        CON_prn.printf('AN%d: Error', par=(pin), v=self.v)
        return -1
