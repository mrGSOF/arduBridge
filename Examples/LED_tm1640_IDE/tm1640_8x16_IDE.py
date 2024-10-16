#!/usr/bin/env python
"""
Script to build an GSOF_ArduBridge environment over the GSOF_ArduBridgeSielf
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 15/Oct/2024
"""

#Basic modules to load
import time, logging
from GSOF_ArduBridge import ArduBridge     #< The GSOF_arduBridge classes
from GSOF_ArduBridge import ArduShield_Uno #< The GSOF_arduBridgeShield library
from GSOF_ArduBridge.device import tm1640_class
from GSOF_ArduBridge.Pin_class import *
import tm1640_test

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def test(f0=100, f1=10000, N=100):
    for f in range(f0, f1, N):
        dds.setFreq(f)
        time.sleep(0.05)

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'auto'        #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate, logLevel=logging.INFO ) #< The GSOF_arduBridge core object
    ards = ArduShield_Uno.ArduBridge_Shield(ardu)                                   #< The GSOF_arduBridge HW shield object
    
    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')

    sdoPin  = Pin(ardu.gpio, 2).mode(Pin.OUTPUT).set(0)
    sclkPin = Pin(ardu.gpio, 3).mode(Pin.OUTPUT).set(0)
    
    tm = tm1640_class.TM1640(sdo=sdoPin, sclk=sclkPin, cols=16)

    print("WeMos D1 Mini -- LED Matrix")
    print("GPIO%d ---------- CLK"%sclkPin.pin)
    print("GPIO%d ---------- DIO"%sdoPin.pin)
    print("3V3 ------------ VCC")
    print("G -------------- GND")

    print("tm.allOn()")
    print("tm.allOff()")
    print("tm.brightness(3) #< 0 to 7")
    print("tm1640_test.test(tm)")
