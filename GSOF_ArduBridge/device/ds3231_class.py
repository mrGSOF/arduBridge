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
from GSOF_ArduBridge.device import DS3231_RM as RM
class Reg():
    def __init__(self, i2c, dev, reg):
        self._i2c = i2c
        self._dev = dev
        self._reg = reg

    def read(self) -> None:
        vBytes = self._i2c.readRegister(self._dev, self._reg.ad, self._reg.size)
        if len(vBytes) == 1:
            vBytes = vBytes[0]
        return self._reg.fromBytes(vBytes)

    def write(self, **values) -> None:
        vByte = self._reg.toBytes(**values)
        print(vByte)
        self._i2c.writeRegister(self._dev, self._reg.ad, vByte)
        return self

class DS3231():
    def __init__(self, i2c, dev=0x68):
        self.seconds = Reg( i2c, dev, RM.Seconds() )
        self.minutes = Reg( i2c, dev, RM.Minutes() )
        self.hours   = Reg( i2c, dev, RM.Hours() )
        self.day     = Reg( i2c, dev, RM.Day() )
        self.date    = Reg( i2c, dev, RM.Date() )
        self.month   = Reg( i2c, dev, RM.Month() )
        self.year    = Reg( i2c, dev, RM.Year() )
        self.alarmSec1  = Reg( i2c, dev, RM.SecondsAlarm1() )
        self.alarmMin1  = Reg( i2c, dev, RM.MinutesAlarm1() )
        self.alarmHour1 = Reg( i2c, dev, RM.HoursAlarm1() )
        self.alarmDate1 = Reg( i2c, dev, RM.DateAlarm1() )
        self.alarmMin2  = Reg( i2c, dev, RM.MinutesAlarm2() )
        self.alarmHour2 = Reg( i2c, dev, RM.HoursAlarm2() )
        self.alarmDate2 = Reg( i2c, dev, RM.DateAlarm2() )
        self.control = Reg( i2c, dev, RM.Control() )
        self.status  = Reg( i2c, dev, RM.Status() )
        self.offset  = Reg( i2c, dev, RM.AgingOffset() )
        self.temp    = Reg( i2c, dev, RM.Temperature() )

    def setTime(self, hours, minutes, seconds):
        self.hours.write(h24=hours, military=1)
        self.minutes.write(minutes=minutes)
        self.seconds.write(seconds=seconds)

    def getTime(self):
        return self.hours.read().get() | \
               self.minutes.read().get() | \
               self.seconds.read().get()

    def setDate(self, year, month, day, weekday):
        cent = int((year%200)/100)
        year = year%100
        self.year.write(year=year)
        self.month.write(month=month, century=cent)
        self.date.write(date=day)
        self.day.write(day=weekday)

    def getDate(self):
        return self.year.read().get() | \
               self.month.read().get() | \
               self.date.read().get() | \
               self.day.read().get()
