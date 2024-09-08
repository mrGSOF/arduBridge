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

The class provides methods for interacting with the analog inputs and outputs of an Arduino via a serial connection.
It uses the BridgeSerial object to communicate over serial with the GSOF_ArduinoBridge firmware.

The packet has a binary byte based structure
byte0 - 'P' for PWM-Out, 'A' for Analog-In
byte1 - pin bumber (binary-value)
byte2 - pwm-value (binary-value) only for analog-out command
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"


class ArduBridgeAn():
    def __init__(self, bridge=False, logger=None):
        self.logger = logger
        self.comm = bridge

    def analogWrite(self, pin, val):
        val = int(val)
        if (val > 0xff):
            val = 0xff
        if (pin < 0x1b):
            vDat = [ord('P'), pin, val]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        if self.logger != None:
            RES = 'OK'
            if reply[0] == -1:
                RES = 'ERR'
            if self.logger != None:
                self.logger.debug(f"PWM{pin}: {val} - {RES}")
        return reply[0]

    def analogRead(self, pin):
        if (pin < 0x1b):
            vDat = [ord('A'), pin]
            self.comm.send(vDat)
        reply = self.comm.receive(2)
        if reply[0] != -1:
            val = (reply[1][0] +(reply[1][1])*256)
            if self.logger != None:
                self.logger.debug(f"AN{pin}: {val}")
            return val
        if self.logger != None:
            self.logger.error(f"AN{pin}: Error")

        return -1
