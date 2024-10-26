#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
the parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 08/Mar/2021
"""

#Basic modules to load
import time
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ArduShield_Uno
from GSOF_ArduBridge.Pin_class import *

from Modules import EPD_base
from GSOF_ArduBridge.device import epd4in2_class
from GSOF_ArduBridge.device import epd2in7_class
from TestScripts.epd_2in7_demo import *
from TestScripts import testScripts

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'auto'        #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    ards = ArduShield_Uno.ArduBridge_Shield(ardu)

    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')

    ardu.gpio.pinMode(13,0) #< SCLK
    ardu.gpio.pinMode(12,0) #< MISO
    ardu.gpio.pinMode(11,0) #< MOSI
    cs   = Pin(ardu.gpio, 10).mode(Pin.OUTPUT).set(1)
    rst  = Pin(ardu.gpio, 8 ).mode(Pin.OUTPUT).set(0).set
    dc   = Pin(ardu.gpio, 9 ).mode(Pin.OUTPUT).set(0).set
    busy = Pin(ardu.gpio, 7 ).mode(Pin.INPUT, invpolarity=False).get
#    MODE0 = 0 #< Clock is normally low,  Data is sampled on the RISING  sclk edge and output on the FALLING sclk edge.
#    MODE1 = 1 #< Clock is normally low,  Data is sampled on the FALLING sclk edge and output on the RISING  sclk edge.
#    MODE2 = 2 #< Clock is normally high, Data is sampled on the FALLING sclk edge and output on the RISING  sclk edge.
#    MODE3 = 3 #< Clock is normally high, Data is sampled on the RISING  sclk edge and output on the FALLING sclk edge.
    ardu.spi.setMode(3, 500000)             #< SPI_MODE3
##
##    # 264x176 display with hardware SPI:
##    disp1 = EPD_base.Waveshare_264_176(rst  = Pin(ardu.gpio, 8 ).mode(Pin.OUTPUT).set(0).set,
##                                       dc   = Pin(ardu.gpio, 9 ).mode(Pin.OUTPUT).set(0).set,
##                                       busy = Pin(ardu.gpio, 7 ).mode(Pin.INPUT).get,
##                                       spi  = ardu.spi
##                                      )
##
##    # 400x300 display with hardware SPI:
##    disp2 = EPD_base.Waveshare_400_300(rst  = Pin(ardu.gpio, 8 ).mode(Pin.OUTPUT).set(0).set,
##                                       dc   = Pin(ardu.gpio, 9 ).mode(Pin.OUTPUT).set(0).set,
##                                       busy = Pin(ardu.gpio, 7 ).mode(Pin.INPUT).get,
##                                       spi  = ardu.spi
##                                       )

    epd27 = epd2in7_class.EPD(rst  = rst,
                              dc   = dc,
                              busy = busy,
                              cs   = cs,
                              out  = ardu.spi.config_write_read_cs,
                              landscape = True,
                             )

    epd42 = epd4in2_class.EPD(rst  = rst,
                              dc   = dc,
                              busy = busy,
                              cs   = cs,
                              out  = ardu.spi.config_write_read_cs,
                              landscape = False,
                             )

##    test = testScripts.test(disp=disp1)
##    test.printHelp()
##    test.config()
print ("epd27.initBwr()")
print ("epd27.clear(bw=0xff, red=0xff) #< White screen")
print ("epd27.clear(bw=0xff, red=0x00) #< Red screen")
print ("epd27.clear(bw=0x00, red=0x00) #< Black screen")
print ("demo(epd27, test=(1,3))")
print ("...")
print ("epd42.initBwr()")
print ("epd42.clear(bw=0xff, red=0xff) #< White screen")
print ("epd42.clear(bw=0xff, red=0x00) #< Red screen")
print ("epd42.clear(bw=0x00, red=0x00) #< Black screen")
print ("demo(epd42, test=(1,3))")
