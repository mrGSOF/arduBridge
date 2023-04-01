#!/usr/bin/env python
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

Class to calculate moving average and variance.
"""


"""
This code is used to calculate and update the moving average and variance of an input data stream.

The Stat_Recursive_X_Array class maintains a cyclic buffer of fixed size N, where N is the number of input data points used to calculate the moving average and variance. The update() method is used to add a new data point to the cyclic buffer, replacing the oldest data point, and returning the value of the oldest data point that was removed. The Ex() method returns the current moving average, while the Var() method returns the current variance. The Ex2() method returns the current average of the squares of the data points.

The Cyclic_Array class is used to maintain the cyclic buffer of data points. It has an update() method that is used to add a new data point to the buffer, replacing the oldest data point, and returning the value of the oldest data point that was removed.

The E() function calculates the average of a list of data points. If a second list is provided, it calculates the dot product of the two lists and returns the average of the result.
"""
__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

def E(X, Y=None):
    S = 0
    if Y==None:
        S = sum(X)
    else:
        for Xi,Yi in zip(X,Y):
            S += Xi*Yi
    return S/len(X)

class Cyclic_Array():
    def __init__(self, N=1, InitVal=0, InitVec=None):
        if InitVec == None:
            self.V = [InitVal]*N
        else:
            self.V = InitVec
        self.idx = 0
        self.isFilled = False
        self.N = len(self.V)

    def update(self, new_val) -> float:
        """ Add a new value to the buffer and drop (also return) the oldest one """
        old_val = self.V[self.idx]
        self.V[self.idx] = new_val
        self.idx += 1
        if self.idx >= self.N:
            self.idx = 0
            self.isFilled = True
        return float(old_val)
 
class Stat_Recursive_X_Array():
    def __init__(self, X=[0]):
        self.ensemble = Cyclic_Array( InitVec=X)

        #Summing the entire array for the first and only time
        self.Sx = 0
        self.Sx2 = 0
        for Xi in X:
            self.Sx += Xi
            self.Sx2 += Xi*Xi

        #Calculating the finale result
        N = self.ensemble.N
        self.E_x = self.Sx/N
        self.E_x2 = self.Sx2/N

    def update(self, Xi) -> float:
        """ Update the moving ensemble. Return the oldest value that was droped """
        Xo = self.ensemble.update(Xi) #< Update the cyclinc buffer with the new value

        ### Update the new sum
        self.Sx -= Xo
        self.Sx += Xi

        N = self.ensemble.N
        if self.ensemble.isFilled:
            self.E_x = self.Sx/N
        else:
            self.E_x = Xi

        #Update the statistical values of the ensemble
        self.Sx2 -= Xo*Xo
        self.Sx2 += Xi*Xi
        self.E_x2 = self.Sx2/N

        N2 = N*N
        self.Var = (1.0/(N*N-N)) * (N*self.Sx2 -self.Sx**2)
        return float(Xo)

    def Ex(self):
        return self.E_x

    def Ex2(self):
        return self.E_x2

    def Var(self):
        return self.Var
