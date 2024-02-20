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

# CONSTANTS
SSD1306_DUMMY_BYTE = 0x00
SSD1306_I2C_ADDRESS = 0x3C    # 011110+SA0 (+RW) - 0x3C or 0x3D (not including the R/W bit)
SSD1306_SETCONTRAST = 0x81
SSD1306_DISPLAYALLON_RESUME = 0xA4
SSD1306_DISPLAYALLON = 0xA5
SSD1306_NORMALDISPLAY = 0xA6
SSD1306_INVERTDISPLAY = 0xA7
SSD1306_DISPLAYOFF = 0xAE
SSD1306_DISPLAYON = 0xAF
SSD1306_SETDISPLAYOFFSET = 0xD3
SSD1306_SETCOMPINS = 0xDA
SSD1306_SETVCOMDETECT = 0xDB
SSD1306_SETDISPLAYCLOCKDIV = 0xD5
SSD1306_SETPRECHARGE = 0xD9
SSD1306_SETMULTIPLEX = 0xA8
SSD1306_SETLOWCOLUMN = 0x00
SSD1306_SETHIGHCOLUMN = 0x10
SSD1306_SETSTARTLINE = 0x40
SSD1306_MEMORYMODE = 0x20
SSD1306_COLUMNADDR = 0x21
SSD1306_PAGEADDR = 0x22
SSD1306_COMSCANINC = 0xC0
SSD1306_COMSCANDEC = 0xC8
SSD1306_SEGREMAP = 0xA0
SSD1306_CHARGEPUMP = 0x8D
SSD1306_EXTERNALVCC = 0x1
SSD1306_SWITCHCAPVCC = 0x2

# Scrolling constants
SSD1306_ACTIVATE_SCROLL = 0x2F
SSD1306_DEACTIVATE_SCROLL = 0x2E
SSD1306_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1306_RIGHT_HORIZONTAL_SCROLL = 0x26
SSD1306_LEFT_HORIZONTAL_SCROLL = 0x27
SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL = 0x2A


class SSD1306_base():
    """
    Base class for SSD1306 OLED displays. Implementors should subclass
    and provide an implementation for the _initialize() method
    """
    def __init__(self, width, height, i2c, dev=SSD1306_I2C_ADDRESS, rst=None):
        """
        :param width - Display's resolution on the horizontal axis (pixels)
        :param height - Display's resolution on the vertical axis (pixels)
        :param rst - Remote GPO function to set and reset the displays reset pin (optional)
        :param i2c - An I2C object to communicate with the display
        :param dev - The display's address (7 bit) on the I2C bus (not including the RW bit)
        """
        self.dev = dev
        self.i2c = i2c
        self.rst = rst
        self.width = width
        self.height = height
        self._pages = height//8                #< pages are like horizontale rows with 8 pixles height
        self._buffer = [0]*(width*self._pages) #< Local display-buffer
        self._vccstate = None

    def _initialize(self) -> None:
        raise NotImplementedError

    def _command(self, c) -> None:
        """Send command byte to display"""
        if type(c) == int:
            cmd = [0x00, c]
        else:
            cmd = [0x00] +c
        self.i2c.writeRaw(self.dev, cmd) #< Co = 0, DC = 0

    def _data(self, vDat) -> None:
        """Send data byte to display"""
        self.i2c.writeRegister( self.dev, 0x40, vDat) #< Co = 0, DC = 1

    def begin(self, vccstate=SSD1306_SWITCHCAPVCC) -> None:
        """Initialize the display. Call this method first after power-cycle"""
        self._vccstate = vccstate        #< Save vcc state (used in _initialize() and dim() methods
        self.reset()                     #< Reset
        self._initialize()               #< Initialize display
        self._command(SSD1306_DISPLAYON) #< Turn on the display.

    def reset(self) -> None:
        """Reset the display, if remote GPO function exists"""
        if self.rst != None:
            self.rst(1)          #< Set reset high for a millisecond.
            time.sleep(0.001)
            self.rst(0)          #< Set reset low for 10 milliseconds.
            time.sleep(0.010)
            self.rst(1)          #< Set reset high again.

        time.sleep(0.010)
        if self._vccstate == None:
            self.begin()

    def display(self) -> None:
        """Copy the local display-buffer to the display's physical memory"""
        cmd = [SSD1306_COLUMNADDR,
               0x00,                       #< Column start address (0 = reset)
               self.width-1,               #< Column end address
               SSD1306_PAGEADDR,
               0x00,                       #< Page start address (0 = reset)
               self._pages-1]              #< Page end address
        self._command(cmd)

        bytesInRow = int(self.width/8)
        for i in range(0, len(self._buffer), bytesInRow): #< Write the display-buffer row-by-row 
            self._data(self._buffer[i:i+bytesInRow])      #< Send a row of pixels

    def image(self, image) -> None:
        """
        Set buffer to value of Python Imaging Library image. The image should
        be in 1 bit mode and a size equal to the display size
        :param image - 
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                .format(self.width, self.height))
        
        pix = image.load()                       #< Grab all the pixels from the image, faster than getpixel
        index = 0
        for page in range(self._pages):          #< Iterate through all memory pages
            for x in range(self.width):          #< Iterate through all columns
                bits = 0
                for bit in (0, 1, 2, 3, 4, 5, 6, 7): #< Don't use range here as it's a bit slow
                    ### Set the bits for the column of pixels at the current position
                    bits = bits << 1                                #< Make room for the new bit
                    bits |= 0 if pix[(x, page*8+7-bit)] == 0 else 1 #< and set its value
                self._buffer[index] = bits                          #< Update local buffer with the new byte value
                index += 1                                          #< and increment to next byte
                   
    def scrollStop(self) -> None:
        self._command(SSD1306_DEACTIVATE_SCROLL)

    def scroll(self, sPage, ePage, left=True, spd=0) -> None:
        self.scrollStop()
        if left:
            self._command(SSD1306_LEFT_HORIZONTAL_SCROLL)
        else:
            self._command(SSD1306_RIGHT_HORIZONTAL_SCROLL)
        self._command(0x00)
        self._command(sPage)
        self._command(spd)
        self._command(ePage)
        self._command(0x00)
        self._command(0xff)
        self._command(SSD1306_ACTIVATE_SCROLL)
        
    def clear(self) -> None:
        """Clear contents of local display-buffer"""
        self._buffer = [0]*(self.width*self._pages)

    def setContrast(self, contrast) -> None:
        """Sets the contrast of the display. Value should be between 0 and 255"""
        if (contrast < 0) or (contrast > 255):
            raise ValueError("Contrast must be a value between 0 to 255 (inclusive)")
        self._command(SSD1306_SETCONTRAST)
        self._command(contrast)

    def dim(self, dim) -> None:
        """
        Adjusts contrast to dim the display if dim is True, otherwise sets the
        contrast to normal brightness if dim is False
        """
        #contrast = 0  #< Assume dim display
        if not dim:
            ### Adjust contrast based on VCC if not dimming
            if self._vccstate == SSD1306_EXTERNALVCC:
                contrast = 0x9F
            else:
                contrast = 0xCF
            self.setContrast(contrast)

class SSD1306_128_64(SSD1306_base):
    def __init__(self, i2c=None, dev=SSD1306_I2C_ADDRESS, rst=None):
        """Call the base class constructor with the proper display parameters (128x64)"""
        super().__init__(128, 64, i2c, dev, rst)

    def _initialize(self):
        """128x64 pixel specific initialization"""
        self._command(SSD1306_DISPLAYOFF)                    # 0xAE
        self._command(SSD1306_SETDISPLAYCLOCKDIV)            # 0xD5
        self._command(self.width)                            # the suggested ratio 0x80
        self._command(SSD1306_SETMULTIPLEX)                  # 0xA8
        self._command(self.height -1)
        self._command(SSD1306_SETDISPLAYOFFSET)              # 0xD3
        self._command(0x0)                                   # no offset
        self._command(SSD1306_SETSTARTLINE | 0x0)            # line #0
        self._command(SSD1306_CHARGEPUMP)                    # 0x8D
        if self._vccstate == SSD1306_EXTERNALVCC:
            self._command(0x10)
        else:
            self._command(0x14)
        self._command(SSD1306_MEMORYMODE)                    # 0x20
        self._command(0x00)                                  # 0x0 act like ks0108
        self._command(SSD1306_SEGREMAP | 0x1)
        self._command(SSD1306_COMSCANDEC)
        self._command(SSD1306_SETCOMPINS)                    # 0xDA
        self._command(0x12)
        self._command(SSD1306_SETCONTRAST)                   # 0x81
        if self._vccstate == SSD1306_EXTERNALVCC:
            self._command(0x9F)
        else:
            self._command(0xCF)
        self._command(SSD1306_SETPRECHARGE)                  # 0xd9
        if self._vccstate == SSD1306_EXTERNALVCC:
            self._command(0x22)
        else:
            self._command(0xF1)
        self._command(SSD1306_SETVCOMDETECT)                 # 0xDB
        self._command(0x40)
        self._command(SSD1306_DISPLAYALLON_RESUME)           # 0xA4
        self._command(SSD1306_NORMALDISPLAY)                 # 0xA6


class SSD1306_128_32(SSD1306_base):
    def __init__(self, i2c=None, dev=SSD1306_I2C_ADDRESS, rst=None):
        """Call base class constructor"""
        super().__init__(128, 32, i2c, dev, rst)

    def _initialize(self) -> None:
        """128x32 pixel specific initialization"""
        self._command(SSD1306_DISPLAYOFF)                    # 0xAE
        self._command(SSD1306_SETDISPLAYCLOCKDIV)            # 0xD5
        self._command(self.width)                            # the suggested ratio 0x80
        self._command(SSD1306_SETMULTIPLEX)                  # 0xA8
        self._command(self.height -1)
        self._command(SSD1306_SETDISPLAYOFFSET)              # 0xD3
        self._command(0x0)                                   # no offset
        self._command(SSD1306_SETSTARTLINE | 0x0)            # line #0
        self._command(SSD1306_CHARGEPUMP)                    # 0x8D
        if self._vccstate == SSD1306_EXTERNALVCC:
            self._command(0x10)
        else:
            self._command(0x14)
        self._command(SSD1306_MEMORYMODE)                    # 0x20
        self._command(0x00)                                  # 0x0 act like ks0108
        self._command(SSD1306_SEGREMAP | 0x1)
        self._command(SSD1306_COMSCANDEC)
        self._command(SSD1306_SETCOMPINS)                    # 0xDA
        self._command(0x02)
        self._command(SSD1306_SETCONTRAST)                   # 0x81
        self._command(0x8F)
        self._command(SSD1306_SETPRECHARGE)                  # 0xd9
        if self._vccstate == SSD1306_EXTERNALVCC:
            self._command(0x22)
        else:
            self._command(0xF1)
        self._command(SSD1306_SETVCOMDETECT)                 # 0xDB
        self._command(0x40)
        self._command(SSD1306_DISPLAYALLON_RESUME)           # 0xA4
        self._command(SSD1306_NORMALDISPLAY)                 # 0xA6


class SSD1306_96_16(SSD1306_base):
    def __init__(self, rst=None, i2c=None, dev=SSD1306_I2C_ADDRESS):
        """Call the base class constructor with the proper display parameters (96x16)"""
        super().__init__(96, 16, rst, i2c, dev)

    def _initialize(self) -> None:
        """96x16 pixel specific initialization"""
        self._command(SSD1306_DISPLAYOFF)                    # 0xAE
        self._command(SSD1306_SETDISPLAYCLOCKDIV)            # 0xD5
        self._command(self.width)                            # the suggested ratio 0x60
        self._command(SSD1306_SETMULTIPLEX)                  # 0xA8
        self._command(self.height -1)
        self._command(SSD1306_SETDISPLAYOFFSET)              # 0xD3
        self._command(0x0)                                   # no offset
        self._command(SSD1306_SETSTARTLINE | 0x0)            # line #0
        self._command(SSD1306_CHARGEPUMP)                    # 0x8D
        if self._vccstate == SSD1306_EXTERNALVCC:
            self._command(0x10)
        else:
            self._command(0x14)
        self._command(SSD1306_MEMORYMODE)                    # 0x20
        self._command(0x00)                                  # 0x0 act like ks0108
        self._command(SSD1306_SEGREMAP | 0x1)
        self._command(SSD1306_COMSCANDEC)
        self._command(SSD1306_SETCOMPINS)                    # 0xDA
        self._command(0x02)
        self._command(SSD1306_SETCONTRAST)                   # 0x81
        self._command(0x8F)
        self._command(SSD1306_SETPRECHARGE)                  # 0xd9
        if self._vccstate == SSD1306_EXTERNALVCC:
            self._command(0x22)
        else:
            self._command(0xF1)
        self._command(SSD1306_SETVCOMDETECT)                 # 0xDB
        self._command(0x40)
        self._command(SSD1306_DISPLAYALLON_RESUME)           # 0xA4
        self._command(SSD1306_NORMALDISPLAY)                 # 0xA6
