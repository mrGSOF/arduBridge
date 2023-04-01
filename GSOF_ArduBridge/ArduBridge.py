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

Generate the main object to communicate with an arduino the runs the GSOF-Ardubridge firmware.
"""

"""
This code defines a class called ArduBridge that can be used to communicate with an Arduino board running the GSOF-Ardubridge firmware. The ArduBridge class has several methods for interacting with the Arduino, including OpenClosePort, Reset, and GetID.

The __init__ method is called when a new ArduBridge object is created and sets up the communication with the Arduino by creating an instance of BridgeSerial.ArduBridgeComm and saving it as self.comm. It also creates instances of several other classes: ArduGPIO.ArduBridgeGPIO, ArduAnalog.ArduBridgeAn, ArduI2C.ArduBridgeI2C, ArduSPI.ArduBridgeSPI, and CAP.ArduBridgePnS. These classes provide methods for interacting with the Arduino's analog inputs, digital inputs and outputs, I2C bus, SPI bus, and pulse and sample functionality, respectively.

The OpenClosePort method can be used to open or close the serial port connection to the Arduino. If the val argument is the string 'open', the serial port is opened. If val is any other string or the integer 0, the serial port is closed. The method returns the number of retries remaining if the serial port fails to open.

The Reset method sends a reset command to the Arduino and flushes the serial buffer. The GetID method sends a request for the Arduino's ID and returns the ID string if a reply is received, or False otherwise.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = ["James Perry"]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import sys, time
from GSOF_ArduBridge import BridgeSerial
from GSOF_ArduBridge import ArduAnalog
from GSOF_ArduBridge import ArduGPIO
from GSOF_ArduBridge import ArduI2C
from GSOF_ArduBridge import ArduSPI
from GSOF_ArduBridge import ArduPulseAndSample as CAP




class ArduBridge():
    def __init__(self, COM='COM9', baud=115200*2):

        version = 'v1.1 running on Python %s'%(sys.version[0:5])
        print('GSOF_ArduBridge %s'%(version))
        self.ExtGpio = [0,0]
        self.COM  = COM
        self.comm = BridgeSerial.ArduBridgeComm( COM=COM, baud=baud )
        self.gpio = ArduGPIO.ArduBridgeGPIO( bridge=self.comm )
        self.an   = ArduAnalog.ArduBridgeAn(bridge=self.comm )
        self.i2c  = ArduI2C.ArduBridgeI2C( bridge=self.comm )#, v=True )
        self.spi  = ArduSPI.ArduBridgeSPI( bridge=self.comm )#, v=True )
        self.cap  = CAP.ArduBridgePnS( bridge=self.comm )#, v=True )

    def OpenClosePort(self, val):
        if type(val) == str:
            if val == 'open':
                val = 1
            else:
                val = 0
        self.comm.OpenClosePort(val)
        retry = 6
        if val != 0:
            while (self.GetID() == False) and (retry > 0):
                time.sleep(0.5)
        return retry

    def Reset(self):
        self.comm.sendReset()
        self.comm.uart_flush()
        self.GetID()

    def GetID(self):
        self.comm.send([ord('?')])
        reply = self.comm.receive(1)
        if reply[0] != -1:
            s = ''
            ACK = 1
            N = reply[1][0]
            while (ACK != -1) and (N > 0):
                reply = self.comm.receive(1)
                ACK = reply[0]
                if ACK != -1:
                    N -= 1
                    s += chr(reply[1][0])
            s += '\n'
            print('%s'%(s))
            if reply[0] == 1:
                #print('Got reply\n')
                return s
            return False
        else:
            print('No reply')
            return False
