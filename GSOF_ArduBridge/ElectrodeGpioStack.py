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

Class to access the external-GPIO connected to the Arduino-Bridge via I2C.
This class is using the BridgeSerial class object to communicate over serial
with the GSOF-Arduino-Bridge firmware.
"""

"""
This script seems to be for managing external General Purpose Input-Output (GPIO) connected to an Arduino microcontroller via I2C (Inter-Integrated Circuit). The script defines a class ExtGpioStack, which has methods to initialize the connection to the external GPIO, set the mode (input or output) of a specific pin, write a value to a specific pin, and read the value of a specific pin. It also has a method pin2dev which maps a pin number to the device ID of the external GPIO to which it is connected. The script also imports a class Max3700ExtGPIO which seems to be used for communication with the external GPIO via I2C
"""
__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time
from GSOF_ArduBridge import CON_prn
from GSOF_ArduBridge import Max3700ExtGPIO

class ExtGpioStack():
    def __init__(self, i2c=False, devList=[], v=False, pin2pin=False):
        self.RES = {1:'OK', 0:'ERR', -1:'ERR'}
        self.v = v
        self.i2c = i2c
        self.devList = devList
        if len(self.devList) == 0:
            self.devList = range(0x40, 0x46, 1)
        self.pin2pin = pin2pin
        if self.pin2pin == False:
            self.pin2pin = range(0,20,1)

    def init(self):
        self.ExtGpio = []
        for dev in self.devList:
            print('\nConfiguring port-extenderID 0x%02x'%(dev))
            if self.i2c:
                self.ExtGpio.append( Max3700ExtGPIO.Max3700ExtGPIO( i2c=self.i2c, devID=dev, v=self.v ) )
                self.ExtGpio[-1].modeSet(mode=1) #Activating the MAX3700
                self.ExtGpio[-1].modeGet()       #Readback the MAX3700 mode
                self.ExtGpio[-1].bankModeGet()
                self.ExtGpio[-1].bankModeSet(0x55, B=0, N=7) #Setting all of its ports to output
                self.ExtGpio[-1].bankModeGet()               #Reading back the written data
                for pin in [0,8,16,24]:
                    self.ExtGpio[-1].portWrite(pin, 0x00)    #Simultaniously write 0 to 8 pins

            else:
                print('No I2C object...')

    def pinMode(self, pin, mode):
        if (mode != 0):
            mode = 1
        pin -= 1
        dev = self.pin2dev(pin)
        reg = self.pin2mReg(pin)

        self.i2c.writeRegister(dev, reg, [mode])
        reply = self.comm.receive(1)
        if self.v:
            CON_prn.printf('ExtDir%d: %s - %s', par=(pin, self.DIR[mode], self.RES[reply]), v=True)
        return reply[0]

    def pinWrite(self, pin, valList):
        """
        Set the state of the specific pin(s)# on the Electrode-Driver-Stack
        """
        pin -= 1
        if type(valList) == int:
            valList = [valList]
        for val in valList:
            if (val != 0):
                val = 1
            dev = self.pin2dev(pin)
            if dev != -1:
                pinDev = self.pin2pin[pin%20]
                reply = dev.pinWrite(pinDev, val)
                CON_prn.printf('ExtPinSet%d: %d - %s', par=(pin, val, self.RES[reply]), v=self.v)
            else:
                CON_prn.printf('ExtPinSet%d: Out of range', par=(pin), v=self.v)
                return -1
            pin += 1
        return 1

    def pinRead(self, pinList):
        """
        Read the state of the specific pin(s)# on the Electrode-Driver-Stack
        """
        if type(pinList) == int:
            pinList = [pinList]
        result = []
        for pin in pinList:
            pin -= 1
            dev = self.pin2dev(pin)
            if dev != -1:
                pinDev = pin%20
                reply = dev.pinRead(pinDev)
                val = reply[0]
                CON_prn.printf('ExtPin%d: %d', par=(pin, val), v=self.v)
                result.append(val)
            else:
                CON_prn.printf('ExtPin%d: Out of range', par=(pin), v=self.v)
                return -1
        return result

    def pinPulse(self, pin, onTime):
        """
        Pulse the the specific pin# on the Electrode-Driver-Stack of onTime [sec]
        """
        self.pinWrite(pin, 1)
        time.sleep(onTime)
        self.pinWrite(pin, 0)
        return 1

    def pin2dev( self, electrode_number ):
        """
        Each device has 20-IO pins
        """
        if electrode_number < 20:
            if len(self.ExtGpio) > 2:
                return self.ExtGpio[2]

        if (electrode_number >= 20) and (electrode_number < 40):
            if len(self.ExtGpio) > 3:
                return self.ExtGpio[3]

        if (electrode_number >= 40) and (electrode_number < 60): 
            if len(self.ExtGpio) > 4:
                return self.ExtGpio[4]

        if (electrode_number >= 60) and (electrode_number < 80):
            if len(self.ExtGpio) > 5:
                return self.ExtGpio[5]

        if (electrode_number >= 80) and (electrode_number < 100):
            if len(self.ExtGpio) > 0:
                return self.ExtGpio[0]

        if (electrode_number >= 100) and (electrode_number < 120):
            if len(self.ExtGpio) > 1:
                return self.ExtGpio[1]

        return -1
