from __future__ import division
import sys
from struct import unpack

from oef_complexForceObjects import *

class ComplexForces(object):

    def OEF_Rod_alt(self): # 1-CROD, 3-CTUBE, 10-CONROD
        deviceCode = self.deviceCode
        
        dt = self.nonlinearFactor
        isSort1 = self.isSort1()
        if isSort1:
            #print "SORT1 - %s" %(self.ElementType(self.elementType))
            format1 = 'iffff' # SORT1
            extract = self.extractSort1
            #dt = self.nonlinearFactor
        else:
            #print "SORT2 - %s" %(self.ElementType(self.elementType))
            format1 = 'fffff' # SORT2
            extract = self.extractSort2
            #eid = self.nonlinearFactor

        self.createThermalTransientObject(self.rodForces,ComplexRodForce,isSort1)

        while len(self.data)>=20: # 5*4
            eData     = self.data[0:20]
            self.data = self.data[20: ]
            #print "len(data) = ",len(eData)

            out = unpack(format1, eData)
            (eid,axialReal,torqueReal,axialImag,torqueImag) = out
            eid2  = extract(eid,dt)
            #print "eType=%s" %(eType)
            
            dataIn = [eid2,axialReal,torqueReal,axialImag,torqueImag]
            print "%s" %(self.ElementType(self.elementType)),dataIn
            #eid = self.obj.addNewEid(out)
            self.obj.add(dt,dataIn)
            #print "len(data) = ",len(self.data)
        ###
        self.handleResultsBuffer(self.OEF_Rod_alt)
        #print self.rodForces
        
    def OEF_Spring_alt(self): # 11-CELAS1, 12-CELAS2, 13-CELAS3, 14-CELAS4
        deviceCode = self.deviceCode
        
        dt = self.nonlinearFactor
        isSort1 = self.isSort1()
        if isSort1:
            #print "SORT1 - %s" %(self.ElementType(self.elementType))
            format1 = 'iff' # SORT1
            extract = self.extractSort1
            #dt = self.nonlinearFactor
        else:
            #print "SORT2 - %s" %(self.ElementType(self.elementType))
            format1 = 'fff' # SORT2
            extract = self.extractSort2
            #eid = self.nonlinearFactor

        self.createThermalTransientObject(self.springForces,ComplexSpringForce,isSort1)

        while len(self.data)>=12: # 3*4
            eData     = self.data[0:12]
            self.data = self.data[12: ]
            #print "len(data) = ",len(eData)

            out = unpack(format1, eData)
            (eid,forceReal,forceImag) = out
            eid2  = extract(eid,dt)
            #print "eType=%s" %(eType)
            
            dataIn = [eid2,forceReal,forceImag]
            print "%s" %(self.ElementType(self.elementType)),dataIn
            #eid = self.obj.addNewEid(out)
            self.obj.add(dt,dataIn)
            #print "len(data) = ",len(self.data)
        ###
        self.handleResultsBuffer(self.OEF_Spring_alt)
        #print self.springForces
        
    def OEF_CBar_alt(self): # 34-CBAR
        deviceCode = self.deviceCode
        
        dt = self.nonlinearFactor
        isSort1 = self.isSort1()
        if isSort1:
            #print "SORT1 - %s" %(self.ElementType(self.elementType))
            format1 = 'iffffffffffffffff' # SORT1
            extract = self.extractSort1
            #dt = self.nonlinearFactor
        else:
            #print "SORT2 - %s" %(self.ElementType(self.elementType))
            format1 = 'fffffffffffffffff' # SORT2
            extract = self.extractSort2
            #eid = self.nonlinearFactor

        self.createThermalTransientObject(self.barForces,ComplexCBARForce,isSort1)

        while len(self.data)>=68: # 17*4
            eData     = self.data[0:68]
            self.data = self.data[68: ]
            #print "len(data) = ",len(eData)

            out = unpack(format1, eData)
            (eid,bm1ar,bm2ar,bm1br,bm2br,ts1r,ts2r,afr,trqr,
                 bm1ai,bm2ai,bm1bi,bm2bi,ts1i,ts2i,afi,trqi) = out
            eid2  = extract(eid,dt)
            #print "eType=%s" %(eType)
            
            dataIn = [eid2,bm1ar,bm2ar,bm1br,bm2br,ts1r,ts2r,afr,trqr,
                           bm1ai,bm2ai,bm1bi,bm2bi,ts1i,ts2i,afi,trqi]
            print "%s" %(self.ElementType(self.elementType)),dataIn
            #eid = self.obj.addNewEid(out)
            self.obj.add(dt,dataIn)
            #print "len(data) = ",len(self.data)
        ###
        self.handleResultsBuffer(self.OEF_CBar_alt)
        #print self.barForces
        
    def OEF_Plate_alt(self): # 33-CQUAD4,74-CTRIA3
        deviceCode = self.deviceCode
        
        dt = self.nonlinearFactor
        isSort1 = self.isSort1()
        if isSort1:
            #print "SORT1 - %s" %(self.ElementType(self.elementType))
            format1 = 'iffffffffffffffff' # SORT1
            extract = self.extractSort1
            #dt = self.nonlinearFactor
        else:
            #print "SORT2 - %s" %(self.ElementType(self.elementType))
            format1 = 'fffffffffffffffff' # SORT2
            extract = self.extractSort2
            #eid = self.nonlinearFactor

        self.createThermalTransientObject(self.plateForces,ComplexPlateForce,isSort1)

        while len(self.data)>=68: # 17*4
            eData     = self.data[0:68]
            self.data = self.data[68: ]
            #print "len(data) = ",len(eData)

            out = unpack(format1, eData)
            (eid,mxr,myr,mxyr,bmxr,bmyr,bmxyr,txr,tyr,
                 mxi,myi,mxyi,bmxi,bmyi,bmxyi,txi,tyi) = out
            eid2  = extract(eid,dt)
            #print "eType=%s" %(eType)
            
            dataIn = [eid2,mxr,myr,mxyr,bmxr,bmyr,bmxyr,txr,tyr,
                           mxi,myi,mxyi,bmxi,bmyi,bmxyi,txi,tyi]
            print "%s" %(self.ElementType(self.elementType)),dataIn
            #eid = self.obj.addNewEid(out)
            self.obj.add(dt,dataIn)
            #print "len(data) = ",len(self.data)
        ###
        self.handleResultsBuffer(self.OEF_Plate_alt)
        #print self.plateForces

    def OEF_CBush_alt(self): # 102-CBUSH
        deviceCode = self.deviceCode
        
        dt = self.nonlinearFactor
        isSort1 = self.isSort1()
        if isSort1:
            #print "SORT1 - %s" %(self.ElementType(self.elementType))
            format1 = 'iffffffffffff' # SORT1
            extract = self.extractSort1
            #dt = self.nonlinearFactor
        else:
            #print "SORT2 - %s" %(self.ElementType(self.elementType))
            format1 = 'fffffffffffff' # SORT2
            extract = self.extractSort2
            #eid = self.nonlinearFactor

        self.createThermalTransientObject(self.bushForces,ComplexCBUSHForce,isSort1)

        while len(self.data)>=52: # 13*4
            eData     = self.data[0:52]
            self.data = self.data[52: ]
            #print "len(data) = ",len(eData)

            out = unpack(format1, eData)
            (eid,fxr,fyr,fzr,mxr,myr,mzr,
                 fxi,fyi,fzi,mxi,myi,mzi) = out
            eid2  = extract(eid,dt)
            #print "eType=%s" %(eType)
            
            dataIn = [eid2,fxr,fyr,fzr,mxr,myr,mzr,
                           fxi,fyi,fzi,mxi,myi,mzi]
            print "%s" %(self.ElementType(self.elementType)),dataIn
            #eid = self.obj.addNewEid(out)
            self.obj.add(dt,dataIn)
            #print "len(data) = ",len(self.data)
        ###
        self.handleResultsBuffer(self.OEF_CBush_alt)
        #print self.bushForces
