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
import unittest

from test_helper import runBDF
from pyNastran.bdf.fieldWriter import printCard,printField

class Tester(unittest.TestCase):
    def Atest_ints(self):
        self.assertEquals(printField( 1        ),'       1','a')
        self.assertEquals(printField( 12345678 ),'12345678','b')
        self.assertEquals(printField('12345678'),'12345678','c')
        #self.assertEquals(printField('1       '),'       1','|%s|' %(printField('1       ')))

    def Atest_floats_greater_than_1(self):
        self.assertEquals(printField( 1.2        ),'     1.2','a')
        self.assertEquals(printField( 1.234567890),'1.234568','b')
        self.assertEquals(printField( 12.234568  ),'12.23457','c')
        self.assertEquals(printField( 123.23457  ),'123.2346','d')
        self.assertEquals(printField( 1234.23468 ),'1234.235','e')
        self.assertEquals(printField( 12345.238  ),'12345.24','f')
        self.assertEquals(printField( 123456.28  ),'123456.3','g')
        self.assertEquals(printField( 1234567.25 ),'1234567.',printField( 1234567.25 ))  # 1.2346+6
        self.assertEquals(printField( 12345678. ), '1.2346+7','|%s|'%printField( 12345678. ))
        self.assertEquals(printField( 123456789.), '1.2346+8','|%s|'%printField( 12345678. ))
    def test_floats_small(self):
        #self.assertEquals(printField( 0.1        ),'      .1','A|%s|'%printField( 0.1))
        #self.assertEquals(printField( 0.0001     ),'   .0001','B|%s|'%printField( 0.0001))
        #self.assertEquals(printField( 0.00001    ),'  .00001','C|%s|'%printField( 0.00001))
        self.assertEquals(printField( 0.000001   ),' .000001','D|%s|'%printField( 0.000001))
        #self.assertEquals(printField( 0.0000001  ),'.0000001','E|%s|'%printField( 0.0000001))
        #self.assertEquals(printField( 0.00000012 ),'   1.2-7','F|%s|'%printField( 0.00000012))
        #self.assertEquals(printField( 0.12345678  ),'.1234568','AA|%s|'%printField( 0.12345678))
        #self.assertEquals(printField( 0.00012349  ),'.0001235','BB|%s|'%printField( 0.00012349))
       #self.assertEquals(printField( 0.00012349  ),'1.235+4','CC|%s|'%printField( 0.00012349)) # bad
        #self.assertEquals(printField( 0.00012349  ),'.0001235','DD|%s|'%printField( 0.00012349))
        #self.assertEquals(printField( 0.000012349 ),'1.2349-5','EE|%s|'%printField( 0.000012349))
        

if __name__=='__main__':
    unittest.main()
    #print printField( 1234567. )