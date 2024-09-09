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

Class to access the Arduino-Bridge PulseAndSample (I/O) command.
This class is using the BridgeSerial class object to communicate over serial
with the GSOF_ArduinoBridge firmware.

The command will generate a pulse on pinPulse while sampling the adcPin for N samples
The packet has a binary byte based structure
byte0 - 'C' for pulse ans sample command
byte1 - pulsePin number (binary-value)
byte2 - adcPin number (binary-value)
byte3 - N samples (binary-value)
"""

"""
The ArduBridgePnS class is used to generate a pulse on pulsePin and sample the adcPin for samples number of samples. The pulseAndSample method of this class sends a command to the Arduino to execute this pulse and sample operation and receives the resulting sample values. The measCap method is not implemented and currently does not do anything.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2022"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

class ArduBridgePnS():
    def __init__(self, bridge=False, logger=None):
        self.logger = logger
        self.comm = bridge

    def pulseAndSample(self, pulsePin, adcPin, samples=64):

        vDat = [ord('C'), pulsePin, adcPin, samples]
        self.comm.send(vDat)
        reply = self.comm.receive(samples)

        if reply[0] != -1:
            val = reply[1]
            if self.logger != None:
                self.logger.debug(f"AN{adcPin}: {str(val)}")
            return val
        if self.logger != None:
            self.logger.error(f"AN{adcPin}: Error")
        return -1

    def measCap(self, pulsePin, adcPin, samples=64):
        return
