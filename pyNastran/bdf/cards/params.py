## GNU General Public License
## 
## Program pyNastran - a python interface to NASTRAN files
## Copyright (C) 2011  Steven P. Doyle
## 
## Author and copyright holder of pyMastran
## Steven Doyle <mesheb82@gmail.com>
## 
## This file is part of pyNastran.
## 
## pyNastran is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## pyNastran is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with pyNastran.  If not, see <http://www.gnu.org/licenses/>.
## 
## This header is automatically generated by applyLicense.py and any
## changes to it will be lost.
## 
# my code
from baseCard import BaseCard

class PARAM(BaseCard):
    def __init__(self,card):
        self.key   = card.field(1)
        self.value = card.field(2)

    def isSameCard(self,param):
        fields1 = [self.key, self.value ]
        fields2 = [param.key,param.value]
        for (field1,field2) in zip(fields1,fields2):
            if not self.isSame(field1,field2):
                return False
            ###
        ###
        return True

    def __repr__(self):
        fields = ['PARAM',self.key,self.value]
        return self.printCard(fields)
