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
from GSOF_ArduBridge.device import DS3231_class

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

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

    rtc = DS3231_class.DS3231(ardu.i2c, dev=0x68)
    
    print("rtc.seconds.read().get()")
    print("rtc.minutes.read().get()")
    print("rtc.hours.read().get()")
    print("rtc.day.read().get()")
    print("rtc.getTime()")
    print("rtc.getDate()")
    print("rtc.setTime(hours=9, minutes=30, seconds=31)")
    print("rtc.setDate(year=25, month=2, day=1, weekday=2)")


