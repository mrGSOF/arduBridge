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

Class of a basic serial communication methods.
The object is constructed with the supplied serial device and baud-rate as an input arguments.
The send and receive methods are thread protected using internal semaphores.
Special data bytes such as RST(0x1b) and ESC(0x5c) are send using an escape code sequence.
The escape code sequence is generated as follow:
Instead of sending the value 0x1b, send the byte sequence 0x5c followed by 0xb1
Instead of sending the value 0x5c, send the byte sequence 0x5c followed by 0xc5
All rest of the values are sent without any manipulations.

By: Guy Soffer (gsoffer@yahoo.com)
Date: 10/April/2020
"""

__version__ = "1.1.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time, sys, threading
import serial

class ArduBridgeComm():
    """Open, Close, Send, Receive methods"""
    RST  = 0x1b #< Reset symbol
    ESC  = 0x5c #< Escape symbol
    CR   = 0x0d #< Carriage return
    LF   = 0x0a #< Linefeed
    ERR  = -1

    def __init__(self, COM, baud=115200*2, PortStatusReport=False, RxTimeOut = 0.015, writeTimeout=0.1, interByteTimeout=None, logger=None):
        self.pyVer = sys.version_info.major +sys.version_info.minor/10.0
        print('GSOF_ArduSerial v1.1 for Python-%s'%(self.pyVer))
        self.RxTry = 25
        self.logger = logger
        self.LINK = False
        self.semaTX = threading.Semaphore(1)
        self.semaRX = threading.Semaphore(1)
        self.ser = serial.Serial(None,
                                 baud,
                                 timeout=RxTimeOut,
                                 writeTimeout=writeTimeout,
                                 inter_byte_timeout=interByteTimeout
                                 )
        self.ser.port = COM
        self.baud = baud
        self.COM = COM
        
    def sendReset(self) -> None:
        """Send the reset command to the Arduino"""
        self.semaTX.release()
        if self.pyVer < 3.0:
            self.uart_wr(chr(self.RST))
        else:
            self.uart_wr( bytes([self.RST]) )
        
    def send(self, vDat) -> None:
        """Send list of bytes over the serial link"""
        self.semaTX.acquire()
        if ( self.LINK == True):
            done = False
            while done == False:
                try:
                    self.ser.flushInput() #self.ser.read(32) #self.uart_flush() #Make sure RX is empty
                    done = True
                except serial.serialutil.SerialException:
                    self.try_to_open_new_port()
                    pass

            if self.pyVer < 3.0:
                vStr = ''
                for c in vDat:
                    if ( (c == self.ESC) or (c == self.RST) ):
                        swap_c = ((c&0xf)<<4) +((c>>4)&0xf)
                        vStr += ( chr(self.ESC) +chr(swap_c) )
                    else:
                        vStr += ( chr(c) )

            else:
                vStr = bytes()
                for c in vDat:
                    if ( (c == self.ESC) or (c == self.RST) ):
                        swap_c = ((c&0xf)<<4) +((c>>4)&0xf)
                        vStr += bytes( [self.ESC, swap_c] )
                    else:
                        vStr += bytes( [c] )
            self.uart_wr( vStr )
        self.semaTX.release()

    def getByte(self) -> list:
        """Returns a list with single byte received over the serial link"""
        c = []
        trail = self.RxTry
        while (len(c)==0) and (trail > 0):
            try:
                c = self.ser.read(1)
            except serial.serialutil.SerialException:
                self.try_to_open_new_port()
                c = []
                pass

            trail -= 1
        if len(c) == 0:
            print('Error - %s RX timeout'%(self.ser.port))
        return c
        
    def receive(self, N) -> list:
        """Returns a list with maximum N received bytes with timeout of 0.1 sec"""
        N = int(N)
        self.semaRX.acquire()
        vDat = [-1]*N
        ERR = [self.ERR]
        if (self.LINK == True):
            ERR = [0, vDat]
            i = 0
            while i<N:
                c = self.getByte()
                
                if len(c) == 0:
                    self.semaRX.release()
                    return ERR
                c = ord(c)
                
                if c == self.ESC:
                    c = self.getByte()
                    while len(c) == 0:
                        time.sleep(0.1)
                        c = self.getByte()
                        #self.semaRX.release()
                        #return ERR
                    c = ord(c)
                    c = ((c&0xf)<<4) +((c>>4)&0xf) #Swapping the value after ESC
                    
                elif c == self.RST:
                    print('Error - Received RST from Arduino-Bridge\n')
                    self.semaRX.release()
                    return ERR
                vDat[i] = c
                i += 1
            self.semaRX.release()
            return [1, vDat]
        print('Error - %s is closed'%(self.ser.port))
        self.semaRX.release()
        return ERR

    def ReportLinkStatus(self, val) -> None:
        """Returns True is serial link is active"""
        self.LINK = val
        if (self.LinkReport):
            self.LinkReport(val)
        
    def OpenClosePort(self, val) -> None:
        """Open (1) or close (0) the serial link"""
        if (val):
            try:
                self.ser.open()
                self.LINK = True
                print('ArduBridge COM is open')
                
            except serial.SerialTimeoutException:
                self.LINK = False
                print('Error - Cannot oprn %s\n'%(self.ser.port))
                pass

            except serial.SerialException:
                print('Cannot execute command\n')
        else:
            self.ser.close()
            self.LINK = False
            print('ArduBridge COM is closed')

    def try_to_open_new_port(self) -> None:
        """Retry to open the serial link every 0.5 sec"""
        self.ser.close()
        while self.ser.isOpen() == False:
            print('COM is dead!! - retry a connection')
            try:
                self.ser.open()
            except serial.serialutil.SerialException:
                time.sleep(0.5)
                pass
        print('COM connection reastablished!!')

    def uart_flush(self) -> None:
        """Flash the serial FIFO"""
        if (self.LINK):
            v=[1]
            while len(v) > 0:
                try:
                    v = self.ser.read(32)
                except serial.serialutil.SerialException:
                    comm = self.try_to_open_new_port()
                    v = [1]

    def uart_wr(self, dat) -> None:
        """Send list of bytes over the serial link, attempt to open the link if closed"""
        if (self.LINK):
            try:
                self.ser.write(dat)
                
            except serial.SerialTimeoutException:
                print('Error - %s TX timeout'%(self.ser.port))
                pass
            
            except serial.serialutil.SerialException:
                comm = self.try_to_open_new_port()
                pass

           
