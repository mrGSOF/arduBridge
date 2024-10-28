#!/usr/bin/env python
"""
Script to build an GSOF_ArduBridge environment over the GSOF_ArduBridgeSielf
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 08/Mar/2021
"""

#Basic modules to load
import time, logging
from GSOF_ArduBridge import ArduBridge     #< The GSOF_arduBridge classes
from GSOF_ArduBridge import ArduShield_Uno #< The GSOF_arduBridgeShield library
from GSOF_ArduBridge.device import pcf8591_class

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

def dacTest(N=10):
    for n in range(0,N):
        for i in range(0,255,5):
            adc.analogWrite(i)
            time.sleep(0.01)

def adcTest(ch=0, N=10):
    for n in range(0,N):
        print("%d"%(adc.analogRead(ch)))
        time.sleep(0.2)

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
        
    adc = pcf8591_class.PCF8591(i2c=ardu.i2c, dev=0x48)

    print("adc.analogRead(ch)")
    print("adc.digitalRead(ch, thrs=0x50)")
    print("adc.analogWrite(val)")
    print("adc.digitalWrite(val, high=0x80)")
    print("dacTest(N=10)")
    print("adcTest(ch=0, N=20)")
