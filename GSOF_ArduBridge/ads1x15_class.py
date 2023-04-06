"""
    This file is part of GSOF_ArduBridge.

    GSOF_ArduBridge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GSOF_ArduBridge is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GSOF_ArduBridge.  If not, see <https://www.gnu.org/licenses/>.

Class definition for an ADS1x15 analog to digital converter (ADC). The class has a number of methods and
 properties that allow you to configure and use the ADC to convert analog signals to digital form.
 The class is designed as base class to construct specific subclasses.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time

class ADS1x15():
    """Base functionality for ADS1x15 analog to digital converters"""
    DEFAULT_ADDRESS = 0x48
    POINTER_CONVERSION = 0x00
    POINTER_CONFIG = 0x01
    
    CONFIG_OS_SINGLE = 0x8000
    CONFIG_MUX_OFFSET = 12
    CONFIG_COMP_QUE_DISABLE = 0x0003
    CONFIG_GAIN = {
        2 / 3: 0x0000,
        1: 0x0200,
        2: 0x0400,
        4: 0x0600,
        8: 0x0800,
        16: 0x0A00
    }

    MODE_CONTINUOUS = 0x0000
    MODE_SINGLE = 0x0100

    def __init__(self, i2c, dev = None, gain = 1, data_rate = None, mode = None):
        self.i2c = i2c
        self._last_pin_read = None
        self.dev = self.DEFAULT_ADDRESS
        self._gain = gain

        if dev != None:
            self.dev = dev

        self._mode = self.MODE_SINGLE
        if mode != None:
            self._mode = mode

        self._data_rate = self.DEFAULT_DR
        if data_rate != None:
            self._data_rate = data_rate

    def getDataRate(self):
        """The data rate for ADC conversion in samples per second"""
        return self._data_rate

    def setDataRate(self, rate: int):
        """Sets the data rate for ADC conversions. The possible rates are defined by the rates property, which is implemented by subclasses of the ADS1x15 class."""
        possible_rates = self.rates
        if rate not in possible_rates:
            raise ValueError("Data rate must be one of: {}".format(possible_rates))
        self._data_rate = rate

    def getRates(self):
        """Possible data rate settings"""
        raise NotImplementedError("Subclass must implement rates property.")

    def rate_config(self):
        """Rate configuration masks"""
        raise NotImplementedError("Subclass must implement rate_config property.")

    def getGain(self):
        """The ADC gain."""
        return self._gain

    def setGain(self, gain):
        """Sets the gain for the ADC. The possible gain settings are defined by the getGains method."""
        possibleGains = self.getGains()
        if gain not in possibleGains:
            raise ValueError("Gain must be one of: {}".format(possibleGains))
        self._gain = gain

    def getGains(self):
        """Possible gain settings"""
        g = list(self.CONFIG_GAIN.keys())
        return g

    def getMode(self):
        """The ADC conversion mode."""
        return self._mode

    def setMode(self, mode):
        """Sets the mode for the ADC."""
        if mode not in (self.MODE_CONTINUOUS, self.MODE_SINGLE):
            raise ValueError("Unsupported mode")
        self._mode = mode

    def _conversion_value(self, raw_adc):
        """Subclasses should override this function that takes the 16 raw ADC
        values of a conversion result and returns a signed integer value.
        """
        raise NotImplementedError("Subclass must implement _conversion_value function!")

    def _read(self, pin):
        """Perform an ADC read. Returns the signed integer result of the read."""
        # Immediately return conversion register result if in CONTINUOUS mode and pin has not changed
        if (self._mode == self.MODE_SINGLE) or (self._last_pin_read != pin):
            # If SINGLE mode or PIN changed
            self._last_pin_read = pin

            # Configure ADC every time before a conversion in SINGLE mode
            # or changing channels in CONTINUOUS mode
            config = 0
            if self._mode == self.MODE_SINGLE:
                config = self.CONFIG_OS_SINGLE

            config |= (pin & 0x07) << self.CONFIG_MUX_OFFSET
            config |= self.CONFIG_GAIN[self._gain]
            config |= self._mode
            config |= self.CONFIG_DR[self._data_rate]
            config |= self.CONFIG_COMP_QUE_DISABLE
            self._write_register(self.POINTER_CONFIG, config)

            # Wait for conversion to complete
            # ADS1x1x devices settle within a single conversion cycle
            if self._mode == self.MODE_SINGLE:
                # Continuously poll conversion complete status bit
                while not self.isConversionComplete():
                    pass
            else:
                # Can't poll registers in CONTINUOUS mode
                # Wait expected time for two conversions to complete
                time.sleep(2 / self._data_rate)

        return self._conversion_value( self._read_register(self.POINTER_CONVERSION) )

    def readPin(self, pin, differential = False):
        """I2C Interface for ADS1x15-based ADCs reads
        params:
            :param pin: individual or differential pin.
            :param bool is_differential: single-ended or differential read.
        """
        if differential:
            pin = pin
        else:
            pin + 0x04
        return self._read(pin)

    def isConversionComplete(self):
        """Return status of ADC conversion"""
        # OS is bit 15
        # OS = 0: Device is currently performing a conversion
        # OS = 1: Device is not currently performing a conversion
        return self._read_register(self.POINTER_CONFIG) & 0x8000

    def _write_register(self, reg, value):
        """Write 16 bit value to register"""
        buf = [0,0]
        value = int(value)
        reg = int(reg)
        buf[0] = (value >> 8) & 0xff  #< Little Endian
        buf[1] = value & 0xff
        self.i2c.writeRegister(self.dev, reg, buf)

    def _read_register(self, reg):
        """Read 16 bit register value"""
        buf = self.i2c.readRegister(self.dev, reg, 2)
        return (buf[0] << 8) | buf[1] #< Little Endian
