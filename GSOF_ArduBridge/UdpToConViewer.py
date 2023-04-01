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

General Viewer class to display stuff to the console.
1. A UDP packet is received at a specific LocalPort.
2. The packet is output to the console using Pythons print command.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = []
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import socket, sys, time, threading

class UdpToConViewer():
    def __init__(self, nameID='', RxPort=6000, threadMode=True):
        self.nameID = str(nameID)
        #self.ip = str(ipRX)
        self.RxPort = int(RxPort)
        #Datagram (UDP) socket
        self.active = False
        self.running = False
        ok = True
        try:
            self.udpRx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            ok = False
         
        if ok:
            # Bind socket to local host and port
            try:
                if threadMode == True:
                    self.udpRx.setblocking(1)
                else:
                    self.udpRx.setblocking(0)
                    self.udpRx.settimeout(0.01)
                self.udpRx.bind(('', self.RxPort))
            except socket.error as msg:
                print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                ok = False

            print('%s: Ready on port %d\n'%(nameID, self.RxPort))
            self.active = True
            if threadMode == True:
                self.Thread = threading.Thread(target=self.run)
                self.Thread.start()
        
    def update(self, s):
        print('%s: %s'%(self.nameID, str(s)))

    def run(self):
        #print('UDP-running...')
        self.running = True
        while self.active:
            #print('UDP-running...')
            self.udpRx.settimeout(1)
            self.getPacket()
        self.running = False
        print('UDP-stoped...')

    def getPacket(self):
        try:
            payload, fromIP = self.udpRx.recvfrom(512)
            payload = bytearray(payload)              #Add the binary payload
            self.update(payload)
        except socket.timeout:
            payload=[]
        return payload
        


 
