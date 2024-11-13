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

### Registers mapping
ID            = 0x00 #< 0xe5
THRS_TAP      = 0x1D
OFSX          = 0x1E
OFSY          = 0x1F
OFSZ          = 0x20
DUR           = 0x21
LATENT        = 0x22
WINDOW        = 0x23
THRS_ACT      = 0x24
THRS_INACT    = 0x25
TIME_INACT    = 0x26
ACT_INACT_CTL = 0x27
THRS_FF       = 0x28
TIME_FF       = 0x29
TAPAXES       = 0x2A
ACT_TAP_STS   = 0x2B
BW_RATE       = 0x2C
POWER_CTL     = 0x2D
INT_ENABLE    = 0x2E
INT_MAP       = 0x2F
INT_SOURCE    = 0x30
DATA_FORMAT   = 0x31
DATAX_L       = 0x32
DATAX_H       = 0x33
DATAY_L       = 0x34
DATAY_H       = 0x35
DATAZ_L       = 0x36
DATAZ_H       = 0x37
FIFO_CTL      = 0x38
FIFO_STS      = 0x39

g = 9.81
ODRhz   = [0.1, 0.2, 0.39, 0.78, 1.56, 3.13, 6.25, 12.5, 25, 50, 100, 200, 400, 800, 1600, 3200]
ODRua   = [23,  23,  23,   23,   34,   40,   45,   50,   60, 90, 140, 140, 140, 140, 90, 140]
ODRualp = [23,  23,  23,   23,   34,   40,   45,   34,   40, 45,  50,  60,  90, 140, 90, 140]
WU    = [8, 4, 2, 1]  #< Hz
RA    = [2, 4, 8, 16] #< +/- g
RAlsb = [2/1024/g, 4/1024/g, 8/1024/g, 16/1024/g] #< mpss/lsb
FM    = ["bypass", "fifo", "stream", "trigger"]

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

class RegS8(Reg8):
    def fromBytes(self, vByte):
        super().fromBytes(vByte)
        if self.val > 0x7F:
            self.val = -1*(((~self.val)+1)&0xff)
        return self
    
class Reg16(Reg8):
    size = 2
    def toBytes(self, val) -> list:
        val = int(val)
        msb  = (val>>8)&0xff
        lsb = val&0xff
        return [lsb, Msb]
    
    def fromBytes(self, vByte):
        self.val = vByte[1]*256 +vByte[0]
        return self

class RegS16(Reg16):
    def fromBytes(self, vByte):
        super().fromBytes(vByte)
        if self.val > 0x7FFF:
            self.val = -1*(((~self.val)+1)&0xffff)
        return self

##class Reg24(Reg16):
##    size = 3
##
##    def toBytes(self, val) -> list:
##        val = int(val)
##        msb  = (val>>16)&0xff
##        lsb  = (val>>8)&0xff
##        xlsb = val&0xff
##        return [msb, lsb, xlsb]
##
##    def fromBytes(self, vByte):
##        self.val = (vByte[0]<<16) +(vByte[1]<<8) +vByte[2]
##        return self

class Id(Reg8):
    ad = ID
    name = 'id'

class ThrsTap(Reg8):
    ad = THRS_TAP
    lsb = 62.5/1000/g #< 62.5 mg/lsb
    name = 'thrs_tap'

    def toBytes(self, val) -> list:
        return [0xff&(val/self.lsb)]
    
    def fromBytes(self, byte):
        self.val = byte*self.lsb
        return self

class OfsX(ThrsTap):
    ad = OFSX
    name = 'ofsx'
    lsb = 15.6/1000/g #< mg/lsb

class OfsY(OfsX):
    ad = OFSY
    name = 'ofsy'

class OfsZ(OfsX):
    ad = OFSZ
    name = 'ofsz'

class Dur(Reg8):
    ad = DUR
    name = 'dur'
    lsb = 625/1000000 #< 625 us/lsb

class Latent(Dur):
    ad = LATENT
    name = 'latent'
    lsb = 1.25/1000 #< 1.25 ms/lsb

class Window(Dur):
    ad = WINDOW
    lsb = 1.25/1000 #< 1.25 ms/lsb

class ActInactCtrl(Reg8):
    ad = ACT_INACT_CTL

    def __init__(self):
        self.act_ac_dc   = 0
        self.actXen      = 0
        self.actYen      = 0
        self.actZen      = 0
        self.inact_ac_dc = 0
        self.inactXen    = 0
        self.inactYen    = 0
        self.inactZen    = 0

    def get(self):
        return {'act_ac_dc':self.act_ac_dc,
                'actXen':self.actXen,
                'actYen':self.actYen,
                'actZen':self.actZen,
                'inact_ac_dc':self.inact_ac_dc,
                'inactXen':self.inactXen,
                'inactYen':self.inactYen,
                'inactZen':self.inactZen}

    def toBytes(self,
                act_ac_dc=0, actXen=0, actYen=0, actZen=0,
                inact_ac_dc=0, inactXen=0, inactYen=0, inactZen=0) -> list:
        val  = (act_ac_dc&1)<<7
        val += (actXen&1)<<6
        val += (actYen&1)<<5
        val += (actZen&1)<<4
        val += (inact_ac_dc&1)<<3
        val += (inactXen&1)<<2
        val += (inactYen&1)<<1
        val += inactZen&1
        return [val]

    def fromBytes(self, vByte):
        self.act_ac_dc   = (vByte>>7)&1
        self.actXen      = (vByte>>6)&1
        self.actYen      = (vByte>>5)&1
        self.actZen      = (vByte>>4)&1
        self.inact_ac_dc = (vByte>>3)&1
        self.inactXen    = (vByte>>2)&1
        self.inactYen    = (vByte>>1)&1
        self.inactZen    = vByte&1
        return self

class Thrs_ff(Reg8):
    ad = THRS_FF

    def __init__(self):
        self.suppress = 0
        self.tapXen   = 0
        self.tapYen   = 0
        self.tapZen   = 0

    def get(self):
        return {'suppress':self.suppress,
                'tapXen':self.tapXen,
                'tapYen':self.tapYen,
                'tapZen':self.tapZen}

    def toBytes(self, suppress=0, tapXen=0, tapYen=0, tapZen=0) -> list:
        val  = (suppress&1)<<3
        val += (tapXen&1)<<2
        val += (tapYen&1)<<1
        val += tapZen&1
        return [val]

    def fromBytes(self, vByte):
        self.suppress = (vByte>>3)&1
        self.tapXen   = (vByte>>2)&1
        self.tapYen   = (vByte>>1)&1
        self.tapZen   = vByte&1
        return self

class ActTapStatus(Reg8):
    ad = ACT_TAP_STS

    def __init__(self):
        self.actXsrc = 0
        self.actYsrc = 0
        self.actZsrc = 0
        self.asleep  = 0
        self.tapXsrc = 0
        self.tapYsrc = 0
        self.tapZsrc = 0

    def get(self):
        return {'actXsrc':self.actXsrc,
                'actYsrc':self.actYsrc,
                'actZsrc':self.actZsrc,
                'asleep':self.asleep,
                'tapXsrc':self.tapXsrc,
                'tapYsrc':self.tapYsrc,
                'tapZsrc':self.tapZsrc}

    def toBytes(self,
                actXsrc=0, actYsrc=0, actZsrc=0, asleep=0,
                tapXsrc=0, tapYsrc=0, tapZsrc=0) -> list:
        val  = (actXsrc&1)<<6
        val += (actYsrc&1)<<5
        val += (actZsrc&1)<<4
        val += (asleep&1)<<3
        val += (tapXsrc&1)<<2
        val += (tapYsrc&1)<<1
        val +=  tapZsrc&1
        return [val]

    def fromBytes(self, vByte):
        self.actXsrc = (vByte>>6)&1
        self.actYsrc = (vByte>>5)&1
        self.actZsrc = (vByte>>4)&1
        self.asleep  = (vByte>>3)&1
        self.tapXsrc = (vByte>>2)&1
        self.tapYsrc = (vByte>>1)&1
        self.tapZsrc = vByte&1
        return self

class BwRate(Reg8):
    ad = BW_RATE

    def __init__(self):
        self.low_power = 0
        self.rate = 0

    def get(self):
        uaTbl = DOua
        if low_power != False:
            uaTbl = DOualp
        ua = uaTblt[self.rate]
        return {'low_power':self.low_power,
                'ua':ua,
                'rate':DOhz[self.rate]}

    def toBytes(self, lowPower=0, rate=12.5) -> list:
        val  = (lowPower&1)<<4
        val +=  DOhz.index(rate)
        return [val]

    def fromBytes(self, vByte):
        self.low_power = (vByte>>4)&1
        self.rate      = vByte&0xf
        return self

class PowerCtrl(Reg8):
    ad = POWER_CTL

    def __init__(self):
        self.link = 0
        self.autoSleep = 0
        self.measure = 0
        self.sleep = 0
        self.wakeup = 0

    def get(self):
        return {'link':self.link,
                'autoSleep':self.autoSleep,
                'measure':self.measure,
                'sleep':self.sleep,
                'wakeup':WU[self.wakeup]}

    def toBytes(self, link=0, autoSleep=0, measure=0, sleep=0, wakeup=0) -> list:
        val  = (link&1)<<5
        val += (autoSleep&1)<<4
        val += (measure&1)<<3
        val += (sleep&1)<<2
        val += wakeup&3
        return [val]

    def fromBytes(self, vByte):
        self.link     = (vByte>>5)&1
        self.autoSleep = (vByte>>4)&1
        self.measure   = (vByte>>3)&1
        self.sleep     = (vByte>>2)&1
        self.wakeup    = vByte&0x3
        return self

class IntEnable(Reg8):
    ad = INT_ENABLE

    def __init__(self):
        self.dataRdy = 0
        self.singleTap = 0
        self.doubleTap = 0
        self.activity = 0
        self.inactivity = 0
        self.freeFall = 0
        self.watermark = 0
        self.overrun = 0

    def get(self):
        return {'dataRdy':self.dataRdy,
                'singleTap':self.singleTap,
                'doubleTap':self.doubleTap,
                'activity':self.activity,
                'inactivity':self.inactivity,
                'freeFall':freeFall,
                'watermark':watermark,
                'overrun':overrun}

    def toBytes(self, dataRdy=0, singleTap=0, doubleTap=0,
                activity=0, inactivity=0, freeFall=0,
                watermark=0, overrun=0) -> list:
        val  = (dataRdy&1)<<7
        val += (singleTap&1)<<6
        val += (doubleTap&1)<<5
        val += (activity&1)<<4
        val += (inactivity&1)<<3
        val += (freeFall&1)<<2
        val += (watermark&1)<<1
        val += overrun&1
        return [val]

    def fromBytes(self, vByte):
        self.dataRdy    = (vByte>>7)&1
        self.singleTap  = (vByte>>6)&1
        self.doubleTap  = (vByte>>5)&1
        self.activity   = (vByte>>4)&1
        self.inactivity = (vByte>>3)&1
        self.freeFall   = (vByte>>2)&1
        self.watermark  = (vByte>>1)&1
        self.overrun    = vByte&0x1
        return self

class IntMap(IntEnable):
    ad = INT_MAP

class IntSource(IntEnable):
    ad = INT_SOURCE

class DataFormat(Reg8):
    ad = DATA_FORMAT

    def __init__(self):
        self.selftest = 0
        self.spi = 0
        self.intInvert = 0
        self.fullRes = 0
        self.justify = 0
        self.range = 0

    def get(self):
        return {'selftest':self.selftest,
                'spi':self.spi,
                'intInvert':self.intInvert,
                'fullRes':self.fullRes,
                'justify':self.justify,
                'range':self.range}

    def toBytes(self, selftest=0, spi=0, intInvert=0,
                fullRes=0, justify=0, Range=0) -> list:
        val  = (selftest&1)<<7
        val += (spi&1)<<6
        val += (intInvert&1)<<5
        val += (fullRes&1)<<3
        val += (justify&1)<<2
        val += Range&3
        return [val]

    def fromBytes(self, vByte):
        self.selftest  = (vByte>>7)&1
        self.spi       = (vByte>>6)&1
        self.intInvert = (vByte>>5)&1
        self.fullRes   = (vByte>>3)&1
        self.justify   = (vByte>>2)&1
        self.range     = vByte&0x3
        return self

class DataX(RegS16):
    ad = DATAX_L
    name = "datax"

class DataY(RegS16):
    ad = DATAY_L
    name = "datay"

class DataZ(RegS16):
    ad = DATAZ_L
    name = "dataz"

class FifoCtrl(Reg8):
    ad = FIFO_CTL

    def __init__(self):
        self.fifoMode = 0
        self.trigger = 0
        self.samples = 0

    def get(self):
        return {'fifo_mode':FM[self.fifoMode],
                'trigger':self.trigger,
                'samples':self.samples}

    def toBytes(self, fifoMode=FM[0], trigger=0, samples=0) -> list:
        val  = FM[fifoMode]<<6
        val += (trigger&1)<<5
        val += samples&0x1f
        return [val]

    def fromBytes(self, vByte):
        self.fifoMode = (vByte>>6)&3
        self.trigger  = (vByte>>5)&1
        self.samples  = vByte&0x1f
        return self

class FifoStatus(Reg8):
    ad = FIFO_STS

    def __init__(self):
        self.fifoTrig = 0
        self.entries = 0

    def get(self):
        return {'fifo_trig':self.fifo_trig,
                'entries':self.entries}

    def toBytes(self, fifo_trig=0, entries=0) -> list:
        val  = (fifo_trig&1)<<7
        val += entries&0x3f
        return [val]

    def fromBytes(self, vByte):
        self.fifo_trig = (vByte>>7)&1
        self.entries   = vByte&0x3f
        return self

def calcAccRightJestify(raw):
    return raw*0.004*g
    
def calcAccLeftJestify(raw, ra):
    return raw*RAlsb[ra]*g
