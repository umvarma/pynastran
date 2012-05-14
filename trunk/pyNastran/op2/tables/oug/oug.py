import sys
import copy
from numpy import array
from struct import unpack

# pyNastran
#from oug_Objects import (
    #fluxObject,                            # analysisCode=1, formatCode=1 sortCode=3
    #nonlinearTemperatureObject,            # analysisCode=10,formatCode=1 sortCode=0 ???
#     )

from oug_displacements import (
     displacementObject,                    # tableCode=1, formatCode=1 sortCode=0
     complexDisplacementObject,             # analysisCode=5  formatCode=3 sortCode=1
     )

from oug_velocities import (                # tableCode=10,formatCode=1 sortCode=0
     velocityObject,
     complexVelocityObject
     )

from oug_accelerations import (             # tableCode=11,formatCode=1 sortCode=0
     accelerationObject,
     complexAccelerationObject
     )

from oug_temperatures import (              # tableCode=1, formatCode=1 sortCode=0
     temperatureObject,
     )

from oug_eigenvectors import (
     eigenVectorObject,                     # analysisCode=2, sortCode=0 formatCode   tableCode=7
     complexEigenVectorObject,              # analysisCode=5, sortCode=1 formatCode=1 tableCode=7
    #realEigenVectorObject,                 # analysisCode=9, sortCode=1 formatCode=1 tableCode=7
     )
from pyNastran.op2.tables.opg_appliedLoads.opg_loadVector import thermalVelocityVectorObject
from pyNastran.op2.op2_helper import polarToRealImag

class OUG(object):
    """Table of displacements/velocities/acceleration/heat flux/temperature"""

    def readTable_OUG(self):
        #self.tableName = 'OUG'
        table3 = self.readTable_OUG_3
        table4Data = self.readOUG_Data
        self.readResultsTable(table3,table4Data)
        self.deleteAttributes_OUG()

    def deleteAttributes_OUG(self):
        params = ['lsdvm','mode','eigr','modeCycle','freq','dt','lftsfq','thermal','randomCode','fCode','numWide','acousticFlag']
        self.deleteAttributes(params)
    
    def readTable_OUG_3(self,iTable): # iTable=-3
        bufferWords = self.getMarker()
        if self.makeOp2Debug:
            self.op2Debug.write('bufferWords=%s\n' %(str(bufferWords)))
        #print "2-bufferWords = ",bufferWords,bufferWords*4,'\n'

        data = self.getData(4)
        bufferSize, = unpack('i',data)
        data = self.getData(4*50)
        #print self.printBlock(data)
        
        (three) = self.parseApproachCode(data)

        self.addDataParameter(data,'randomCode',  'i',8,False)   ## random code
        self.addDataParameter(data,'formatCode',  'i',9,False)   ## format code
        self.addDataParameter(data,'numWide',     'i',10,False)  ## number of words per entry in record; @note is this needed for this table ???
        self.addDataParameter(data,'acousticFlag','f',13,False)  ## acoustic pressure flag
        self.addDataParameter(data,'thermal',     'i',23,False)  ## thermal flag; 1 for heat transfer, 0 otherwise
        
        if not self.isSort1():
            raise NotImplementedError('sort2...')

        ## assuming tCode=1
        if self.analysisCode==1:   # statics / displacement / heat flux
            self.addDataParameter(data,'lsdvmn',  'i',5,False)   ## load set number
            self.applyDataCodeValue('dataNames',['lsdvmn'])
            self.setNullNonlinearFactor()
        elif self.analysisCode==2: # real eigenvalues
            self.addDataParameter(data,'mode',     'i',5)         ## mode number
            self.addDataParameter(data,'eigr',     'f',6,False)   ## real eigenvalue
            self.addDataParameter(data,'modeCycle','i',7,False)   ## mode or cycle @todo confused on the type - F1???
            self.applyDataCodeValue('dataNames',['mode','eigr','modeCycle'])
        #elif self.analysisCode==3: # differential stiffness
            #self.lsdvmn = self.getValues(data,'i',5) ## load set number
            #self.dataCode['lsdvmn'] = self.lsdvmn
        #elif self.analysisCode==4: # differential stiffness
            #self.lsdvmn = self.getValues(data,'i',5) ## load set number
        elif self.analysisCode==5:   # frequency
            self.addDataParameter(data,'freq','f',5)   ## frequency
            self.applyDataCodeValue('dataNames',['freq'])
        elif self.analysisCode==6: # transient
            self.addDataParameter(data,'dt','f',5)   ## time step
            self.applyDataCodeValue('dataNames',['dt'])
        elif self.analysisCode==7: # pre-buckling
            self.addDataParameter(data,'lsdvmn',  'i',5)   ## load set number
            self.applyDataCodeValue('dataNames',['lsdvmn'])
        elif self.analysisCode==8: # post-buckling
            self.addDataParameter(data,'lsdvmn',  'i',5)   ## load set number
            self.addDataParameter(data,'eigr',    'f',6,False)   ## real eigenvalue
            self.applyDataCodeValue('dataNames',['lsdvmn','eigr'])
        elif self.analysisCode==9: # complex eigenvalues
            self.addDataParameter(data,'mode','i',5)   ## mode number
            self.addDataParameter(data,'eigr','f',6,False)   ## real eigenvalue
            self.addDataParameter(data,'eigi','f',7,False)   ## imaginary eigenvalue
            self.applyDataCodeValue('dataNames',['mode','eigr','eigi'])
        elif self.analysisCode==10: # nonlinear statics
            self.addDataParameter(data,'lftsfq','f',5)   ## load step
            self.applyDataCodeValue('dataNames',['lftsfq'])
        elif self.analysisCode==11: # old geometric nonlinear statics
            self.addDataParameter(data,'lsdvmn',  'i',5)   ## load set number
            self.applyDataCodeValue('dataNames',['lsdvmn'])
        elif self.analysisCode==12: # contran ? (may appear as aCode=6)  --> straight from DMAP...grrr...
            self.addDataParameter(data,'lsdvmn',  'i',5)   ## load set number
            self.applyDataCodeValue('dataNames',['lsdvmn'])
        else:
            raise InvalidAnalysisCodeError('invalid analysisCode...analysisCode=%s' %(self.analysisCode))
        # tCode=2
        #if self.analysisCode==2: # sort2
        #    self.lsdvmn = self.getValues(data,'i',5)
        
        #print "*iSubcase=%s"%(self.iSubcase)
        #print "analysisCode=%s tableCode=%s thermal=%s" %(self.analysisCode,self.tableCode,self.thermal)
        #print self.codeInformation()

        #self.printBlock(data)
        self.readTitle()

    def readOUG_Data(self):
        #print "self.analysisCode=%s tableCode(1)=%s thermal(23)=%g" %(self.analysisCode,self.tableCode,self.thermal)
        tfsCode = [self.tableCode,self.formatCode,self.sortCode]
        #print self.dataCode
        #if self.thermal==2:
        #    self.skipOES_Element()
        #print "tfsCode=%s" %(tfsCode)
        
        if self.tableCode==1:    # displacement
            assert self.tableName in ['OUGV1','OUPV1'],'tableName=%s tableCode=%s\n%s' %(self.tableName,self.tableCode,self.codeInformation())
            self.readOUG_Data_table1()
        elif self.tableCode==7:  # modes
            assert self.tableName in ['OUGV1'],'tableName=%s tableCode=%s\n%s' %(self.tableName,self.tableCode,self.codeInformation())
            self.readOUG_Data_table7()
        elif self.tableCode==10: # velocity
            assert self.tableName in ['OUGV1'],'tableName=%s tableCode=%s\n%s' %(self.tableName,self.tableCode,self.codeInformation())
            self.readOUG_Data_table10()
        elif self.tableCode==11: # Acceleration vector
            assert self.tableName in ['OUGV1'],'tableName=%s tableCode=%s\n%s' %(self.tableName,self.tableCode,self.codeInformation())
            self.readOUG_Data_table11()
        else:
            #print "***start skipping***"
            #self.log.debug('skipping approach/table/format/sortCode=%s on %s-OUG table' %(self.atfsCode,self.tableName))
            #self.skipOES_Element()
            #print "***end skipping***"
            print self.codeInformation()
            #raise NotImplementedError(self.codeInformation())
            raise NotImplementedError('bad approach/table/format/sortCode=%s on %s-OUG table' %(self.atfsCode,self.tableName))
        ###
        #print self.obj


    def readThermal4(self): # used on self.thermal in [2,4,8]:
        #print self.codeInformation()
        #print self.printBlock(self.data)
        n=0
        nEntries = len(self.data)//32
        for i in range(nEntries):
            eData = self.data[n:n+32]
            out = unpack('iiffffff',eData)
            #nid = (out[0]-self.deviceCode)//10    ## @todo fix the deviceCode

            #print out
            n+=32
            #print "nid = ",nid
        #sys.exit('thermal4...')
    
    def readOUG_Data_table1(self): # displacement / temperature
        isSort1 = self.isSort1()
        if self.numWide==8:  # real/random
            if self.thermal==0:
                self.createTransientObject(self.displacements,displacementObject) # real
            elif self.thermal==1:
                self.createTransientObject(self.temperatures,temperatureObject)
            #elif self.thermal==8:
                #self.createTransientObject(self.scaledDisplacements,displacementObject)
            else:
                raise NotImplementedError('***thermal=%s***\n%s' %(self.thermal,self.codeInformation()))
            self.OUG_RealTable()
        elif self.numWide==14:  # real/imaginary or mag/phase
            if self.thermal==0:
                self.createTransientObject(self.displacements,complexDisplacementObject) # complex
            else:
                raise NotImplementedError(self.codeInformation())
            self.OUG_ComplexTable()
        else:
            raise NotImplementedError('only numWide=8 or 14 is allowed  numWide=%s' %(self.numWide))
        ###

    def readOUG_Data_table7(self): # eigenvector
        isSort1 = self.isSort1()
        if self.numWide==8:  # real/random
            if self.thermal==0:
                self.createTransientObject(self.eigenvectors,eigenVectorObject) # real
            else:
                raise NotImplementedError(self.codeInformation())
            self.OUG_RealTable()
        elif self.numWide==14:  # real/imaginary or mag/phase
            if self.thermal==0:
                self.createTransientObject(self.eigenvectors,complexEigenVectorObject) # complex
            else:
                raise NotImplementedError(self.codeInformation())
            self.OUG_ComplexTable()
        else:
            raise NotImplementedError('only numWide=8 or 14 is allowed  numWide=%s' %(self.numWide))
        ###

    def readOUG_Data_table10(self): # velocity
        isSort1 = self.isSort1()
        if self.numWide==8:  # real/random
            if self.thermal==0:
                self.createTransientObject(self.velocities,velocityObject) # real
            elif self.thermal==1:
                self.createTransientObject(self.velocities,thermalVelocityVectorObject) # real
            else:
                raise NotImplementedError(self.codeInformation())
            self.OUG_RealTable()
        elif self.numWide==14:  # real/imaginary or mag/phase
            if self.thermal==0:
                self.createTransientObject(self.velocities,complexVelocityObject) # complex
            else:
                raise NotImplementedError(self.codeInformation())
            self.OUG_ComplexTable()
        else:
            raise NotImplementedError('only numWide=8 or 14 is allowed  numWide=%s' %(self.numWide))
        ###

    def readOUG_Data_table11(self): # acceleration
        isSort1 = self.isSort1()
        if self.numWide==8:  # real/random
            if self.thermal==0:
                self.createTransientObject(self.accelerations,accelerationObject) # real
            else:
                raise NotImplementedError(self.codeInformation())
            self.OUG_RealTable()
        elif self.numWide==14:  # real/imaginary or mag/phase
            if self.thermal==0:
                self.createTransientObject(self.accelerations,complexAccelerationObject) # complex
            else:
                raise NotImplementedError(self.codeInformation())
            self.OUG_ComplexTable()
        else:
            raise NotImplementedError('only numWide=8 or 14 is allowed  numWide=%s' %(self.numWide))
        ###

    def getOUG_FormatStart(self):
        """
        Returns an i or an f depending on if it's SORT2 or not.
        Also returns an extraction function that is called on the first argument
        """
        isSort1 = self.isSort1()
        if isSort1:
            #print "SORT1 - %s" %(self.ElementType(self.elementType))
            #print "SORT1"
            format1 = 'i' # SORT1
            extract = self.extractSort1
            #if self.analysisCode in [5]:
                #extract==self.extractSort2
        else: # values from IDENT   #@todo test this...
            #print "SORT2"
            #print "SORT2 - %s" %(self.ElementType(self.elementType))
            if self.analysisCode in [1,2,3,4,7,8,11]:
                format1 = 'i' # SORT1
            elif self.analysisCode in [5,6,9,10,12]:
                format1 = 'f' # SORT1
            else:
                raise InvalidAnalysisCodeError('invalid analysisCode...analysisCode=%s' %(self.analysisCode))
            ###

            extract = self.extractSort2
            #eid = self.nonlinearFactor
        return (format1,extract)

    def OUG_RealTable(self):
        dt = self.nonlinearFactor
        (format1,extract) = self.getOUG_FormatStart()
        format1 += 'iffffff'

        #print "len(data) = ",len(self.data)
        while len(self.data)>=32: # 8*4
            eData     = self.data[0:32]
            self.data = self.data[32: ]
            #print "len(data) = ",len(eData)

            out = unpack(format1, eData)
            (eid,gridType,tx,ty,tz,rx,ry,rz) = out
            eid2  = extract(eid,dt)
            #print "eType=%s" %(eType)
            
            dataIn = [eid2,gridType,tx,ty,tz,rx,ry,rz]
            #print "%s" %(self.ElementType(self.elementType)),dataIn
            #print "%s" %(self.tableName),dataIn
            #eid = self.obj.addNewEid(out)
            self.obj.add(dt,dataIn)
            #print "len(data) = ",len(self.data)
        ###
        self.handleResultsBuffer(self.OUG_RealTable)

    def OUG_ComplexTable(self):
        dt = self.nonlinearFactor

        (format1,extract) = self.getOUG_FormatStart()
        format1 += 'iffffffffffff'
        #print "format1 = ",format1
        isMagnitudePhase = self.isMagnitudePhase()

        while len(self.data)>=56: # 14*4
            eData     = self.data[0:56]
            self.data = self.data[56: ]
            #print "len(data) = ",len(eData)

            out = unpack(format1, eData)
            (eid,gridType,txr,tyr,tzr,rxr,ryr,rzr,
                          txi,tyi,tzi,rxi,ryi,rzi) = out

            if isMagnitudePhase:
                tx = polarToRealImag(txr,txi); rx = polarToRealImag(rxr,rxi)
                ty = polarToRealImag(tyr,tyi); ry = polarToRealImag(ryr,ryi)
                tz = polarToRealImag(tzr,tzi); rz = polarToRealImag(rzr,rzi)
            else:
                tx = complex(txr,txi); rx = complex(rxr,rxi)
                ty = complex(tyr,tyi); ry = complex(ryr,ryi)
                tz = complex(tzr,tzi); rz = complex(rzr,rzi)
                
            eid2  = extract(eid,dt)
            #print "eType=%s" %(eType)
            
            dataIn = [eid2,gridType,tx,ty,tz,rx,ry,rz]
            #print "%s" %(self.ElementType(self.elementType)),dataIn
            #eid = self.obj.addNewEid(out)
            self.obj.add(dt,dataIn)
            #print "len(data) = ",len(self.data)
        ###
        self.handleResultsBuffer(self.OUG_ComplexTable)
