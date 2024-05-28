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

Function to manage debug print outs to file and console.
"""

"""
define a simple function printf for debugging purposes. The printf function takes five arguments:

text: a string containing text to print. This string can include format specifiers which are replaced by par.
par: a tuple containing values to use in place of the format specifiers in text.
data: a string that is appended to the end of the output.
v: a boolean value indicating whether the output should be printed to the console.
_file: a file object to which the output should be written. If this argument is False, the output is not written to a file.
The printf function first constructs the string to be printed by replacing the format specifiers in text with the values
in par and appending data to the end. It then prints the resulting string to the console if v is True and writes the string
to a file if _file is a file object that is not closed.
"""

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

def printf(text, par=(), data='', v=True, _file=False):
    PrintLine = text % par
    PrintLine += str(data) +' '
    
    if PrintLine[-1]=='\n':
        PrintLine = PrintLine[:-1]
    if v:
        print(PrintLine)
    if (_file):
        if (_file.closed == False):
            _file.write(PrintLine+'\n')
