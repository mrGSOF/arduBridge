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
from GSOF_ArduBridge.device import ad9833_class

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def ddsTest(f0=100, f1=10000, N=100):
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

    ardu.gpio.setMode(2, ardu.gpio.OUTPUT)
    ardu.gpio.setMode(3, ardu.gpio.OUTPUT)
    ardu.gpio.setMode(4, ardu.gpio.OUTPUT)
    
    dds = ad9833_class.AD9833(gpio=ardu.gpio, sdata=2, sclk=3, fsync=4)

    print("dds.setFreq(hz)")
    print("ddsTest(f0, f1, N=20)")
