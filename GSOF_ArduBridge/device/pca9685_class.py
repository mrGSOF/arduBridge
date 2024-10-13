from __future__ import annotations
import time

"""
This is a Python class for interacting with the PCA9685 PWM controller via I2C.
The PCA9685 is a 16-channel, 12-bit pulse width modulation (PWM) controller that can be used
to control the intensity of LED lighting or the position of servo motors, among other things.

The class has several methods:
__init__(self, i2c, dev=PCA9685_ADDRESS): This is the constructor for the class.
It initializes the class with an I2C object and the device address of the PCA9685 (0x40 by default).
It also initializes the device by setting all outputs to 0 and configuring the device clock.

setFreq(self, freq_hz): This method sets the PWM frequency of the PCA9685.
The frequency must be between 40 and 1600 Hz. The method calculates the prescale value needed to achieve the
desired frequency and sets it in the device's PRESCALE register. It also puts the device into sleep mode, updates
the PRESCALE register, and then restores the device to its previous mode.

setOnOff(self, channel, on, off): This method sets the "on" and "off" times for a single PWM channel.
The "on" time is the delay until the signal transitions from low to high, and the "off" time is the pulse
width (the time the signal stays high). Both times are specified in ticks, with a tick being the time it
takes for the device's internal timer to increment by 1.
The PCA9685 has a 12-bit timer, so there are 4096 ticksin a full timer cycle.

setAllOnOff(self, on, off): This method sets the "on" and "off" times for all PWM channels at once.
It works in the same way as the setOnOff method, but applies the specified times to all channels
"""

### I2C default address:
PCA9685_ADDRESS    = 0x40

### Registers:
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

### MODE1 Bits:
RESTART            = 0x80 #< 
ECTCLK             = 0x40 #< Set to one to select external clock source (upto 50 Mhz)
AI                 = 0x20 #< Automatic address increament
SLEEP              = 0x10
SUB1               = 0x08
SUB2               = 0x04
SUB3               = 0x02
ALLCALL            = 0x01

### MODE1 Bits:
INVRT              = 0x10
OCH                = 0x08 #<Output change on STOP command
OUTDRV             = 0x04 #<The 16 LEDn outputs are configured with a totem pole structure.
OUTNE              = 0x03 #< 0 - When OE = 1 (output drivers not enabled), LEDn = 0.
                          #< 1 - When OE = 1 (output drivers not enabled):
                          #<     LEDn = 1 when OUTDRV = 1
                          #<     LEDn = high-impedance when OUTDRV = 0 (same as OUTNE[1:0] = 10)
                          #< 2,3 When OE = 1 (output drivers not enabled), LEDn = high-impedance

class PCA9685():
    """PCA9685 PWM controller"""
    def __init__(self, i2c, dev=PCA9685_ADDRESS, osci_hz=25000000):
        self.i2c = i2c
        self.dev = dev
        self.osci_hz = osci_hz
        self.maxTicks = 4096 #< 12 bit timer
        self.maxTime  = self.maxTicks/self.osci_hz
        self.prescale = 0 #< PWM frequency is 6103 hz = 25000000hz / 4096

    def sleep(self) -> None:
        """Reset the chip."""
        self.i2c.writeRegister(self.dev, MODE1, [SLEEP])  #< go to sleep

    def wakeup(self):
        mode1 = self.i2c.readRegister(self.dev, MODE1, 1)[0]
        mode1 = mode1 & ~SLEEP  #< wake up (reset sleep)
        self.i2c.writeRegister(self.dev, MODE1, [mode1])
        time.sleep(0.01)  #< wait for oscillator

    def init(self, v=True):
        self.setAllOnOffTicks(0, 0)
        self.i2c.writeRegister(self.dev, MODE2, [OUTDRV])
        self.i2c.writeRegister(self.dev, MODE1, [ALLCALL])
        time.sleep(0.01)  #< wait for oscillator
        self.wakeup()
        self.setPrescale(self.prescale)
        if v==True:
            self.printConfig()
        return self
        
##    def reset(self):
##        """Sends a software reset (SWRST) command to all servo drivers on the bus."""
##        //self.i2c.readRaw(0x06)  #< SWRST
##        vHdr = [self.I2C_PACKET_ID,         #I2C packet-ID
##                self.CMD_I2C_ADDRESS,       #next byte is the I2C device-address
##                dev,                        #DEV#
##                self.CMD_I2C_READ]          #Start the read sequence
##        self.comm.send(vHdr)

    def setPrescale(self, prescale):
        oldmode = self.i2c.readRegister(self.dev, MODE1, 1)[0]
        newmode = (oldmode & 0x7F) | 0x10    #< sleep
        self.i2c.writeRegister(self.dev, MODE1, [newmode])
        self.i2c.writeRegister(self.dev, PRESCALE, [prescale])
        self.i2c.writeRegister(self.dev, MODE1, [oldmode])
        time.sleep(0.01)
        self.i2c.writeRegister(self.dev, MODE1, [oldmode|RESTART])
                
    def getPwmFrequency(self) -> float:
        return self.osci_hz/((self.prescale+1)*self.maxTicks)
    
    def getPulseResolution(self) -> float:
        return (self.prescale +1)/self.osci_hz

    def printConfig(self):
        print( "Prescaler: %d"%(self.prescale) )
        print( "PWM frequency %1.1f Hz"%(self.getPwmFrequency()) )
        print( "Pulse resolution: %1.2f us"%(self.getPulseResolution()*1000000) )
        
    def setPwmFrequency(self, freq_hz, v=True) -> None:
        """Set the PWM tick relolution between 40 to 1600 hertz"""
        #print( "Setting PWM frequency to %1.1f Hz"%(freq_hz) )
        prescaleval = self.osci_hz / (self.maxTicks*freq_hz) -1 #osci_hz / self.maxTicks / freq_hz -1
        self.prescale = int(prescaleval + 0.5)
        self.setPrescale(self.prescale)
        if v==True:
            self.printConfig()

    def setPwmResolution(self, lsb_us=1, v=True):
        """Set the PWM tick relolution between 40 to 1600 hertz"""
        print( "Setting PWM frequency to %1.1f Hz"%(freq_hz) )
        self.prescaleval = (self.dt / lsb_us/1000000) -1
        prescale = int(prescaleval + 0.5)
        self.setPrescale(self.prescale)
        if v==True:
            self.printConfig()

    def setOnOffTicks(self, ch, ticksUntilOn, ticksUntilOff) -> None:
        """
        Sets a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        ticksUntilOn:  The delay until the signal will transition from low to high (in ticks 0..4095)
        ticksUntilOff: The delay until the signal will transition from high to low (in ticks 0..4095)
        """
        if (ch == 255):
            out_on_base  = ALL_OUT_ON_L
            out_off_base = ALL_OUT_OFF_L
        else:
            out_on_base  = OUT0_ON_L  +4*ch
            out_off_base = OUT0_OFF_L +4*ch

        self.i2c.writeRegister(self.dev, out_on_base +0,  [ticksUntilOn&0xff])
        self.i2c.writeRegister(self.dev, out_on_base +1,  [ticksUntilOn>>8])
        self.i2c.writeRegister(self.dev, out_off_base +0, [ticksUntilOff&0xff])
        self.i2c.writeRegister(self.dev, out_off_base +1, [ticksUntilOff>>8])
        return self

    def setAllOnOffTicks(self, ticksUntilOn, ticksUntilOff) -> PCA9685:
        """
        Sets all PWM channels
        offTicks: The delay until the signal will transition from low to high (in ticks 0..4095)
        onTicks: The pulse width (high to low) in ticks (0..4095)
        """
        return self.setOnOffTicks(ch=255, ticksUntilOn=ticksUntilOn, ticksUntilOff=ticksUntilOff)

    def setPulseWidthTicks(self, ch, pw, phase=0) -> None:
        """
        Sets a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        ticksUntilOn:  The delay until the signal will transition from low to high (in ticks 0..4095)
        ticksUntilOff: The delay until the signal will transition from high to low (in ticks 0..4095)
        """
        ticksUntilOn = phase
        ticksUntilOff = ticksUntilOn +pw
        return self.setOnOffTicks(ch=ch, ticksUntilOn=ticksUntilOn, ticksUntilOff=ticksUntilOff)

    def setPulseWidth(self, ch, pw, phase=0.0) -> None:
        """
        Sets a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        ticksUntilOn:  The delay until the signal will transition from low to high (in seconds)
        ticksUntilOff: The delay until the signal will transition from high to low (in seconds)
        """
        ticksUntilOn = int(phase*self.osci_hz +0.5)
        ticksUntilOff = ticksUntilOn +int(pw*self.osci_hz/self.prescale +0.5)
        return self.setOnOffTicks(ch=ch, ticksUntilOn=ticksUntilOn, ticksUntilOff=ticksUntilOff)

    def setPwm(self, pin, perc) -> PCA9685:
        """
        Sets a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        perc: porportional value between 0.0 to 1.0 where 0 is OFF and 1 in ON.
        """
        if perc > 1.0:
            perc = 1.0
        ticks = int((self.maxTicks -1)*perc +0.5)
        self.setPulseWidthTicks(ch=pin, pw=ticks, phase=0)
        return self

    def digitalWrite(self, pin, val) -> int:
        """
        Emulates an Arduino digitalWrite command to set a GPO pin.
        pin: The channel that should be updated with the new values (0..15)
        val: integer value 0 or 1 where 0 is OFF and 1 in ON.
        """
        if val != 0:
            val = 1
        self.setPwm(pin, int(val))
        return 1

    def analogWrite(self, pin, val) -> int:
        """
        Emulates an Arduino analogWrite command to set a single PWM channel.
        channel: The channel that should be updated with the new values (0..15)
        val: integer value between 0 to 255, where 0 is 0% (OFF) and 255 in 100% (ON).
        """
        val = int(val)
        if val < 0:
            val = 0
        elif val > 255:
            val = 255
        self.setPwm(pin, val/255)
        return 1
