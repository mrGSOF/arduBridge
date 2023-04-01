
import time

"""
This is a Python class for interacting with the PCA9685 PWM controller via I2C. The PCA9685 is a 16-channel, 12-bit pulse width modulation (PWM) controller that can be used to control the intensity of LED lighting or the position of servo motors, among other things.

The class has several methods:

__init__(self, i2c, dev=PCA9685_ADDRESS): This is the constructor for the class. It initializes the class with an I2C object and the device address of the PCA9685 (which is a constant set to 0x40). It also initializes the device by setting all outputs to 0 and configuring the device to use an external clock and to enable the output driver.

setFreq(self, freq_hz): This method sets the PWM frequency of the PCA9685. The frequency must be between 40 and 1600 Hz. The method calculates the prescale value needed to achieve the desired frequency and sets it in the device's PRESCALE register. It also puts the device into sleep mode, updates the PRESCALE register, and then restores the device to its previous mode.

setOnOff(self, channel, on, off): This method sets the "on" and "off" times for a single PWM channel. The "on" time is the delay until the signal transitions from low to high, and the "off" time is the pulse width (the time the signal stays high). Both times are specified in ticks, with a tick being the time it takes for the device's internal timer to increment by 1. The PCA9685 has a 12-bit timer, so there are 4096 ticks in a full timer cycle.

setAllOnOff(self, on, off): This method sets the "on" and "off" times for all PWM channels at once. It works in the same way as the setOnOff method, but applies the specified times to all channels
"""

### Registers/etc:
PCA9685_ADDRESS    = 0x40

MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
OUT0_ON_L          = 0x06
OUT0_ON_H          = 0x07
OUT0_OFF_L         = 0x08
OUT0_OFF_H         = 0x09
ALL_OUT_ON_L       = 0xFA
ALL_OUT_ON_H       = 0xFB
ALL_OUT_OFF_L      = 0xFC
ALL_OUT_OFF_H      = 0xFD
PRESCALE           = 0xFE
TEST_MODE          = 0xFF

### Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04

class PCA9685():
    """PCA9685 PWM controller"""
    def __init__(self, i2c, dev=PCA9685_ADDRESS):
        self.i2c = i2c
        self.dev = dev
        self.maxTime = 4096 #< 12 bit timer
        self.setAllOnOff(0, 0)
        self.i2c.writeRegister(self.dev, MODE2, [OUTDRV])
        self.i2c.writeRegister(self.dev, MODE1, [ALLCALL])
        time.sleep(0.01)  #< wait for oscillator
        mode1 = self.i2c.readRegister(self.dev, MODE1, 1)[0]
        mode1 = mode1 & ~SLEEP  #< wake up (reset sleep)
        self.i2c.writeRegister(self.dev, MODE1, [mode1])
        time.sleep(0.01)  #< wait for oscillator

    def setFreq(self, freq_hz):
        """Set the PWM frequency to the provided value between 40 to 1600 hertz"""
        prescaleval = 25000000.0    #< 25MHz
        prescaleval /= self.maxTime #< 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        print( "Setting PWM frequency to %1.1f Hz"%(freq_hz) )
        print( "Estimated pre-scale: %1.4f"%(prescaleval) )
        prescale = int(prescaleval + 0.5)
        print( "Final pre-scale: %d"%(prescale) )
        oldmode = self.i2c.readRegister(self.dev, MODE1, 1)[0]
        newmode = (oldmode & 0x7F) | 0x10    #< sleep
        self.i2c.writeRegister(self.dev, MODE1, [newmode])  #< go to sleep
        self.i2c.writeRegister(self.dev, PRESCALE, [prescale])
        self.i2c.writeRegister(self.dev, MODE1, [oldmode])
        time.sleep(0.01)
        self.i2c.writeRegister(self.dev, MODE1, [oldmode|0x80])

    def setOnOff(self, channel, on, off):
        """
        Sets a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        on: The delay until the signal will transition from low to high (in ticks 0..4095)
        off:The pulse width (high to low) in ticks (0..4095)
        """
        self.i2c.writeRegister(self.dev, OUT0_ON_L +4*channel, [on&0xff])
        self.i2c.writeRegister(self.dev, OUT0_ON_H +4*channel, [on>>8])
        self.i2c.writeRegister(self.dev, OUT0_OFF_L +4*channel, [off&0xff])
        self.i2c.writeRegister(self.dev, OUT0_OFF_H +4*channel, [off>>8])

    def setAllOnOff(self, on, off):
        """Sets all PWM channels"""
        self.i2c.writeRegister(self.dev, ALL_OUT_ON_L, [on&0xff])
        self.i2c.writeRegister(self.dev, ALL_OUT_ON_H, [on>>8])
        self.i2c.writeRegister(self.dev, ALL_OUT_OFF_L, [off&0xff])
        self.i2c.writeRegister(self.dev, ALL_OUT_OFF_H, [off>>8])

    def setPwm(self, pin, perc):
        """
        Sets a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        perc: porportional value between 0.0 to 1.0 where 0 is OFF and 1 in ON.
        """
        maxTicks = self.maxTime-1
        ticks = int(maxTicks*perc +0.5)
        if ticks > maxTicks:
            ticks = maxTicks
        self.setOnOff(pin, 0, ticks)

    def digitalWrite(self, pin, val):
        """
        Emulates an Arduino digitalWrite command to set a GPO pin.
        pin: The channel that should be updated with the new values (0..15)
        val: integer value 0 or 1 where 0 is OFF and 1 in ON.
        """
        if val != 0:
            val = 1
        self.setPwm(pin, val)
        return 1

    def analogWrite(self, pin, val):
        """
        Emulates an Arduino analogWrite command to set a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        val: integet value between 0 to 255 where 0 is OFF and 255 in ON.
        """
        if val > 255:
            val = 255
        self.setPwm(pin, val/255)
        return 1
