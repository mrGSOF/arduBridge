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
This class Stat_Recursive_X_Array is used to calculate statistical quantities such as mean and variance of a given set of data points. The class has an attribute CycAry which is an instance of the Cyclic_Array class. The Cyclic_Array class is used to implement a cyclic array data structure that stores a fixed number of elements, and when a new element is added and the array is full, the oldest element is removed to make space for the new element.

The Stat_Recursive_X_Array class has the following methods:

__init__(self, X=[0]): This is the constructor method which is used to initialize the object. It takes in a list X of data points and stores it in the CycAry attribute. It also calculates the sum of the elements in X, sum of squares of the elements in X, mean of the elements in X and variance of the elements in X.
step(self, Xi): This method is used to add a new element Xi to the cyclic array and update the statistical quantities. It returns the oldest element removed from the cyclic array to make space for the new element.
Ex(self): This method returns the mean of the elements in the cyclic array.
Ex2(self): This method returns the sum of squares of the elements in the cyclic array.
Var(self): This method returns the variance of the elements in the cyclic array.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import copy, math

class Cyclic_Array():
    def __init__(self, N=1, InitVal=0, InitVec=None):
        if InitVec == None:
            self.V = [InitVal]*N
        else:
            self.V = InitVec
        self.idx = 0
        self.isFilled = False
        self.N = len(self.V)

    def step(self, new_val):
        old_val = self.V[self.idx]
        self.V[self.idx] = new_val
        self.idx += 1
        if self.idx >= self.N:
            self.idx = 0
            self.isFilled = True
        return old_val

def E(X, Y=None):
    S = 0
    if Y==None:
        S = sum(X)
    else:
        for Xi,Yi in zip(X,Y):
            S += Xi*Yi
    return S/len(X)
 
class Stat_Recursive_X_Array():
    def __init__(self, X=[0]):
        self.CycAry = Cyclic_Array( InitVec=X)
        self.lastValue = X

        #Summing the entire array for the first and only time
        self.Sx = 0
        self.Sx2 = 0
        for i,Xi in enumerate(X):
            self.Sx += Xi
            self.Sx2 += Xi*Xi

        #Calculating the finale result
        N = self.CycAry.N
        self.E_x = self.Sx/N
        self.E_x2 = self.Sx2/N

    def step(self, Xi):
        #Cycling the array with a new value
        self.lastValue = Xi
        Xo = self.CycAry.step(Xi)
        N = self.CycAry.N

        #Updating the new sum of the array
        self.Sx -= Xo
        self.Sx += Xi

        if self.CycAry.isFilled:
            self.E_x = self.Sx/N
        else:
            self.E_x = self.lastValue
                
        #Updating the new sum of the array
        self.Sx2 -= Xo*Xo
        self.Sx2 += Xi*Xi
        self.E_x2 = self.Sx2/N

        N2 = N*N
        self.Var = (1.0/(N*N-N)) * (N*self.Sx2 -self.Sx**2)
        return Xo

    def Ex(self):
        return self.E_x

    def Ex2(self):
        return self.E_x2

    def Var(self):
        return self.Var
