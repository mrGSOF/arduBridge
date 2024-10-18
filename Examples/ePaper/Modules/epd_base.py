
from __future__ import division
import time

def delay_ms(ms):
    time.sleep(ms/1000)

class EpdBase():
    """Base class for Waveshare-based ePaper displays.  Implementors should subclass
    and provide an implementation for the _initialize function.
    """

    def __init__(self, width, height, rst, cs, dc, busy, spi):
        self.rst    = rst
        self.cs     = cs
        self.dc     = dc
        self.isBusy = busy
        self.spi    = spi
        self.width  = width
        self.height = height
        self._pages = height//8
        self._buffer = [0]*(width*self._pages)

    # Hardware reset
    def reset(self):
        if self.rst is not None:
            self.rst(1)
            delay_ms(200) 
            self.rst(0)
            delay_ms(5)
            self.rst(1)
            delay_ms(200)   

    def send_command(self, command):
        self.dc(0)
        self.cs(0)
        self.spi.write_read([command])
        self.cs(1)

    def send_data(self, data):
        if type(data) == 'int':
            data = [data]
        self.dc(1)
        for dat in data:
            self.cs(0)
            self.spi.write_read( [dat] )
            self.cs(1)

    def ReadBusy(self):        
        logger.debug("e-Paper busy")
        while(self.busy() == 0):      #  0: idle, 1: busy
            delay_ms(200)                
        logger.debug("e-Paper busy release")

    def initialize(self):
        self.reset()

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

    def display(self, picData_old, picData_new):
        self.PIC_display(self, picData_old, picData_new)

    def clear(self):
        """Clear contents of image buffer."""
        self._buffer = [0]*(self.width*self._pages)

class Waveshare_264_176(EpdBase):
    def __init__(self, rst, cs, dc, busy, spi):
        super().__init__(264, 176, rst, cs, dc, busy, spi)
        #super(Waveshare_264_176, self).__init__(264, 176, rst, cs, dc, busy, spi)

class Waveshare_400_300(EpdBase):
    def __init__(self, rst, cs, dc, busy, spi):
        super().__init__(400, 300, rst, cs, dc, busy, spi)
        #super(Waveshare_264_176, self).__init__(264, 176, rst, cs, dc, busy, spi)
