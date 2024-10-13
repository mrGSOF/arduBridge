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

__version__ = "1.0.0"
__author__ = "Guy Soffer"
__copyright__ = "Copyright 2024"
__credits__ = []
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

def solve(p0, p1, acc=200, dt=0.05) -> list:
    """Smooth transition from P0 to P1 with max acceleration"""
    acc = abs(acc)
    DP = abs(p1-p0)

    p = 0
    v = 0
    t = 0
    points = []
    while p < DP:
        if p < (DP/2):
            p += v*dt +0.5*acc*dt**2
            v += acc*dt
        else:
            p += v*dt -0.5*acc*dt**2
            v -= acc*dt
        t += dt
        point = p0 +p
        if p0 > p1:
            point = p0 -p
            
        points.append(point)
    return points
