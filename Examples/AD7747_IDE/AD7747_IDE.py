#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 21/Jan/2021
"""

#Basic modules to load
import time
from GSOF_ArduBridge import ArduBridge
import sensor_lib, testScripts

ad7747_ad = 0x48 #< 7bit I2C address
pin_adON = 7 #9

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

### Helper function for encoder read/write
def adON(on):
    ardu.gpio.pinMode(pin_adON, 0)
    ardu.gpio.digitalWrite(pin_adON, on&1)

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'auto'       #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    #sns = sensor_lib.CapSensor(i2c=ardu.i2c, dev=ad7747_ad, units='psi', gain=45*6894.757)
    sns = sensor_lib.CapSensor(i2c=ardu.i2c, dev=ad7747_ad, units='psi',
                               coef = (59425,0),  #< pF to pa
                               #coef = (-9643.463911, 44539.17343621, -0.68119552)
                               offset = 0.0,      #< Capacitance at zero gauge pressure
                               temp = 0.0,        #< and at ambient temperature (C)
                               tcGain=-0.008)     #< degC to pF relation (From excel)
    test = testScripts.test(sns=sns)

    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')
    test.printHelp()
    ardu.i2c.setFreq(100000)
    time.sleep(1)
        
    #sns.configure()
