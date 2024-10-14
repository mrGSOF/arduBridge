"""
MicroPython TM1640 LED matrix display driver
https://github.com/mcauser/micropython-tm1640

MIT License
Copyright (c) 2017-2023 Mike Causer
Modified by Guy Soffer to work with ArduBridge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

#from GSOF_ArduBridge.Sleep_us import *

__version__ = '1.0.0'

TM1640_CMD1   = 64  #< 0x40 data command
TM1640_CMD2   = 192 #< 0xC0 address command
TM1640_CMD3   = 128 #< 0x80 display control command
TM1640_DSP_ON = 8   #< 0x08 display on
TM1640_DELAY  = 10  #< 10us delay between clk/dio pulses

class TM1640():
    """Library for LED matrix display modules based on the TM1640 LED driver."""
    def __init__(self, sclk, sdo, cols=16, brightness=7):
        self.cols = cols
        self.sclk = sclk.set(0)
        self.sdo = sdo.set(0)

        if not 0 <= brightness <= 7:
            raise ValueError("Brightness out of range")
        self._brightness = brightness
        #sleep_us(TM1640_DELAY)
        self._write_data_cmd()
        self._write_dsp_ctrl()

    def _start(self):
        self.sdo.set(0)
        #sleep_us(TM1640_DELAY)
        self.sclk.set(0)
        #sleep_us(TM1640_DELAY)

    def _stop(self):
        self.sdo.set(0)
        #sleep_us(TM1640_DELAY)
        self.sclk.set(1)
        #sleep_us(TM1640_DELAY)
        self.sdo.set(1)

    def _write_data_cmd(self):
        # automatic address increment, normal mode
        self._start()
        self._write_byte(TM1640_CMD1)
        self._stop()

    def _write_dsp_ctrl(self):
        # display on, set brightness
        self._start()
        self._write_byte(TM1640_CMD3 | TM1640_DSP_ON | self._brightness)
        self._stop()

    def _write_byte(self, b):
        for i in range(8):
            self.sdo.set((b >> i) & 1)
            #sleep_us(TM1640_DELAY)
            self.sclk.set(1)
            #sleep_us(TM1640_DELAY)
            self.sclk.set(0)
            #sleep_us(TM1640_DELAY)

    def allOn(self) -> None:
        self.write([255]*self.cols)

    def allOff(self) -> None:
        self.write([0]*self.cols)

    def brightness(self, val=None):
        """
        Set the display brightness 0-7.
        brightness 0 = 1/16th pulse width
        brightness 7 = 14/16th pulse width
        """
        if val is None:
            return self._brightness
        if not 0 <= val <= 7:
            raise ValueError("Brightness out of range")

        self._brightness = val
        self._write_data_cmd()
        self._write_dsp_ctrl()

    def write(self, rows, pos=0):
        if not 0 <= pos <= 7:
            raise ValueError("Position out of range")

        self._write_data_cmd()
        self._start()

        self._write_byte(TM1640_CMD2 | pos)
        for row in rows:
            self._write_byte(row)

        self._stop()
        self._write_dsp_ctrl()

    def write_int(self, int, pos=0, len=8):
        self.write(int.to_bytes(len, 'big'), pos)

    def write_hmsb(self, buf, pos=0):
        self._write_data_cmd()
        self._start()

        self._write_byte(TM1640_CMD2 | pos)
        for i in range(7-pos, -1, -1):
            self._write_byte(buf[i])

        self._stop()
        self._write_dsp_ctrl()
