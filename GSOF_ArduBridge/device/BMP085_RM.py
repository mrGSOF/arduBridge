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

I2C_AD = 0x77

### Calibraction coefficients
AC1_H = 0xAA
AC1_L = 0xAB
AC2_H = 0xAC
AC2_L = 0xAD
AC3_H = 0xAE
AC3_L = 0xAF
AC4_H = 0xB0
AC4_L = 0xB1
AC5_H = 0xB2
AC5_L = 0xB3
AC6_H = 0xB4
AC6_L = 0xB5
B1_H  = 0xB6
B1_L  = 0xB7
B2_H  = 0xB8
B2_L  = 0xB9
MB_H  = 0xBA
MB_L  = 0xBB
MC_H  = 0xBC
MC_L  = 0xBD
MD_H  = 0xBE
MD_L  = 0xBF

###Registers
ID       = 0xD0
VER      = 0xD1
#RST      = 0xE0 #< No documentation
CMD      = 0xF4
ADC_MSB  = 0xF6
ADC_LSB  = 0xF7
ADC_XLSB = 0xF8

#Commands
TS        = 0x2E #< 0b00101110 Temperature-Sample 4.5ms
PS        = 0x34 #< 0bxy110100 xy = oss value
PS_4p5ms  = 0x34 #< Pressure-Sample 4.5ms
PS_7p5ms  = 0x74 #< Pressure-Sample 7.5ms
PS_13p5ms = 0xB4 #< Pressure-Sample 13.5ms
PS_25p5ms = 0xF4 #< Pressure-Sample 25.5ms

OSS = []
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

class AC1(RegS16):
    ad  = AC1_H

class AC2(RegS16):
    ad = AC2_H

class AC3(RegS16):
    ad = AC3_H

class AC4(Reg16):
    ad = AC4_H

class AC5(Reg16):
    ad = AC5_H

class AC6(Reg16):
    ad = AC6_H

class B1(RegS16):
    ad = B1_H

class B2(RegS16):
    ad = B2_H

class MB(RegS16):
    ad = MB_H

class MC(RegS16):
    ad = MC_H

class MD(RegS16):
    ad = MD_H
    
class ID(Reg8):
    ad = ID
    name = 'id'

class VER(Reg8):
    ad = VER
    name = 'ver'

#class RST(Reg8): #< No documentation
#    ad = RST

class CMD(Reg8):
    ad = CMD

    def toBytes(self, smpT=False, smpP=False, oss=0) -> list:
        if smpT == True:
            cmd = TS
        elif smpP == True:
            cmd = PS +((oss&3)<<6)
        return [cmd]

class ADC16(Reg16):
    ad = ADC_MSB

class ADC24(Reg24):
    ad = ADC_MSB

def calcPressure_Pa(raw, AC1, AC2, AC3, AC4, B1, B2, oss=0, b5=None, temp=25.0):
    """Convert the raw pressure value to Pascal value"""
    """Calibration values and temperature should be read prior to this command"""
    raw = raw>>( 8 -oss )
    b6 = b5 - 4000

    ### calculate B3
    x1 = (b6*b6) >> 12
    x1 = (x1 *B2)>>11
    x2 = (AC2*b6)>>11
    x3 = (x1 + x2)
    b3 = ( ( ( (AC1*4 + x3) <<oss )+ 2) >> 2 )

    ### calculate B4
    x1 = (AC3* b6) >> 13
    x2 = (B1 * ((b6*b6) >> 12) ) >> 16
    x3 = ((x1 + x2) + 2) >> 2
    b4 = (AC4 * (x3 + 32768)) >> 15
     
    ### calculate B7
    b7 = ( raw - b3) * (50000>>oss)
    if (b7 < 0x80000000):
        p = int((b7 << 1) / b4)
    else:
        p = int(b7 / b4) << 1

    x1 = (p >> 8)**2
    x1 = (x1 * 3038) >> 16
    x2 = (-7357*p) >> 16
    p += (x1 + x2 + 3791) >> 4 #< pressure in Pa
    return p

def calcTemperature_C(raw, AC5, AC6, MC, MD):
    """Converts the raw temperature value to Centigrade and returns it together with B5 coefficient"""
    x1 = (AC5*(raw - AC6 )) >>15
    x2 = (MC<<11) / (x1 + MD)
    b5 = int(x1 + x2)
    TEMP = ((b5 + 8)>>4)/10.0
    return (TEMP, b5)
