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
"""
I2C_AD = 0x1E

CFGA   = 0x00
CFGB   = 0x01
MODE   = 0x02
X_H    = 0x03
X_L    = 0x04
Z_H    = 0x05
Z_L    = 0x06
Y_H    = 0x07
Y_L    = 0x08
STATUS = 0x09
IDA    = 0x0A
IDB    = 0x0B
IDC    = 0x0C

MA      = (1,2,4,8) #< Samples per average
DO      = (0.75, 1.5, 3.0, 7.5, 15.0, 30.0, 75.0, -1) #< Hz
MS      = ("normal", "positiveBias", "negativeBias", "reserved")
GNrange = (0.88, 1.3, 1.9, 2.5, 4.0, 4.7, 5.6, 8.1) #< +/- max Gauss
GNgain  = (1370, 1090, 820, 660, 440, 390, 330, 230) #< LSb/Gauss
GNlsb   = (0.73, 0.92, 1.22, 1.52, 2.27, 2.56, 3.03, 4.35) #< mGauss/LSb
MD      = ("continuous", "single", "idle", "sleep")

class Reg8():
    size = 1
    name = None
    def __init__(self):
        self.val = 0

    def get(self) -> dict:
        if self.name == None:
            return self.val
        return {self.name:self.val}

    def toBytes(self, val) -> list:
        return [0xff&val]
    
    def fromBytes(self, byte):
        self.val = byte&0xff
        return self

class Reg16(Reg8):
    size = 2
    def toBytes(self, val) -> list:
        val = int(val)
        msb  = (val>>8)&0xff
        lsb = val&0xff
        return [msb, lsb]
    
    def fromBytes(self, vByte):
        self.val = vByte[0]*256 +vByte[1]
        return self

class RegS16(Reg16):
    def fromBytes(self, vByte):
        super().fromBytes(vByte)
        if self.val > 0x7FFF:
            self.val = -1*(((~self.val)+1)&0xffff)
        return self

class Reg24(Reg16):
    size = 3

    def toBytes(self, val) -> list:
        val = int(val)
        msb  = (val>>16)&0xff
        lsb  = (val>>8)&0xff
        xlsb = val&0xff
        return [msb, lsb, xlsb]

    def fromBytes(self, vByte):
        self.val = (vByte[0]<<16) +(vByte[1]<<8) +vByte[2]
        return self

class CfgA(Reg8):
    ad = CFGA

    def __init__(self):
        self.avgN = 0 #< Averaged samples N 
        self.rate = 0 #< Rate
        self.mode = 0 #< Measurement mode
        
    def get(self) -> int:
        return {'avgN':self.avgN, 'rate':self.rate, 'measurement':self.meas}

    def toBytes(self, avgN=4, rate=0, meas=0) -> list:
        ma = MA.index(avgN)
        do = DO.index(rate)
        ms = MS.index(meas)
        val = (ma<<5) +(do<<2) +(ms&3)
        return [val]

    def fromBytes(self, vByte):
        self.avgN = MA[(vByte>>5)&3]
        self.rate = DO[(vByte>>2)&7]
        self.meas = MS[vByte&3]
        return self

class CfgB(Reg8):
    ad = CFGB

    def __init__(self):
        self.gn = 0 #< Gain

    def get(self) -> int:
        gn = self.gn
        return {'gain':GNgain[gn], 'range':GNrange[gn], 'lsb':GNlsb[gn]}
        
    def toBytes(self, gn) -> list:
        val = ((gn&7)<<5)
        return [val]

    def fromBytes(self, vByte):
        self.gn = (vByte>>5)&7
        return self

class Mode(Reg8):
    ad = MODE

    def __init__(self):
        self.hs = 0 #< High Speed I2C (3.4Mb/sec
        self.mode = 0

    def get(self) -> int:
        md = self.mode
        return {'hs':self.hs, 'mode':self.mode}
        
    def toBytes(self, hs=0, mode=MD[0]) -> list:
        md = MD.index(mode)
        val = ((hs&1)<<7) +md
        return [val]

    def fromBytes(self, vByte):
        self.hs   = (vByte>>7)&1
        self.mode = MD[vByte&3]
        return self

class AdcX(RegS16):
    ad = X_H
    name = "outx"
    
class AdcZ(RegS16):
    ad = Z_H
    name = "outz"

class AdcY(RegS16):
    ad = Y_H
    name = "outy"

class Status(Reg8):
    ad = STATUS

    def __init__(self):
        self.lock = 0 #< When set, all data output registers are locked and any new data will not be placed.
        self.rdy  = 0 #< Set when data is written to all six data registers and re3ady to be read.

    def get(self) -> int:
        return {'lock':self.lock, 'rdy':self.rdy}
        
    def fromBytes(self, vByte):
        self.lock = (vByte>>1)&1
        self.rdy  = vByte&1
        return self

class Id(Reg24):
    ad = IDA
    name = "id"

    def __init__(self):
        self.val = "" #< Should be "H43"

    def fromBytes(self, vByte):
        self.val = bytes(vByte)
        return self

def calcGauss(raw, GN):
    return raw*GNlsb[GN]
