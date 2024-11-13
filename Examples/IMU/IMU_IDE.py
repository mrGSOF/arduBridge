#!/usr/bin/env python
"""
Script to build an GSOF_ArduBridge environment over the GSOF_ArduBridgeSielf
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 12/Nov/2024
"""

#Basic modules to load
import time, logging
from GSOF_ArduBridge import ArduBridge     #< The GSOF_arduBridge classes
from GSOF_ArduBridge import ArduShield_Uno #< The GSOF_arduBridgeShield library
from GSOF_ArduBridge.device import MPU6050_class
from GSOF_ArduBridge.device import BMP085_class
from GSOF_ArduBridge.device import HMC5883_class
from GSOF_ArduBridge.device import ADXL345_class

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

    ardu.i2c.setFreq(600000)  #< Try to increase to improve speed
        
    imu = MPU6050_class.MPU6050(ardu.i2c, dev=0x69)
    bar = BMP085_class.BMP085(ardu.i2c, dev=0x77)
    mag = HMC5883_class.HMC5883(ardu.i2c, dev=0x1E)
    adxl = ADXL345_class.ADXL345(ardu.i2c, dev=0x77)

    print("----------------")
    print("bar.id.read().get()")
    print("bar.readEECalibrationValues()")
    print("bar.getTemperature_c()")
    print("bar.getPressure_pa()")

    print("----------------")
    print("imu.whoAmI.read().get()")
    print("imu.reset()")
    print("imu.setConfig()")
    print("imu.getAll()")
    print("imu.setFifoEnable(fifoEnable=1, accEn=1, tempEn=0, gyroEn=1)")
    print("sample = imu.getFifo(tmplt='aaaggg')")
    print("sample = imu.setFifoEnable(fifoEnable=1, accEn=1, tempEn=0, gyroEn=1).wait(100).getFifo(tmplt='aaaggg', v=True)")

    print("----------------")
    print("mag.id.read().get()")
    print("mag.setCfg( avgN=4, rate=7.5, meas='normal', maxGauss=4.0, mode='continuous' )")
    print("mag.startHardIronClibration()")
    print("mag.getSingleGauss(N=3, delay=0.05)")
