#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 21/Oct/2024
"""

#Basic modules to load
import time
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge.Pin_class import *
from GSOF_ArduBridge.device import TMC5130_class
#from TestScripts import testScripts

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'auto'       #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    stepSizeDeg = 3.46   #<--LIM106 Stepper step size in degrees
#    stepSizeDeg = 1.8   #<--MOONS Stepper step size in degrees
#    stepSizeDeg = 0.9   #<-- Z417 Stepper step size in degrees
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\

    print('Discovering ArduBridge on port %s'%(port))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')

    gpio = ardu.gpio
    sclk = Pin(gpio, 13).mode(gpio.OUTPUT)        #< SCLK
    miso = Pin(gpio, 12).mode(gpio.INPUT)         #< MISO
    mosi = Pin(gpio, 11).mode(gpio.OUTPUT)        #< MOSI
    cs   = Pin(gpio, 10).mode(gpio.OUTPUT).set(1) #< CS
##    MODE0 = 0 #< Clock is normally low,  Data is sampled on the RISING  sclk edge and output on the FALLING sclk edge.
##    MODE1 = 1 #< Clock is normally low,  Data is sampled on the FALLING sclk edge and output on the RISING  sclk edge.
##    MODE2 = 2 #< Clock is normally high, Data is sampled on the FALLING sclk edge and output on the RISING  sclk edge.
##    MODE3 = 3 #< Clock is normally high, Data is sampled on the RISING  sclk edge and output on the FALLING sclk edge.
    ardu.spi.setMode(3, 1000000) #< Data is sampled on the transition from low to high (trailing edge) (CPHA = 1)
    
    stp = TMC5130_class.TMC5130(cs  = cs,
                                out = ardu.spi.config_write_read_cs,
                                stepSizeDeg = stepSizeDeg)

print("stp.configure()")
print("stp.setPosition(pos=200000, units='bin', v=True)")
print("stp.setPosition(pos=720, units='deg', v=True)")
print("stp.getPosition(units='deg')")
