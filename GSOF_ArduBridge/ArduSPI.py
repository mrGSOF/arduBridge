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

Class to access the Arduino-Bridge SPI bus.
It uses the BridgeSerial class object to communicate over serial with the 
GSOF-Arduino-Bridge firmware.
The setMode method is used to set the mode of the SPI communication,
which determines the clock polarity (CPOL) and clock phase (CPHA) of the
communication. The write_read method is used to write data to the device and
receive data from it in a single operation.
It takes a list of bytes as an argument and sends them to the device,
then receives and returns the response from the device.
The setOff method is used to turn off the SPI communication.

The packet has a binary byte based structure
To write:
<'3'>,<TXD1>,<TXD2>...<TXDn>, <0x1b>
<''>, <RXD1>,<RTD2>...<RDXn>, <0x1b>
e.g, to write the value 0x14, 0x15 and 0x16 use:
['3', 0x14, 0x15, 0x16 0x1b]
In respond you three bytes will be reveived
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

class ArduBridgeSPI():
    MODE0 = 0 #< Clock is normally low, Data is sampled on the transition from low to high (leading edge)
    MODE1 = 1 #< Clock is normally low, Data is sampled on the transition from high to low (trailing edge)
    MODE2 = 2 #< Clock is normally high, Data is sampled on the transition from high to low (leading edge)
    MODE3 = 3 #< Clock is normally high, Data is sampled on the transition from low to high (trailing edge)
    OFF   = 4 #< SPI-OFF

    def __init__(self, bridge=False, logger=None):
            self.logger = logger
            self.comm = bridge
            self.RES = {1:'OK', -1:'ERR'}
            self.mode = -1

            #I2C protocol command
            self.SPI_PACKET_ID     = ord('3')
            self.SPI_CFG_PACKET_ID = ord('4')

    def setOff(self, v=False):
        """Disable the SPI"""
        self.setMode(self.OFF, v=v)

    def setMode(self, mode, freq, v=False):
        """Set the mode of the SPI bus (MODE0..MODE3)"""
        modeDesc = ("SPI_MODE0:\nClock is normally low (CPOL = 0)\nData is sampled on the transition from low to high (leading edge) (CPHA = 0)",
                    "SPI_MODE1:\nClock is normally low (CPOL = 0)\nData is sampled on the transition from high to low (trailing edge) (CPHA = 1)",
                    "SPI_MODE2:\nClock is normally high (CPOL = 1)\nData is sampled on the transition from high to low (leading edge) (CPHA = 0)",
                    "SPI_MODE3:\nClock is normally high (CPOL = 1)\nData is sampled on the transition from low to high (trailing edge) (CPHA = 1)")
        freq  = int(freq/100)
        freqL = freq&0xff
        freqH = (freq>>8)&0xff
        vDat = [self.SPI_CFG_PACKET_ID, mode, freqL, freqH]
        self.comm.send(vDat)
        reply = self.comm.receive(1) #Read the received bytes
        if reply[0] > 0:      #did we received a byte
            res = reply[1][0]  #if yes, read the result
            if v:
                if mode < self.OFF:
                    self.logger.info(modeDesc[mode])
                else:
                    self.logger.info("SPI-OFF")
            self.mode = mode
        else:
            self.logger.error("Error setting the SPI mode\n")
        return self

    def write_read(self, vByte):
        """Send and receive list of bytes (vByte) on the SPI bus. Returns a list of bytes"""
        vDat = [self.SPI_PACKET_ID]+ vByte #SPI packet-ID +data-vector
        self.comm.send(vDat)
        self.comm.sendReset()         #End the SPI mode
        reply = self.comm.receive(len(vByte)) #Read the received bytes
  
        if self.logger != None:
            if reply[0] != 0:      #did we received a byte
                res = reply[1][0]  #if yes, read the result
                self.logger.debug(f"SPI-Res: {res}")
        return reply
