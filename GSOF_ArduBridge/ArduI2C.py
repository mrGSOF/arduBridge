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

Class to access the Arduino-Bridge I2C bus.
This class is using the BridgeSerial object to communicate over serial
with the GSOF-Arduino-Bridge firmware.
The packet has a binary byte based structure

To write:
e.g. to write to device 0x14 starting at register 0x10 the values 0,1,2 use:
The method writeRegister(dev=0x14, reg=0x10, vByte=[0,1,2]):

Or send the below byte steam to the arduBridge
['2', 'A', 0x14, 'L', 4, 'W', 0x10, 0x00, 0x01, 0x02]
<'2'>,<'A'>,<DEV#>,<'L'>,<n+1>,<'W'>,<REG#>,<DAT1>,<DAT2>...<DATn>

To read:
e.g. to read from device 0x14 starting as register 0x10, 3 bytes use:
The method readRegister(dev=0x14, reg=0x10, N=3):

Or send the below byte steam to the arduBridge
['2', 'A', 0x14, 'L', 1, 'w', 0x10,'2', 'L', 3, 'R']
<'2'>,<'A'>,<DEV#>,<'L'>,<1>,<'w'>,<REG#>,<'2'>,<n>,<'R'>

note:'2' I2C packet header
     'W' write
     'w' write-restart
     'R' read
     'A' device-address
     'L' data length
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

class ArduBridgeI2C():
    def __init__(self, bridge=False, logger=None):
        self.logger = logger
        self.comm = bridge
        self.RES = {1:'OK', -1:'ERR'}

        #I2C protocol command
        self.I2C_PACKET_ID = ord('2')
        self.CMD_I2C_ADDRESS = ord('A')
        self.CMD_I2C_LENGTH = ord('L')
        self.CMD_I2C_FREQ = ord('F')
        self.CMD_I2C_WRITE_RESTART = ord('w')
        self.CMD_I2C_WRITE = ord('W')
        self.CMD_I2C_READ_RESTART = ord('r')
        self.CMD_I2C_READ = ord('R')

        self.ERROR_NONE	= ord('N')
        self.ERROR_UNESCAPE = ord('U')
        self.ERROR_LENGTH = ord('L')
        self.ERROR_READ = ord('R')
        self.ERROR_WRITEDATA = ord('W')
        self.ERROR_SENDDATA = ord('S')

        self.ERROR = {self.ERROR_NONE:'OK',
                      self.ERROR_UNESCAPE:'UNESCAPE',
                      self.ERROR_LENGTH:'LENGTH',
                      self.ERROR_READ:'READ',
                      self.ERROR_WRITEDATA:'WRITE-DATA',
                      self.ERROR_SENDDATA:'SEND-DATA'}

    def setFreq(self, freq):
        """Set_freq method sets the I2C bus frequency"""
        freq = int(freq/10000)&0xff
        vDat = [self.I2C_PACKET_ID,   #I2C packet-ID
                self.CMD_I2C_FREQ,    #next byte is the I2C closk frequency
                freq]
        
        self.comm.send(vDat)          #< Send command to arduBridge
        self.comm.sendReset()         #< To exit the I2C mode

        
    def writeRaw(self, dev, vByte):
        """Send list of bytes (vByte) to device (dev 7bit)"""
        vDat = [self.I2C_PACKET_ID,   #I2C packet-ID
                self.CMD_I2C_ADDRESS, #next byte is the I2C device-address
                dev,                  #DEV#
                self.CMD_I2C_LENGTH,  #Next byte is the data length
                len(vByte),           #Data length
                self.CMD_I2C_WRITE   #Next bytes should be sent as is to the I2C device
                ]+vByte                #data-vector
        
        self.comm.send(vDat)
        reply = self.comm.receive(1)
  
        if self.logger != None:
            if reply[0] != 0:      #did we received a byte
                res = reply[1][0]  #if yes, read the result
                self.logger.debug("I2C-WR: Dev-0x%02x - %s" % (dev, self.ERROR[res]))
        return reply

    def readRaw(self, dev, N):
        """Read N bytes from device (dev 7bit) and returns a list of bytes"""
        vHdr = [self.I2C_PACKET_ID,         #I2C packet-ID
                self.CMD_I2C_ADDRESS,       #next byte is the I2C device-address
                dev,                        #DEV#
                self.CMD_I2C_LENGTH,        #Next byte is the data length (including the register#)
                N,                          #Data length
                self.CMD_I2C_READ]          #Start the read sequence

        self.comm.send(vHdr)
        reply = self.comm.receive(1)        #1st byte is how many bytes where read
        if reply[0] != 0:
            n = reply[1][0]
            reply = self.comm.receive(n)    #Read n bytes
            if reply[0] != 0:
                val = reply[1]
                if self.logger != None:
                    self.logger.debug("I2C-RD: Dev-0x%02x, Dat %s" % (dev, str(val)))
                return val
        if self.logger != None:
            self.logger.error(f"I2C-RD: Dev{dev} - Error")
        return -1

    def writeRegister(self, dev, reg, vByte):
        """Write bytes (vByte) to register (reg) on device (dev 7bit)"""
        vDat = [self.I2C_PACKET_ID,   #I2C packet-ID
                self.CMD_I2C_ADDRESS, #next byte is the I2C device-address
                dev,                  #DEV#
                self.CMD_I2C_LENGTH,  #Next byte is the data length (including the register#)
                len(vByte) +1,        #Data length
                self.CMD_I2C_WRITE,   #Next bytes should be sent as is to the I2C device
                reg] +vByte           #REG# +data-vector
        
        self.comm.send(vDat)
        reply = self.comm.receive(1)
  
        if self.logger != None:
            if reply[0] != 0:      #did we received a byte
                res = reply[1][0]  #if yes, read the result
                if self.logger != None:
                    self.logger.debug('I2C-WR: Dev-0x%02x, Reg%d - %s' % (dev, reg, self.ERROR[res]))
        return reply

    def readRegister(self, dev, reg, N, delay=0.0):
        """Read N bytes from register (reg) on device (dev 7bit) and returns a list of bytes"""
        vHdr = [self.I2C_PACKET_ID,         #I2C packet-ID
                self.CMD_I2C_ADDRESS,       #next byte is the I2C device-address
                dev,                        #DEV#
                self.CMD_I2C_LENGTH,        #Next byte is the data length (including the register#)
                1,                          #Data length
                self.CMD_I2C_WRITE_RESTART, #Next bytes should be sent as is to the I2C device
                reg]

        vRd  = [self.I2C_PACKET_ID,         #I2C packet-ID
                self.CMD_I2C_LENGTH,        #Next byte is the data length (including the register#)
                N,                          #N bytes to read
                self.CMD_I2C_READ]          #Start the read sequence

        if delay <= 0.0:
            ### READ WITHOUT DELAY
            self.comm.send(vHdr +vRd)

            reply = self.comm.receive(1)        #1st byte is the ACK for the register write
            err = True
            if (reply[0] != 0) and (reply[0] != -1):
                err = False
        else:
            ### READ WITH DELAY
            self.comm.send(vHdr)                    #< Start by sending the register (command) number
            reply = self.comm.receive(1)            #< ACK for the register (command) write
            err = True
            if (reply[0] != 0) and (reply[0] != -1):
                err = False
                if delay > 0.0:
                    time.sleep(delay)               #< DELAY BETWEEN WRITE COMMAND AND READ SEQUENCE
                self.comm.send(vRd)                 #< Send the read command
                    
        if err == False:
            reply = self.comm.receive(1)        #< The number of bytes that where read
            if reply[0] != 0:
                n = reply[1][0]
                reply = self.comm.receive(n)    #< Read N bytes
                if reply[0] != 0:
                    val = reply[1]
                    if self.logger != None:
                        self.logger.debug("I2C-RD: Dev-0x%02x, Reg%d, Dat %s " % (dev, reg, str(val)))
                    return val
        if self.logger != None:
            self.logger.error(f"I2C-RD: Dev{dev}, Reg{reg} - Error")
        return -1
