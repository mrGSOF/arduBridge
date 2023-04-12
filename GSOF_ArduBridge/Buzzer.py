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

Class to build a simple sound playback.
The play function should be called with optional repeat value.
The default repeat value is 1.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import winsound

class Buzzer():
    def __init__(self, fileName, repeat=1):
        self.fileName = fileName
        self.repeat = repeat

    def play(self, repeat=False):
        if repeat == False:
            repeat = self.repeat

        while repeat > 0:
            repeat -= 1
            winsound.PlaySound(self.fileName, winsound.SND_FILENAME)
            
