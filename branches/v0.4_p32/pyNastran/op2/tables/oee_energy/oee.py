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
import sys
import copy
from struct import unpack

# pyNastran
from pyNastran.op2.op2Errors import *
from pyNastran.op2.tables.oee_energy.oee_objects import *

class OEE(object):
    """Table of energy"""

    def readTable_OEE(self):
        table3 = self.readTable_OEE_3
        table4Data = self.readOEE_Data
        self.readResultsTable(table3,table4Data)
        self.deleteAttributes_OEE()

    def deleteAttributes_OEE(self): # no thermal
        params = ['lsdvm','mode','eigr','freq','dt','lftsfq','formatCode','numWide']
        self.deleteAttributes(params)
    
    def readTable_OEE_3(self,iTable): # iTable=-3
        bufferWords = self.getMarker()
        if self.makeOp2Debug:
            self.op2Debug.write('bufferWords=%s\n' %(str(bufferWords)))
        #print "2-bufferWords = ",bufferWords,bufferWords*4,'\n'

        data = self.getData(4)
        bufferSize, = unpack('i',data)
        data = self.getData(4*50)
        #print self.printBlock(data)

        aCode = self.getBlockIntEntry(data,1)
        self.eTotal = self.parseApproachCode(data) # total energy of all elements in iSubcase/mode

        elementName, = unpack('8s',data[24:32])
        elementName = elementName.decode().strip() ## element name
        if elementName.isalpha():
            self.dataCode['elementName'] = elementName

        self.addDataParameter(data,'loadSet',   'i',8, False)  ## Load set or zero
        self.addDataParameter(data,'formatCode','i',9, False)  ## format code
        self.addDataParameter(data,'numWide',   'i',10,False)  ## number of words per entry in record; @note is this needed for this table ???
        self.addDataParameter(data,'cvalres',   'i',11,False)  ## C
        self.addDataParameter(data,'setID',     'i',13,False)  ## Set identification number Number
        self.addDataParameter(data,'eigenReal', 'i',14,False)  ## Natural eigenvalue - real part
        self.addDataParameter(data,'eigenImag', 'i',15,False)  ## Natural eigenvalue - imaginary part
        self.addDataParameter(data,'freq',      'f',16,False)  ## Natural frequency
        self.addDataParameter(data,'etotpos',   'f',18)        ## Total positive energy
        self.addDataParameter(data,'etotneg',   'f',19,False)  ## Total negative energy


        #self.printBlock(data) # on
        if self.analysisCode==1:   # statics / displacement / heat flux
            #del self.dataCode['nonlinearFactor']
            self.nonlinearFactor = None
        elif self.analysisCode==2: # real eigenvalues
            self.addDataParameter(data,'mode','i',5)   ## mode number
            #print "mode(5)=%s" %(self.mode)
        elif self.analysisCode==3: # differential stiffness
            pass
        elif self.analysisCode==4: # differential stiffness
            pass
        elif self.analysisCode==5:   # frequency
            self.addDataParameter(data,'freq2','f',5)   ## frequency

        elif self.analysisCode==6: # transient
            self.addDataParameter(data,'time','f',5)   ## time step
            #print "time(5)=%s" %(self.time)
        elif self.analysisCode==7: # pre-buckling
            pass
        elif self.analysisCode==8: # post-buckling
            self.addDataParameter(data,'mode','i',5)   ## mode number
            #print "mode(5)=%s" %(self.mode)
        elif self.analysisCode==9: # complex eigenvalues
            self.addDataParameter(data,'mode','i',5)   ## mode number
            #print "mode(5)=%s" %(self.mode)
        elif self.analysisCode==10: # nonlinear statics
            self.addDataParameter(data,'loadFactor','f',5)   ## load factor
            #print "loadFactor(5) = %s" %(self.loadFactor)
        elif self.analysisCode==11: # old geometric nonlinear statics
            pass
        elif self.analysisCode==12: # contran ? (may appear as aCode=6)  --> straight from DMAP...grrr...
            self.addDataParameter(data,'time','f',5)   ## time step
            #print "time(5)=%s" %(self.time)
        else:
            raise InvalidATFSCodeError('invalid analysis code...analysisCode=%s' %(self.analysisCode))
        ###
        
        #print "*iSubcase=%s elementName=|%s|"%(self.iSubcase,self.elementName)
        #print "analysisCode=%s tableCode=%s" %(self.analysisCode,self.tableCode)
        #if self.numWide==5:
            #print self.codeInformation()
        #print self.codeInformation()
        #self.printBlock(data)
        self.readTitle()

    def readOEE_Data(self):
        #print "self.analysisCode=%s tableCode(1)=%s" %(self.analysisCode,self.tableCode)
        tfsCode = [self.tableCode,self.formatCode,self.sortCode]
        
        if tfsCode==[18,1,0]:
            self.readStrainEnergy_table18_format1_sort0()
        #elif fsCode==[18,1,1]:
        #    self.readOEE_Data_format1_sort1()
        #elif fsCode==[18,2,1]:
        #    self.readOEE_Data_format2_sort1()
        else:
            self.skipOES_Element()
            #raise NotImplementedError('unsupported OEE static solution...aftsCode=%s' %(self.atfsCode))
        ###
        #print str(self.obj)

    def readStrainEnergy_table18_format1_sort0(self):
        """
        assert self.tableCode==18 # Strain Energy
        assert self.formatCode==1 # Real
        assert self.sortCode==0   # Real
        """
        if self.analysisCode==1: # displacement
            #print "isStrainEnergy"
            self.createTransientObject(self.strainEnergy,StrainEnergyObject)
        elif self.analysisCode==2: # buckling modes
            #print "isBucklingStrainEnergy"
            self.createTransientObject(self.strainEnergy,StrainEnergyObject)
        #elif self.analysisCode==5: # freq
            #print "isFreqStrainEnergy"
            #self.createTransientObject(self.strainEnergy,StrainEnergyObject)
        elif self.analysisCode==6: # transient
            #print "isTransientStrainEnergy"
            self.createTransientObject(self.strainEnergy,StrainEnergyObject,debug=False)
        #elif self.analysisCode==9: # nonlinear static eigenvector
            #print "isComplexStrainEnergy"
            #self.createTransientObject(self.strainEnergy,StrainEnergyObject)
        elif self.analysisCode==10: # nonlinear statics
            #print "isNonlinearStrainEnergy"
            self.createTransientObject(self.strainEnergy,StrainEnergyObject)
        else:
            #raise NotImplementedError('bad analysis/table/format/sortCode=%s on OEE table' %(self.atfsCode))
            pass
        ###
        self.readMappedScalarsOut(debug=False) # handles dtMap