#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 21/Dec/2021
"""

#Basic modules to load
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ArduBridge_HW

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = "COM6"          #< Change to the correct COM to access the Arduino
    #port = "/dev/ttyUSB0" #< Under Linux
    baudRate = 115200*2    #< Leave as is (230400 bits per second)
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    ards = ArduBridge.ArduBridge( ardu, an_ref=3.3 )

    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')

    #\/\/\/ REST OF YOUR CODE GOES HERE \/\/\/

    #/\/\/\        CODE BLOCK END       /\/\/\


