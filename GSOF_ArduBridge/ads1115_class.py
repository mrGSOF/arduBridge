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

This code defines a class called ADS1115 that is a subclass of ads1x15_class.ADS1x15.
It is used to interface with an ADS1115 analog-to-digital converter (ADC) over an I2C interface.
The class has several attributes to define the: possible data rates, the gain settings,
and the resolution of the ADC. It also has several constants for the ADC's input pins.

The _conversion_value method converts a binary ADC value to a voltage using the ADC's gain setting and resolution.
It also handles negative values by appling the two's complement method.
The getRatesList method returns a list of the possible data rates for the ADC, sorted in ascending order.
The getRates method returns a dictionary of the data rate configuration masks.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

from GSOF_ArduBridge import ads1x15_class

class ADS1115(ads1x15_class.ADS1x15):
    """Class for the ADS1115 16 bit ADC"""
    # Data sample rates
    DEFAULT_DR = 128
    CONFIG_DR = {
        8: 0x0000,
        16: 0x0020,
        32: 0x0040,
        64: 0x0060,
        128: 0x0080, #< Default Data Rate (DR)
        250: 0x00A0,
        475: 0x00C0,
        860: 0x00E0,
    }

    GAIN_TO_VREF = {
        2 / 3: 6.144,
        1: 4.096,
        2: 2.048,
        4: 1.024,
        8: 0.512,
        16: 0.256
    }
    
    # Pins
    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3

    RES = 2**16

#    def __init__(self, i2c, dev = None, gain = 1, data_rate = None, mode = None, Vref = 5.0):
#        ads1x15_class.ADS1x15.__init__(self, i2c, dev, gain, data_rate, mode)
#        self.Vref = Vref
        
    def getRatesList(self):
        """Returns a list of the possible data rates for the ADC"""
        r = list(self.CONFIG_DR.keys())
        return r.sort()

    def getRates(self):
        """Returns a dictionary of the data rate configuration masks"""
        return self.CONFIG_DR

    def _conversion_value(self, raw_adc):
        """Returns the ADC input voltage and binary ADC values (volt, bin)"""
        #volt = self.GAIN_TO_VREF[self._gain]*raw_adc/(self.RES/2)
        if raw_adc&0x8000:
            raw_adc = -1*((raw_adc^0xffff) +1)
        volt = 4*self.GAIN_TO_VREF[1]*raw_adc/(self.RES)
        return (volt, raw_adc)
