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

class Pin():
    def __init__(self, gpio, pin):
        self.pin = pin
        self.gpio = gpio

    def high(self):
        self.gpio.setPin(self.pin, 1)
        return self

    def low(self):
        self.gpio.setPin(self.pin, 0)
        return self

    def set(self, val):
        self.gpio.setPin(self.pin, int(bool(val)))
        return self

class AD9833():
    def __init__(self, gpio, sdata, sclk, fsync, osci_hz=25e6):
        self.fsync = Pin(gpio, fsync).high()
        self.sclk  = Pin(gpio, sclk).high()
        self.sdata = Pin(gpio, sdata).low()
        self._clkFreq = osci_hz

    def setFreq(self, f):
        flag_b28  = 1<<13
        flag_freq = 1<<14
        scale = 1<<28
        n_reg = int(f * scale / self._clkFreq)
        word_low = n_reg& 0x3fff
        word_hi  = (n_reg>>14)&0x3fff

        self._sendWord(flag_b28)
        self._sendWord(flag_freq | word_low)
        self._sendWord(flag_freq | word_hi)

    def _sendWord(self, word):
        self.fsync.low()
        mask = 1<<15      #< MSB first
        while mask > 0:
            self.sdata.set(bool(word & mask))
            mask >>= 1
            self.sclk.low().high()
        self.sdata.low()
        self.fsync.high()
