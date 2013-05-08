## GNU Lesser General Public License
## 
## Program pyNastran - a python interface to NASTRAN files
## Copyright (C) 2011-2012  Steven Doyle, Al Danial
## 
## Authors and copyright holders of pyNastran
## Steven Doyle <mesheb82@gmail.com>
## Al Danial    <al.danial@gmail.com>
## 
## This file is part of pyNastran.
## 
## pyNastran is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## pyNastran is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with pyNastran.  If not, see <http://www.gnu.org/licenses/>.
## 
from numpy import angle

def writeFloats10E(vals):
    vals2 = []
    isAllZeros = True
    for v in vals:
        v2 = '%10.3E' % v
        if v2 == ' 0.000E+00' or v2 == '-0.000E+00':
            v2 = ' 0.0      '
        else:
            isAllZeros = False
        vals2.append(v2)
    return (vals2, isAllZeros)


def writeFloats12E(vals):
    vals2 = []
    isAllZeros = True
    for v in vals:
        v2 = '%12.5E' % v
        if v2 == ' 0.00000E+00' or v2 == '-0.00000E+00':
            v2 = ' 0.0        '
        else:
            isAllZeros = False
        vals2.append(v2)
    return (vals2, isAllZeros)


def writeFloats13E(vals):
    vals2 = []
    isAllZeros = True
    for v in vals:
        v2 = '%13.6E' % v
        if v2 == ' 0.000000E+00' or v2 == '-0.000000E+00':
            v2 = ' 0.0         '
        else:
            isAllZeros = False
        vals2.append(v2)
    return (vals2, isAllZeros)


def writeImagFloats13E(vals, isMagPhase):
    vals2 = []
    isAllZeros = True

    if isMagPhase:
        for v in vals:
            v2 = '%13.6E' % (abs(v))
            if v2 == ' 0.000000E+00' or v2 == '-0.000000E+00':
                v2 = ' 0.0         '
            else:
                isAllZeros = False
            vals2.append(v2)

        for v in vals:
            v3 = '%13.6E' % (angle(v, deg=True))
            if v3 == ' 0.000000E+00' or v3 == '-0.000000E+00':
                v3 = ' 0.0         '
            else:
                isAllZeros = False
            vals2.append(v3)
    else:
        for v in vals:
            v2 = '%13.6E' % (v.real)
            if v2 == ' 0.000000E+00' or v2 == '-0.000000E+00':
                v2 = ' 0.0         '
            else:
                isAllZeros = False
            vals2.append(v2)

        for v in vals:
            v3 = '%13.6E' % (v.imag)
            if v3 == ' 0.000000E+00' or v3 == '-0.000000E+00':
                v3 = ' 0.0         '
            else:
                isAllZeros = False
            vals2.append(v3)
    return (vals2, isAllZeros)


def writeFloats8p4F(vals):
    vals2 = []
    isAllZeros = True
    for v in vals:
        v2 = '%8.4f' % v
        if v2 == '  0.0000' or v2 == ' -0.0000':
            v2 = '  0.0   '
        else:
            isAllZeros = False
        vals2.append(v2)
    return (vals2, isAllZeros)
