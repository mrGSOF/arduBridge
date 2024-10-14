# -*- coding: utf-8 -*-
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
"""

import time

class BlinkM():
    """Light controller class, sends messages to the blinkM.
    """
    def __init__(self, i2c, dev=0x09):
        """ """
        self.i2c = i2c
        self.dev = dev

    def write(self, buf):
        """Write command to blinkM"""
        self.i2c.writeRaw(self.dev, buf)

    def wait(self, t):
        time.sleep(t)
        return self
    
    def read(self, cmd, N):
        """Read command result from blinkM"""
        res = self.i2c.readRegister(self.dev, cmd, N)
        return res

    def getVersion(self):
        """Get blinkM firmware version"""
        ver = self.read(ord('Z'), 2)
        ver = ver[0]*256 +ver[1]
        print("0x%04x"%ver)
        return ver

    def setDevAddress(self, dev):
        """Set device address"""
        self.write( [ord('A'),dev,0xd0,0x0d,dev] )
        return self

    def getDevAddress(self) -> int:
        """Get device address"""
        return self.read( ord('a'), 1 )[0]

    def setRgb(self, red, green, blue):
        """Command blinkM to RGB color"""
        self.write( [ord('n'), int(red)&0xff, int(green)&0xff, int(blue)&0xff] )
        return self

    def getRgb(self):
        """Get blinkM) current RGB values"""
        return self.read(ord('g'), 3)

    def setFadeRate(self, rate):
        """Command blinkM fade rate 1 to 255)"""
        if rate < 1:
            rate = 1
        elif rate > 255:
            rate = 255
        self.write( [ord('f'), int(rate)] )
        return self

    def fadeToRgb(self, red, green, blue, rate=255):
        """Command blinkM to fade to RGB color"""
        self.setFadeRate(rate)
        self.write( [ord('c'), int(red)&0xff, int(green)&0xff, int(blue)&0xff] )
        return self

    def off(self):
        """ Switch the blink(1) off instantly"""
        self.setRgb(0,0,0)
        return self

    def play(self, script=1, startLine=0, repeats=0):
        """ Play internal color pattern
        :param script: script number
        :param startLine: pattern line to start from
        :param repeats: number of times to play, 0=play forever
        """
        self.write( [ord('p'), int(script)&0xff, int(repeats)&0xff, int(startLine)&0xff] )
        return self

    def stop(self):
        """ Stop internal color pattern playing"""
        self.write( [ord('o')] )
        return self

##    def save_pattern(self):
##        """ Save internal RAM pattern to flash
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        buf = [REPORT_ID, ord('W'), 0xBE, 0xEF, 0xCA, 0xFE, 0, 0, 0]
##        self.write(buf)
##
##    def set_ledn(self, ledn=0):
##        """ Set the 'current LED' value for writePatternLine
##        :param ledn: LED to adjust, 0=all, 1=LEDA, 2=LEDB
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        buf = [REPORT_ID, ord('l'), ledn, 0, 0, 0, 0, 0, 0]
##        self.write(buf)
##
##    def write_pattern_line(self, step_milliseconds, color, pos, ledn=0):
##        """ Write a color & step time color pattern line to RAM
##        :param step_milliseconds: how long for this pattern line to take
##        :param color: LED color
##        :param pos: color pattern line number (0-15)
##        :param ledn: LED number to adjust, 0=all, 1=LEDA, 2=LEDB
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        self.set_ledn(ledn)
##        red, green, blue = self.color_to_rgb(color)
##        r, g, b = (red, green, blue)
##        step_time = int(step_milliseconds / 10)
##        th = (step_time & 0xff00) >> 8
##        tl = step_time & 0x00ff
##        buf = [REPORT_ID, ord('P'), int(r), int(g), int(b), th, tl, pos, 0]
##        self.write(buf)
##
##    def read_pattern_line(self, pos):
##        """ Read a color pattern line at position
##        :param pos: pattern line to read
##        :return pattern line data as tuple (r,g,b, step_millis) or False on err
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        buf = [REPORT_ID, ord('R'), 0, 0, 0, 0, 0, int(pos), 0]
##        self.write(buf)
##        buf = self.read()
##
##        r, g, b = buf[2:4]
##
##        step_millis = ((buf[5] << 8) | buf[6]) * 10
##        return r, g, b, step_millis
##
##    def read_pattern(self):
##        """ Read the entire color pattern
##        :return List of pattern line tuples
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        pattern = []
##        for i in range(0, 16):  # FIXME: adjustable for diff blink(1) models
##            pattern.append(self.read_pattern_line(i))
##        return pattern
##
##    def clear_pattern(self):
##        """ Clear entire color pattern in blink(1)
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        for i in range(0, 16):  # FIXME: pattern length
##            self.write_pattern_line(0, 'black', i)
##
##    def play_pattern(self, pattern_str, onDevice=True):
##        """ Play a Blink1Control-style pattern string
##        :param pattern_str: The Blink1Control-style pattern string to play
##        :param onDevice: True (default) to run pattern on blink(1),
##                         otherwise plays in Python process
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        if not onDevice:
##            return self.play_pattern_local(pattern_str)
##
##        # else, play it in the blink(1)
##        num_repeats, colorlist = self.parse_pattern(pattern_str)
##
##        empty_color = {
##            'rgb': '#000000',
##            'time': 0.0,
##            'ledn': 0,
##            'millis': 0
##        }
##
##        colorlist += [empty_color] * (32 - len(colorlist))
##
##        for i, c in enumerate(colorlist):
##            self.write_pattern_line(c['millis'], c['rgb'], i, c['ledn'])
##
##        return self.play(count=num_repeats)
##
##    def play_pattern_local(self, pattern_str):
##        """ Play a Blink1Control pattern string in Python process
##            (plays in blink1-python, so blocks)
##        :param pattern_str: The Blink1Control-style pattern string to play
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        num_repeats, colorlist = self.parse_pattern(pattern_str)
##        if num_repeats == 0:
##            num_repeats = -1
##
##        while num_repeats:
##            num_repeats -= 1
##
##            for c in colorlist:
##                self.fade_to_color(c['millis'], c['rgb'], c['ledn'])
##                time.sleep(c['time'])
##
##    @staticmethod
##    def parse_pattern(pattern_str):
##        """ Parse a Blink1Control pattern string to a list of pattern lines
##            e.g. of the form '10,#ff00ff,0.1,0,#00ff00,0.1,0'
##        :param pattern_str: The Blink1Control-style pattern string to parse
##        :returns: an list of dicts of the parsed out pieces
##        """
##        pattparts = pattern_str.replace(' ', '').split(',')
##        num_repeats = int(pattparts[0])  # FIXME
##        pattparts = pattparts[1:]
##
##        colorlist = []
##        dpattparts = dict(enumerate(pattparts))  # lets us use .get(i,'default')
##        for i in range(0, len(pattparts), 3):
##            rgb = dpattparts.get(i + 0, '#000000')
##            time_ = float(dpattparts.get(i + 1, 0.0))
##            ledn = int(dpattparts.get(i + 2, 0))
##            # set default if empty string
##            rgb = rgb if rgb else '#000000'  # sigh
##            time_ = time_ if time_ else 0.0  # sigh
##            ledn = ledn if ledn else 0  # sigh
##            millis = int(time_ * 1000)
##            color = {
##                'rgb': rgb,
##                'time': time_,
##                'ledn': ledn,
##                'millis': millis
##            }
##
##            colorlist.append(color)
##
##        return num_repeats, colorlist
##
##    def server_tickle(
##        self,
##        enable,
##        timeout_millis=0,
##        stay_lit=False,
##        start_pos=0,
##        end_pos=16
##    ):
##        """Enable/disable servertickle / serverdown watchdog
##        :param: enable: Set True to enable serverTickle
##        :param: timeout_millis: millisecs until servertickle is triggered
##        :param: stay_lit: Set True to keep current color of blink(1), False to turn off
##        :param: start_pos: Sub-pattern start position in whole color pattern
##        :param: end_pos: Sub-pattern end position in whole color pattern
##        :raises: Blink1ConnectionFailed: if blink(1) is disconnected
##        """
##        if self.dev is None:
##            return ''
##
##        en = int(enable is True)
##        timeout_time = int(timeout_millis / 10)
##        th = (timeout_time & 0xff00) >> 8
##        tl = timeout_time & 0x00ff
##        st = int(stay_lit is True)
##        buf = [REPORT_ID, ord('D'), en, th, tl, st, start_pos, end_pos, 0]
##        self.write(buf)
