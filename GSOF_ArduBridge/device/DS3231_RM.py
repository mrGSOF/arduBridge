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

### Registers mapping
SECONDS        = 0x00
MINUTES        = 0x01
HOURS          = 0x02
DAY            = 0x03
DATE           = 0x04
CENT_MONTH     = 0x05
YEAR           = 0x06
ALARM1_SECONDS = 0x07
ALARM1_MINUTES = 0x08
ALARM1_HOURS   = 0x09
ALARM1_DATE    = 0x0a
ALARM2_MINUTES = 0x0b
ALARM2_HOURS   = 0x0c
ALARM2_DATE    = 0x0d
CONTROL        = 0x0e
STATUS         = 0x0f
AGING_OFFSET   = 0x10
TEMP_MSB       = 0x11
TEMP_LSB       = 0x12

class Seconds():
    ad   = SECONDS
    size = 1
    def __init__(self):
        self.seconds = 0

    def get(self):
        return {"seconds":self.seconds}
        
    def toBytes(self, seconds) -> list:
        return [0xff&( (int(seconds/10)<<4) +(seconds%10) )]
    
    def fromBytes(self, byte) -> int:
        self.seconds = 10*(byte>>4) +(byte&0x0f)
        return self

class Minutes():
    ad   = MINUTES
    size = 1
    def __init__(self):
        self.minutes = 0
        
    def get(self):
        return {"minutes":self.minutes}

    def toBytes(self, minutes) -> list:
        minutes = int(minutes)
        return [0xff&( (int(minutes/10)<<4) +(minutes%10) )]
    
    def fromBytes(self, byte) -> int:
        self.minutes = 10*(byte>>4) +(byte&0x0f)
        return self

class Hours():
    ad   = HOURS
    size = 1
    def __init__(self):
        self.hours = 0
        
    def get(self):
        return {"hours":self.hours}

    def toBytes(self, h24, military) -> list:
        pm = 0
        h24 &= 0x1f
        if military == False:
            if h24 > 12:
                pm = 1
        military = int(military)
        h10 = int(bool(int(h24/10)))
        h20 = int(bool(int(h24/20)))
        hours = h24%10
        return [0xff&( (military<<6) +(pm<<5) +(h20<<5) +(h10<<4) +hours)]
    
    def fromBytes(self, byte) -> int:
        self.hours = 10*(0x3&(byte>>4)) +(byte&0xf)
        return self

class Day():
    ad   = DAY
    size = 1
    def __init__(self):
        self.day = 0

    def get(self):
        return {"day":self.day}

    def toBytes(self, day) -> list:
        day &= 0x7
        return [day]

    def fromBytes(self, byte) -> int:
        self.day  = byte&0x7      #< 1 to 7
        return self

class Date():
    ad   = DATE
    size = 1
    def __init__(self):
        self.date = 0

    def get(self):
        return {"date":self.date}

    def toBytes(self, date) -> list:
        date &= 0x1f
        d10 = int(date/10)
        date = date%10
        return [0xff&((d10<<4) +date )]

    def fromBytes(self, byte) -> int:
        self.date = 10*int(bool(byte&0x10)) +(byte&0xf)
        return self

class Month():
    ad   = CENT_MONTH
    size = 1
    def __init__(self):
        self.month = 0
        self.century = 0

    def get(self):
        return {"century":self.century, "month":self.month}

    def toBytes(self, month, century=0) -> list:
        month &= 0xf
        m10 = int(month/10)
        month = month%10
        return [0xff&( (century<<7) +(m10<<4) +month )]

    def fromBytes(self, byte) -> int:
        self.month = 10*int(bool(byte&0x10)) +(byte&0xf)
        self.century = int(bool(byte&0x80))
        return self

class Year():
    ad   = YEAR
    size = 1
    def __init__(self):
        self.year = 0

    def get(self):
        return {"year":self.year}

    def toBytes(self, year) -> list:
        y10 = int(year/10)
        year = year%10
        return [0xff&( (y10<<4) +year )]

    def fromBytes(self, byte) -> int:
        self.year = 10*(byte>>4) +(byte&0xf)
        return self

class SecondsAlarm1(Seconds):
    ad  = ALARM1_SECONDS
    def __init__(self):
        super().__init__()
        self.a1m1 = 0

    def get(self):
        return super().get() | {"A1M1":self.a1m1}
        
    def toBytes(self, seconds, a1m1=0) -> list:
        return [(a1m1<<7) +super().toBytes(second)]
    
    def fromBytes(self, byte) -> int:
        self.a1m1 = int(byte)>>7
        return super().fromBytes(byte)

class MinutesAlarm1(Minutes):
    ad  = ALARM1_MINUTES
    def __init__(self):
        super().__init__()
        self.a1m2 = 0
        
    def get(self):
        return super().get() | {"A1M2":self.a1m2}

    def toBytes(self, minutes, a1m2=0) -> list:
        return [(a1m2<<7) +super().toBytes(minutes)]
    
    def fromBytes(self, byte) -> int:
        self.a1m2 = int(byte)>>7
        return super().fromBytes(byte)

class HoursAlarm1(Hours):
    ad  = ALARM1_HOURS
    def __init__(self):
        super().__init__()
        self.a1m3 = 0
        
    def get(self):
        res = super().get() | {"A1M3":self.a1m3}

    def toBytes(self, hours24, militay, a1m3=0) -> list:
        return [(a1m3<<7) +super.toBytes(hours24, military)]
    
    def fromBytes(self, byte) -> int:
        self.a1m3 = int(byte)>>7
        return super().fromBytes(byte)

class DateAlarm1(Date):
    ad  = ALARM1_DATE
    def __init__(self):
        super().__init__()
        self.dydt = 0
        self.a1m4 = 0

    def get(self):
        res = super().get() | {"A1M4":self.a1m4}

    def toBytes(self, date, dydt, a1m4=0) -> list:
        date &= 0x1f
        d10 = int(date/10)
        date = date%10
        return [(a1m4<<7) +(dydt<<6) +0x3f&super.toBytes(date)]

    def fromBytes(self, byte) -> int:
        byte = 0xff&int(byte)
        self.a1m4 = byte>>7
        self.dydt = 0x1&(byte>>6)
        return super().fromBytes(byte)

class MinutesAlarm2(MinutesAlarm1):
    ad  = ALARM2_MINUTES

class HoursAlarm2(HoursAlarm1):
    ad  = ALARM2_HOURS

class DateAlarm2(DateAlarm1):
    ad  = ALARM2_DATE
    
class Control():
    ad  = CONTROL
    size = 1
    def __init__(self):
        self.nEOSC = 0
        self.BBSQW = 0
        self.CONV  = 0
        self.RS    = 0
        self.INTCN = 0
        self.A2IE  = 0
        self.A1IE  = 0

    def get(self):
        return {"nEOSC":self.nEOSC,
                "BBSQW":self.BBSQW,
                "CONV" :self.CONV,
                "RS"   :self.RS,
                "INTCN":self.INTCN,
                "A2IE" :self.A2IE,
                "A1IE" :self.A1IE,}

    def toBytes(self,
                nEOSC = 0, #< Enable oscilator
                BBSQW = 0, #< Battery-Backed Square-Wave Enable
                CONV  = 0, #< Convert Temperature
                RS    = 3, #< Rate Select
                INTCN = 1, #< Interrupt Control
                A2IE  = 0, #< Alarm 2 Interrupt Enable
                A1IE  = 0, #< Alarm 1 Interrupt Enable
               ) -> bytes:
        return bytes([(nEOSC<<7) +(BBSQW<<6) +(CONV<<5) +(RS<<3) +(INTCN<<2) +(A2IE<<1) +A1IE])
    
    def fromBytes(self, byte) -> int:
        byte = int(byte)
        self.nEOSC = int(bool(byte&0x80))
        self.BBSQW = int(bool(byte&0x40))
        self.CONV  = int(bool(byte&0x20))
        self.RS    = 0x3&(byte>>3)
        self.INTCN = int(bool(byte&0x04))
        self.A2IE  = int(bool(byte&0x02))
        self.A1IE  = int(bool(byte&0x01))
        return self
    
class Status():
    ad   = STATUS
    size = 1
    def __init__(self):
        self.OSF     = 0 #< Oscilator Stop Flag
        self.EN32KHz = 0 #< Enable 32KHz Output
        self.BSY     = 0 #< Busy flag
        self.A2F     = 0 #< Alarm 2 Flag
        self.A1F     = 0 #< Alarm 1 Flag

    def get(self):
        return {"OSF"    :self.OSF,
                "EN32KHz":self.EN32KHz,
                "BSY"    :self.BSY,
                "A2F"    :self.A2F,
                "A1F"    :self.A1F,}

    def toBytes(self,
                EN32KHz, #< Enable 32KHz Output
                A2F,     #< Alarm 2 Flag
                A1F,     #< Alarm 1 Flag
               ) -> list:
        return [(EN32KHz<<3) +(A2F<<1) +A1F]
    
    def fromBytes(self, byte) -> int:
        byte = int(byte)
        self.OSF     = int(bool(byte&0x80))
        self.EN32KHz = int(bool(byte&0x08))
        self.BSY     = int(bool(byte&0x04))
        self.A2F     = int(bool(byte&0x02))
        self.A1F     = int(bool(byte&0x01))
        return self

class AgingOffset():
    ad   = AGING_OFFSET
    size = 1
    def __init__(self):
        self.offset = 0

    def get(self):
        return {"agingOffset":self.offset}
    
    def toBytes(self, offset) -> list:
        return [offset]
    
    def fromBytes(self, byte) -> int:
        byte = int(byte)
        self.offset = int(byte)
        return self

class Temperature():
    ad   = TEMP_MSB
    size = 2
    def __init__(self):
        self.temp_C = 0
    
    def get(self):
        return {"temp_C":self.temp_C}
    
    def toBytes(self, date) -> list:
        return [0xff&int(self.temp_C*4)]

    def fromBytes(self, byte) -> int:
        temp  = (byte[1]&0xc0)>>6 #> LSB
        temp += (byte[0])<<8      #< MSB
        self.temp_C = (temp>>6)*0.25
        return self
