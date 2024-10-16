# -*- coding: cp1255 -*-
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
# Modified: Guy Soffer to work with arduBridge (2021)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division
import time


class WaveshareBase():
    """Base class for Waveshare-based ePaper displays.  Implementors should subclass
    and provide an implementation for the _initialize function.
    """

    def __init__(self, width, height, rst, cs, dc, busy, spi):
        self.spi    = spi
        self.rst    = rst
        self.cs     = cs
        self.dc     = dc
        self.isBusy = busy
        self.width  = width
        self.height = height
        self._pages = height//8
        self._buffer = [0]*(width*self._pages)

    def command(self, c):
        self.dc(0)
        self.cs(0)
        self.spi.write_read( [0x00, c] ) #< Data out on falling edge
        self.cs(1)

    def data(self, c):
        self.dc(1)
        self.cs(0)
        self.spi.write_read( [0x40, c] ) #< Data out on falling edge
        self.cs(1)

    def EPD_W21_Init(self):
        self.reset()

    def initialize(self):
        self.reset()

        self.command(0x06) #<boost soft start
        self.data(0x07) #<A
        self.data(0x07) #<B
        self.data(0x17) #<C       

        self.command(0x04)  
        self.lcd_chkstatus()

        self.command(0x00) #<panel setting
        self.data(0x0f)    #< LUT

        self.command (0x16)
        self.data(0x00) #<KW-BF   KWR-AF	BWROTP 0f	

        self.command(0xF8)
        self.data (0x60)
        self.data(0xa5)

        self.command(0xF8)
        self.data(0x73)
        self.data(0x23)

        self.command(0xF8)
        self.data(0x7C)
        self.data(0x00)

    def EPD_refresh(self):
        EPD_W21_WriteCMD(0x12) #<DISPLAY REFRESH 	
        time.sleep(0.01) #<!!!The delay here is necessary, 200uS at least!!!     
        self.lcd_chkstatus()

    def EPD_sleep(self):
        self.command(0X02) #< power off
        self.command(0X07) #< deep sleep
        self.data(0xA5)

    def PIC_display(self, picData_old, picData_new):
        self.data(0x10) #< Transfer old data
        for i in range(0,5808):	     
            self.data(picData_old[i]);
            self.command(0x13) #< Transfer new data

        for i in range(0,5808):	     
            self.data(picData_new[i]);

    def PIC_display_Clean(self):
        self.command(0x10) #< Transfer old data
        for i in range(0,5808):	     
            self.data(0x00)

        self.command(0x13) #< Transfer new data
        for i in range(0,5808):	     
            self.data(0x00)

    def lcd_chkstatus(self):
        while(self.isBusy()):   
            self.command(0x71);
        time.sleep(0.001);                       

    def begin(self, vccstate=None):
        return

    def reset(self):
        """Reset the display."""
        if self.rst is not None:
            # Set reset high for a 10 ms.
            self.rst(1)
            time.sleep(0.01)
            # Set reset low for 10 milliseconds.
            self.rst(0)
            time.sleep(0.01)
            # Set reset high again.
            self.rst(1)

    def display(self, picData_old, picData_new):
        self.PIC_display(self, picData_old, picData_new)

    def clear(self):
        """Clear contents of image buffer."""
        self._buffer = [0]*(self.width*self._pages)

class Waveshare_264_176(WaveshareBase):
    def __init__(self, rst, cs, dc, busy, spi):
        super().__init__(264, 176, rst, cs, dc, busy, spi)
        #super(Waveshare_264_176, self).__init__(264, 176, rst, cs, dc, busy, spi)

class Waveshare_400_300(WaveshareBase):
    def __init__(self, rst, cs, dc, busy, spi):
        super().__init__(400, 300, rst, cs, dc, busy, spi)
        #super(Waveshare_264_176, self).__init__(264, 176, rst, cs, dc, busy, spi)
