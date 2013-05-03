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
from numpy import array,log,exp,pi
from baseCard import BaseCard

class AEFACT(BaseCard):
    """
    Defines real numbers for aeroelastic analysis.
    AEFACT SID D1 D2 D3 D4 D5 D6 D7
           D8  D9 -etc.-
    AEFACT 97 .3 .7 1.0
    """
    type = 'AEFACT'
    def __init__(self,card=None,data=None): ## @todo doesnt support data
        ## Set identification number. (Unique Integer > 0)
        self.sid = card.field(1)
        ## Number (float)
        self.Di = card.fields(2)

    def rawFields(self):
        fields = ['AEFACT',self.sid]+self.Di
        return fields
    
    def reprFields(self):
        return self.rawFields()

class AELINK(BaseCard):
    """
    Defines relationships between or among AESTAT and AESURF entries, such that:
    \f[ u^D + \Sigma_{i=1}^n C_i u_i^I = 0.0\f]
    AELINK ID LABLD LABL1 C1 LABL2 C2 LABL3 C3
           LABL4 C4 -etc.-
    AELINK 10 INBDA OTBDA -2.0
    """
    type = 'AELINK'
    def __init__(self,card=None,data=None): ## @todo doesnt support data
        ## an ID=0 is applicable to the global subcase, ID=1 only subcase 1
        self.id = card.field(1)
        ## defines the dependent variable name (string)
        self.label = card.field(2)
        ## defines the independent variable name (string)
        self.independentLabels = []
        ## linking coefficient (real)
        self.Cis = []

        fields = card.fields(3)
        #print "aelink fields = ",fields
        assert len(fields)%2==0,'fields=%s' %(fields)
        #print "len(fields) = ",len(fields)
        for i in range(0,len(fields),2):
            independentLabel = fields[i]
            Ci               = fields[i+1]
            self.independentLabels.append(independentLabel)
            self.Cis.append(Ci)
        ###
        #print self

    def rawFields(self):
        fields = ['AELINK',self.id,self.label]
        #print "self.independentLabels = ",self.independentLabels
        #print "self.Cis = ",self.Cis
        for ivar,ival in zip(self.independentLabels,self.Cis):
            fields += [ivar,ival]
        #print "AELINK fields = ",fields
        return fields

class AELIST(BaseCard):
    """
    Defines a list of aerodynamic elements to undergo the motion prescribed with the
    AESURF Bulk Data entry for static aeroelasticity.
    AELIST SID E1 E2 E3 E4 E5 E6 E7
    E8...
    AELIST 75 1001 THRU 1075 1101 THRU 1109 1201
           1202
    
    Remarks:
    1. These entries are referenced by the AESURF entry.
    2. When the 'THRU' option is used, all intermediate grid points must exist.
       The word 'THRU' may not appear in field 3 or 9 (2 or 9 for continuations).
    3. Intervening blank fields are not allowed.
    """
    type = 'AELIST'
    def __init__(self,card=None,data=None): ## @todo doesnt support data
        ## Set identification number. (Integer > 0)
        self.sid = card.field(1)
        ## List of aerodynamic boxes generated by CAERO1 entries to define a
        ## surface. (Integer > 0 or 'THRU')
        self.elements = self.expandThru(card.fields(2))
        self.cleanIDs()

    def cleanIDs(self):
        self.elements = list(set(self.elements))
        self.elements.sort()

    def rawFields(self):
        fields = ['AELIST',self.sid]+self.elements
        return fields

class AEPARM(BaseCard):
    """
    Defines a general aerodynamic trim variable degree-of-freedom (aerodynamic
    extra point). The forces associated with this controller will be derived
    from AEDW, AEFORCE and AEPRESS input data.
    AEPARM ID LABEL UNITS
    AEPARM 5 THRUST LBS
    """
    type = 'AEPARM'
    def __init__(self,card=None,data=None):
        if card:
            self.id    = card.field(1)
            self.label = card.field(2)
            self.units = card.fiedl(3,'')
        else:
            self.id    = data[0]
            self.label = data[1]
            self.units = data[2]
            assert len(data)==3,'data = %s' %(data)
        ###

    def rawFields(self):
        fields = ['AEPARM',self.id,self.label,self.units]
        return fields

class AESTAT(BaseCard):
    """
    Specifies rigid body motions to be used as trim variables in static aeroelasticity.
    AESTAT ID   LABEL
    AESTAT 5001 ANGLEA
    """
    type = 'AESTAT'
    def __init__(self,card=None,data=None):
        if card:
            self.id    = card.field(1)
            self.label = card.field(2)
        else:
            self.id    = data[0]
            self.label = data[1]
            assert len(data)==2,'data = %s' %(data)
        ###

    def rawFields(self):
        fields = ['AESTAT',self.id,self.label]
        return fields

class AESURF(BaseCard):
    """
    Specifies an aerodynamic control surface as a member of the set of aerodynamic extra
    points. The forces associated with this controller will be derived from rigid rotation of
    the aerodynamic model about the hinge line(s) and from AEDW, AEFORCE and
    AEPRESS input data. The mass properties of the control surface can be specified using
    an AESURFS entry.
    
    AESURF ID LABEL CID1 ALID1 CID2 ALID2 EFF LDW
    CREFC CREFS PLLIM PULIM HMLLIM HMULIM TQLLIM TQULIM
    """
    type = 'AESURF'
    def __init__(self,card=None,data=None): ## @todo doesnt support data
        ## Set identification number. (Integer > 0)
        self.aesid = card.field(1)
        ## Controller identification number
        self.cntlid = card.field(2)
        ## Controller name.
        self.label = card.field(3)

        ## Identification number of a rectangular coordinate system with a
        ## y-axis that defines the hinge line of the control surface
        ## component.
        self.cid1  = card.field(4)
        ## Identification of an AELIST Bulk Data entry that identifies all
        ## aerodynamic elements that make up the control surface
        ## component. (Integer > 0)
        self.alid1 = card.field(5)

        self.cid2  = card.field(6)
        self.alid2 = card.field(7)

        ## Control surface effectiveness. See Remark 4. (Real != 0.0; Default=1.0)
        self.eff    = card.field(8,1.0)
        ## Linear downwash flag. See Remark 2. (Character, one of LDW or NOLDW; Default=LDW).
        self.ldw    = card.field(9,'LDW')
        ## Reference chord length for the control surface. (Real>0.0; Default=1.0)
        self.crefc  = card.field(10,1.0)
        ## Reference surface area for the control surface. (Real>0.0; Default=1.0)
        self.crefs  = card.field(11,1.0)
        ## Lower and upper deflection limits for the control surface in
        ## radians. (Real, Default = +/- pi/2)
        self.pllim  = card.field(12,-pi/2.)
        self.pulim  = card.field(13, pi/2.)
        ## Lower and upper hinge moment limits for the control surface in
        ## force-length units. (Real, Default = no limit) -> 1e8
        self.hmllim = card.field(14)
        self.hmulim = card.field(15)
        ## Set identification numbers of TABLEDi entries that provide the
        ## lower and upper deflection limits for the control surface as a
        ## function of the dynamic pressure. (Integer>0, Default = no limit)
        self.tqllim = card.field(16)
        self.tqulim = card.field(17)
        

    def rawFields(self):
        fields = ['AESURF',self.aesid,self.cntlid,self.label,self.cid1,self.alid1,self.cid2,self.alid2,self.eff,self.ldw,
                           self.crefc,self.crefs,self.pllim,self.pulim,self.hmllim,self.hmulim,self.tqllim,self.tqulim]
        return fields

    def reprFields(self):
        eff   = self.setBlankIfDefault(self.eff,1.0)
        ldw   = self.setBlankIfDefault(self.ldw,'LDW')
        crefc = self.setBlankIfDefault(self.crefc,1.0)
        crefs = self.setBlankIfDefault(self.crefs,1.0)

        pllim = self.setBlankIfDefault(self.pllim,-pi/2.)
        pulim = self.setBlankIfDefault(self.pulim, pi/2.)
        
        fields = ['AESURF',self.aesid,self.cntlid,self.label,self.cid1,self.alid1,self.cid2,self.alid2,eff,ldw,
                           crefc,crefs,pllim,pulim,self.hmllim,self.hmulim,self.tqllim,self.tqulim]
        return fields

class AESURFS(BaseCard): # not integrated
    """
    Optional specification of the structural nodes associated with an aerodynamic control
    surface that has been defined on an AESURF entry. The mass associated with these
    structural nodes define the control surface moment(s) of inertia about the hinge
    line(s).
    Specifies rigid body motions to be used as trim variables in static aeroelasticity.
    AESURFS ID   LABEL - LIST1 - LIST2
    AESURFS 6001 ELEV  - 6002  - 6003
    """
    type = 'AESURFS'
    def __init__(self,card=None,data=None):
        if card:
            self.id    = card.field(1)
            self.label = card.field(2)
            self.list1 = card.field(4)
            self.list2 = card.field(6)
        else:
            self.id    = data[0]
            self.label = data[1]
            self.list1 = data[2]
            self.list2 = data[3]
            assert len(data)==4,'data = %s' %(data)
        ###

    def rawFields(self):
        fields = ['AESURFS',self.id,self.label,None,self.list1,None,self.list2]
        return fields

class Aero(BaseCard):
    """Base class for AERO and AEROS cards."""
    def __init__(self,card,data):
        pass

    def IsSymmetricalXY(self):
        if self.symXY==1:
            return True
        return False

    def IsSymmetricalXZ(self):
        if self.symXZ==1:
            return True
        return False

    def EnableGroundEffect(self):
        self.symXY = -1

    def DisableGroundEffect(self):
        self.symXY = 1

    def IsAntiSymmetricalXY(self):
        if self.symXY==-1:
            return True
        return False

    def IsAntiSymmetricalXZ(self):
        if self.symXY==-1:
            return True
        return False

class AERO(Aero):
    """
    Gives basic aerodynamic parameters for unsteady aerodynamics.
    AERO ACSID VELOCITY REFC RHOREF SYMXZ SYMXY
    AERO 3     1.3+4    100.  1.-5  1     -1
    """
    type = 'AERO'
    def __init__(self,card=None,data=None):
        Aero.__init__(self,card,data)
        if card:
            self.acsid    = card.field(1,0)
            self.velocity = card.field(2)
            self.cRef     = card.field(3)
            self.rhoRef   = card.field(4)
            self.symXZ    = card.field(5,0)
            self.symXY    = card.field(6,0)
        else:
            self.acsid    = data[0]
            self.velocity = data[1]
            self.cRef     = data[2]
            self.rhoRef   = data[3]
            self.symXZ    = data[4]
            self.symXY    = data[5]
            assert len(data)==6,'data = %s' %(data)
        ###
        #angle = self.wg*self.t*(t-(x-self.x0)/self.V) # T is the tabular function

    def rawFields(self):
        fields = ['AERO',self.acsid,self.velocity,self.cRef,self.rhoRef,self.symXZ,self.symXY]
        return fields

    def reprFields(self):
        symXZ = self.setBlankIfDefault(self.symXZ,0)
        symXY = self.setBlankIfDefault(self.symXY,0)
        fields = ['AERO',self.acsid,self.velocity,self.cRef,self.rhoRef,symXZ,symXY]
        return fields

class AEROS(Aero):
    """
    Gives basic aerodynamic parameters for unsteady aerodynamics.
    AEROS ACSID RCSID REFC REFB REFS SYMXZ SYMXY
    AEROS 10   20     10.  100. 1000. 1
    """
    type = 'AEROS'
    def __init__(self,card=None,data=None):
        Aero.__init__(self,card,data)
        if card:
            self.acsid  = card.field(1,0)
            self.rcsid  = card.field(2)
            self.cRef   = card.field(3)
            self.bRef   = card.field(4)
            self.Sref   = card.field(5)
            self.symXZ  = card.field(6,0)
            self.symXY  = card.field(7,0)
        else:
            self.acsid  = data[0]
            self.rcsid  = data[1]
            self.cRef   = data[2]
            self.bRef   = data[3]
            self.Sref   = data[4]
            self.symXZ  = data[5]
            self.symXY  = data[6]
            assert len(data)==7,'data = %s' %(data)
        ###

    def rawFields(self):
        fields = ['AEROS',self.acsid,self.rcsid,self.cRef,self.bRef,self.Sref,self.symXZ,self.symXY]
        return fields

    def reprFields(self):
        symXZ = self.setBlankIfDefault(self.symXZ,0)
        symXY = self.setBlankIfDefault(self.symXY,0)
        fields = ['AEROS',self.acsid,self.rcsid,self.cRef,self.bRef,self.Sref,symXZ,symXY]
        return fields

class CSSCHD(BaseCard):
    """
    Defines a scheduled control surface deflection as a function of Mach number and
    angle of attack
    CSSCHD SlD AESID LALPHA LMACH LSCHD
    """
    type = 'ASSCHD'
    def __init__(self,card=None,data=None):
        Aero.__init__(self,card,data)
        if card:
            self.sid    = card.field(1)
            self.aesid  = card.field(2) # AESURF
            self.lAlpha = card.field(3) # AEFACT
            self.lMach  = card.field(4) # AEFACT
            self.lSchd  = card.field(5) # AEFACT
        else:
            self.sid    = data[0]
            self.aesid  = data[1] # AESURF
            self.lAlpha = data[2] # AEFACT
            self.lMach  = data[3] # AEFACT
            self.lSchd  = data[4] # AEFACT
        ###

    def crossReference(self,model):
        self.aesid  = self.AESurf(self.aesid)
        self.lAlpha = self.AEFact(self.lAlpha)
        self.lMach  = self.AEFact(self.lMach)
        self.lSchd  = self.AEFact(self.lSchd)

    def AESid(self):
        if isinstance(self.aesid,int):
            return self.aesid
        return self.aesid.aesid

    def LAlpha(self):
        if isinstance(self.lAlpha,int):
            return self.lAlpha
        return self.lAlpha.sid

    def LMach(self):
        if isinstance(self.lMach,int):
            return self.lMach
        return self.lMach.sid

    def LSchd(self):
        if isinstance(self.lSchd,int):
            return self.lSchd
        return self.lSchd.sid

    def rawFields(self):
        fields = ['CSSCHD',self.sid,self.AESid(),self.LAlpha(),self.LMach(),self.LSchd()]
        return fields

    def reprFields(self):
        return self.rawFields()

class CAERO1(BaseCard):
    """
    Defines an aerodynamic macro element (panel) in terms of two leading edge locations
    and side chords. This is used for Doublet-Lattice theory for subsonic aerodynamics
    and the ZONA51 theory for supersonic aerodynamics.
    CAERO1 EID PID CP NSPAN NCHORD LSPAN LCHORD IGID
    X1 Y1 Z1 X12 X4 Y4 Z4 X43
    """
    type = 'CAERO1'
    def __init__(self,card=None,data=None):
        """
        1
        | \
        |   \
        |     \
        |      4
        |      |
        |      |
        2------3
        """
        #Material.__init__(self,card)
        self.eid    =  card.field(1)
        self.pid    =  card.field(2)
        self.cp     =  card.field(3,0)
        self.nspan  =  card.field(4,0)
        self.nchord =  card.field(5,0)
        
        #if self.nspan==0:
        self.lspan  =  card.field(6)

        #if self.nchord==0:
        self.lchord =  card.field(7)
        
        self.igid =  card.field(8)

        self.p1   =  array([card.field(9, 0.0), card.field(10,0.0), card.field(11,0.0)])
        self.x12 = card.field(12,0.)
        #self.p2   =  self.p1+array([card.field(12,0.0), 0., 0.])

        self.p4   =  array([card.field(13,0.0), card.field(14,0.0), card.field(15,0.0)])
        self.x43 = card.field(16,0.)
        #self.p3   =  self.p4+array([card.field(16,0.0), 0., 0.])

    def Cp(self):
        if isinstance(self.cp,int):
            return self.cp
        return self.cp.cid

    def Pid(self):
        if isinstance(self.pid,int):
            return self.pid
        return self.pid.pid

    def crossReference(self,model):
        self.pid = model.PAero(self.pid)
        self.cp  = model.Coord(self.cp)

    def Points(self):
        p1,matrix = self.cp.transformToGlobal(self.p1)
        p4,matrix = self.cp.transformToGlobal(self.p4)

        p2 = self.p1+array([self.x12,0.,0.])
        p3 = self.p4+array([self.x43,0.,0.])

        #print "x12 = ",self.x12
        #print "x43 = ",self.x43
        #print "pcaero[%s] = %s" %(self.eid,[p1,p2,p3,p4])
        return [p1,p2,p3,p4]
    
    def SetPoints(self,points):
        self.p1 = points[0]
        self.p2 = points[1]
        self.p3 = points[2]
        self.p4 = points[3]
        x12 = self.p2-self.p1
        x43 = self.p4-self.p3
        self.x12 = x12[0]
        self.x43 = x43[0]

    def rawFields(self):
        fields = ['CAERO1',self.eid,self.Pid(),self.Cp(),self.nspan,self.nchord,self.lspan,self.lchord,self.igid,
                         ]+list(self.p1)+[self.x12]+list(self.p4)+[self.x43]
        return fields

    def reprFields(self):
        cp     = self.setBlankIfDefault(self.Cp(),0)
        nspan  = self.setBlankIfDefault(self.nspan,0)
        nchord = self.setBlankIfDefault(self.nchord,0)
        fields = ['CAERO1',self.eid,self.Pid(),cp,nspan,nchord,self.lspan,self.lchord,self.igid,
                         ]+list(self.p1)+[self.x12]+list(self.p4)+[self.x43]
        return fields

class CAERO2(BaseCard):
    """
    Aerodynamic Body Connection
    Defines aerodynamic slender body and interference elements for Doublet-Lattice
    aerodynamics
    """
    type = 'CAERO2'
    def __init__(self,card=None,data=None):
        """
        1 \
        |   \
        |     \
        |      3
        |      |
        |      |
        2------4
        """
        #Material.__init__(self,card)
        ## Element identification number
        self.eid  = card.field(1)
        ## Property identification number of a PAERO2 entry.
        self.pid  = card.field(2)
        ## Coordinate system for locating point 1.
        self.cp   = card.field(3,0)
        ## Number of slender body elements. If NSB > 0, then NSB equal divisions
        ## are assumed; if zero or blank, specify a list of divisions in LSB.
        ## (Integer >= 0)
        self.nsb  = card.field(4)
        ## Number of interference elements. If NINT > 0, then NINT equal
        ## divisions are assumed; if zero or blank, specify a list of divisions in
        ## LINT. (Integer >= 0)
        self.nint = card.field(5)
        
        ## ID of an AEFACT Bulk Data entry for slender body division points; used
        ## only if NSB is zero or blank. (Integer >= 0)
        self.lsb  = card.field(6) # ID of AEFACT
        ## ID of an AEFACT data entry containing a list of division points for
        ## interference elements; used only if NINT is zero or blank. (Integer > 0)
        self.lint = card.field(7)
        ## Interference group identification. Aerodynamic elements with different
        ## IGIDs are uncoupled. (Integer >= 0)
        self.igid = card.field(8)
        ## Location of point 1 in coordinate system CP
        self.p1   =  array([card.field(9, 0.0), card.field(10,0.0), card.field(11,0.0)])
        ## Length of body in the x-direction of the aerodynamic coordinate system.
        ## (Real > 0)
        self.x12 = card.field(12,0.)

    def Cp(self):
        if isinstance(self.cp,int):
            return self.cp
        return self.cp.cid

    def Pid(self):
        if isinstance(self.pid,int):
            return self.pid
        return self.pid.pid

    def Lsb(self):  # AEFACT
        if isinstance(self.lsb,int):
            return self.lsb
        return self.lsb.sid

    def crossReference(self,model):
        self.pid = model.PAero(self.pid)  # links to PAERO2
        self.cp  = model.Coord(self.cp)
        #self.lsb = model.AeFact(self.lsb) # not added

    def Points(self):
        p1,matrix = self.cp.transformToGlobal(self.p1)

        p2 = self.p1+array([self.x12,0.,0.])
        #print "x12 = ",self.x12
        #print "pcaero[%s] = %s" %(self.eid,[p1,p2])
        return [p1,p2]
    
    def SetPoints(self,points):
        self.p1 = points[0]
        self.p2 = points[1]
        x12 = self.p2-self.p1
        self.x12 = x12[0]

    def rawFields(self):
        fields = ['CAERO2',self.eid,self.Pid(),self.Cp(),self.nsb,self.nint,self.lsb,self.lint,self.igid,
                         ]+list(self.p1)+[self.x12]
        return fields

    def reprFields(self):
        cp     = self.setBlankIfDefault(self.Cp(),0)
        fields = ['CAERO2',self.eid,self.Pid(),cp,self.nsb,self.nint,self.lsb,self.lint,self.igid,
                         ]+list(self.p1)+[self.x12]
        return fields

class FLFACT(BaseCard):
    """
    FLFACT SID F1 F2 F3 F4 F5 F6 F7
    F8 F9 -etc.-
    
    FLFACT 97 .3 .7 3.5
    
    FLFACT SID F1 THRU FNF NF FMID       # delta quantity approach
    FLFACT 201 .200 THRU .100 11 .133333
    """
    type = 'FLFACT'
    def __init__(self,card=None,data=None):
        if card:
            self.sid     = card.field(1)
            self.factors = card.fields(2)
            
            if len(self.factors)>1 and self.factors[1]=='THRU':
                raise NotImplementedError('embedded THRUs not supported yet on FLFACT card\n')
                #(a,thru,b,n,dn) = factors
                #for i in range(
            ###
        else:
            self.sid     = data[0]
            self.factors = data[1:]
        ###

    def rawFields(self):
        fields = ['FLFACT',self.sid]+self.factors
        return fields

    def __repr__(self):
        fields = self.reprFields()
        return self.printCard(fields,tol=0.)

class FLUTTER(BaseCard):
    """
    Defines data needed to perform flutter analysis.
    FLUTTER SID METHOD DENS MACH RFREQ IMETH NVALUE/OMAX EPS
    FLUTTER 19  K      119  219  319       S 5           1.-4
    """
    type = 'FLUTTER'
    def __init__(self,card=None,data=None):
        if card:
            self.sid      = card.field(1)
            self.method   = card.field(2)
            self.density  = card.field(3)
            self.mach     = card.field(4)
            self.rfreqVel = card.field(5)
        else:
            assert len(data)==8,'FLUTTER = %s' %(data)
            self.sid      = data[0]
            self.method   = data[1]
            self.density  = data[2]
            self.mach     = data[3]
            self.rfreqVel = data[4]
            self.method   = data[5]
            self.imethod  = data[6]
            self.nValue   = data[7]
            self.omax     = data[8]
            raise NotImplementedError('verify...')
        ###
        assert self.method in ['K','PK','PKNL','PKS','PKNLS','KE']

        if self.method in ['K','KE']:
            self.imethod = card.field(6,'L')
            self.nValue  = card.field(7)
            self.omax    = None
            assert self.imethod in ['L','S']
        elif self.method in ['PKS','PKNLS']:
            self.imethod = None
            self.nValue  = None
            self.omax    = card.field(7)
        else:
            self.nValue  = card.field(7)
            self.omax    = None
            self.imethod = None

        self.epsilon = card.field(8) # no default listed...

    def _rawNValueOMax(self):
        if self.method in ['K','KE']:
            return (self.imethod,self.nValue)
            assert self.imethod in ['L','S']
        elif self.method in ['PKS','PKNLS']:
            return(self.imethod,self.omax)
        else:
            return(self.imethod,self.nValue)
        ###

    def _reprNValueOMax(self):
        if self.method in ['K','KE']:
            imethod = self.setBlankIfDefault(self.imethod,'L')
            return (imethod,self.nValue)
            assert self.imethod in ['L','S']
        elif self.method in ['PKS','PKNLS']:
            return(self.imethod,self.omax)
        else:
            return(self.imethod,self.nValue)
        ###

    def rawFields(self):
        (imethod,nValue) = self._rawNValueOMax()
        fields = ['FLUTTER',self.sid,self.method,self.density,self.mach,self.rfreqVel,imethod,nValue,self.epsilon]
        return fields

    #def reprFields(self):
    #    (imethod,nValue) = self._reprNValueOMax()
    #    fields = ['FLUTTER',self.sid,self.method,self.density,self.mach,self.rfreqVel,imethod,nValue,self.epsilon]
    #    return fields

class GUST(BaseCard):
    """
    Defines a stationary vertical gust for use in aeroelastic response analysis.
    GUST SID DLOAD WG  X0   V
    GUST 133 61    1.0 0.   1.+4
    """
    type = 'GUST'
    def __init__(self,card=None,data=None):
        if card:
            self.sid   = card.field(1)
            self.dload = card.field(2)
            self.wg    = card.field(3)
            self.x0    = card.field(4)
            self.V     = card.field(5)
        else:
            self.sid   = data[0]
            self.dload = data[1]
            self.wg    = data[2]
            self.x0    = data[3]
            self.V     = data[4]
            assert len(data)==5,'data = %s' %(data)
        ###
        #angle = self.wg*self.t*(t-(x-self.x0)/self.V) # T is the tabular function

    def rawFields(self):
        fields = ['GUST',self.sid,self.dload,self.wg,self.x0,self.V]
        return fields

class MKAERO1(BaseCard):
    """
    Provides a table of Mach numbers (m) and reduced frequencies (k) for aerodynamic
    matrix calculation
    MKAERO1 m1 m2 m3 m4 m5 m6 m7 m8
            k1 k2 k3 k4 k5 k6 k7 k8
    """
    type = 'MKAERO1'
    def __init__(self,card=None,data=None):
        if card:
            fields  = card.fields(1)
            nFields = len(fields)-8
            self.machs  = []
            self.rFreqs = []
            for i in range(1,1+nFields):
                self.machs.append( card.field(i  ))
                self.rFreqs.append(card.field(i+8))
            ###
        else:
            raise NotImplementedError('MKAERO1')
        ###
        #print "machs  = ",self.machs
        #print "rFreqs = ",self.rFreqs
        #print self
        #sys.exit()
    
    def addFreqs(self,mkaero):
        self.getMach_rFreqs()
        for m in mkaero.machs:
            self.machs.append(m)
        for f in mkaero.rFreqs:
            self.rFreqs.append(f)
        ###

    def rawFields(self):
        #fields = ['MKAERO2']
        #for i,(mach,rfreq) in enumerate(zip(self.machs,self.rFreqs)):
        #    fields += [mach,rfreq]
        machs = [None]*8        
        freqs = [None]*8
        for i,mach in enumerate(self.machs):
            machs[i] = mach
        for i,freq in enumerate(self.rFreqs):
            freqs[i] = freq
        fields = ['MKAERO1']+machs+freqs
        return fields

    def getMach_rFreqs(self):
        return (self.machs,self.rFreqs)

    def reprFields(self):
        return self.rawFields()

class MKAERO2(BaseCard):
    """
    Provides a table of Mach numbers (m) and reduced frequencies (k) for aerodynamic
    matrix calculation
    MKAERO2 m1 k1 m2 k2 m3 k3 m4 k4
    """
    type = 'MKAERO2'
    def __init__(self,card=None,data=None):
        if card:
            fields  = card.fields(1)
            nFields = len(fields)
            self.machs  = []
            self.rFreqs = []
            for i in range(1,1+nFields,2):
                self.machs.append( card.field(i  ))
                self.rFreqs.append(card.field(i+1))
            ###
        else:
            raise NotImplementedError('MKAERO2')
        ###
    
    def addFreqs(self,mkaero):
        self.getMach_rFreqs()
        for m in mkaero.machs:
            self.machs.append(m)
        for f in mkaero.rFreqs:
            self.rFreqs.append(f)
        ###

    def rawFields(self):
        fields = ['MKAERO2']
        for i,(mach,rfreq) in enumerate(zip(self.machs,self.rFreqs)):
            fields += [mach,rfreq]
        return fields

    def getMach_rFreqs(self):
        return (self.machs,self.rFreqs)

    def reprFields(self):
        return self.rawFields()


class PAERO1(BaseCard):
    """
    Defines associated bodies for the panels in the Doublet-Lattice method.
    PAERO1 PID B1 B2 B3 B4 B5 B6
    """
    type = 'PAERO1'
    def __init__(self,card=None,data=None):
        self.pid = card.field(1)
        Bi = card.fields(2)
        self.Bi = []

        for bi in Bi:
            if isinstance(bi,int) and bi>=0:
                self.Bi.append(bi)
            elif bi is not None:
                raise Exception('invalid Bi value on PAERO1 bi=|%r|' %(bi))
            #else:
            #    pass
        ###

    def Bodies(self):
        return self.Bi

    def rawFields(self):
        fields = ['PAERO1',self.pid] + self.Bi
        return fields

    def reprFields(self):
        return self.rawFields()

class PAERO2(BaseCard):
    """
    Defines the cross-sectional properties of aerodynamic bodies
    PAERO2 PID ORIENT WIDTH AR LRSB LRIB LTH1 LTH2
    THI1 THN1 THI2 THN2 THI3 THN3
    """
    type = 'PAERO2'
    def __init__(self,card=None,data=None):
        ## Property identification number. (Integer > 0)
        self.pid    = card.field(1)
        ## Orientation flag. Type of motion allowed for bodies. Refers to the
        ## aerodynamic coordinate system of ACSID. See AERO entry.
        ## (Character = 'Z', 'Y', or 'ZY')
        self.orient = card.field(2)
        ## Reference half-width of body and the width of the constant width
        ## interference tube. (Real > 0.0)
        self.width  = card.field(3)
        ## Aspect ratio of the interference tube (height/width). float>0.
        self.AR     = card.field(4)
        ## Identification number of an AEFACT entry containing a list of slender
        ## body half-widths at the end points of the slender body elements. If
        ## blank, the value of WIDTH will be used. (Integer > 0 or blank)
        self.lrsb   = card.field(5)
        ## Identification number of an AEFACT entry containing a list of slender
        ## body half-widths at the end points of the interference elements. If
        ## blank, the value of WIDTH will be used. (Integer > 0 or blank)
        self.lrib   = card.field(6)
        ## dentification number of AEFACT entries for defining ? arrays for
        ## interference calculations. (Integer >= 0)
        self.lth1   = card.field(7)
        self.lth2   = card.field(8)
        self.thi = []
        self.thn = []
        fields = card.fields(9)
        nFields = len(fields)
        for i in range(9,9+nFields,2):
            self.thi.append(card.field(i  ))
            self.thi.append(card.field(i+1))
        ###

    def rawFields(self):
        fields = ['PAERO2',self.pid,self.orient,self.width,self.AR,self.lrsb,self.lrib,self.lth1,self.lth2]
        for thi,thn in zip(self.thi,self.thn):
            fields += [thi,thn]
        return fields

    def reprFields(self):
        return self.rawFields()

class SPLINE1(BaseCard):
    """
    Defines a surface spline for interpolating motion and/or forces for aeroelastic
    problems on aerodynamic geometries defined by regular arrays of aerodynamic
    points
    SPLINE1 EID CAERO BOX1 BOX2 SETG DZ METH USAGE
    NELEM MELEM
    
    SPLINE1 3   111    115  122  14   0.
    """
    type = 'SPLINE1'
    def __init__(self,card=None,data=None):
        if card:
            self.eid    = card.field(1)
            self.caero  = card.field(2)
            self.box1   = card.field(3)
            self.box2   = card.field(4)
            self.setg   = card.field(5)
            self.dz     = card.field(6,0.0)
            self.method = card.field(7,'IPS')
            self.usage  = card.field(8,'BOTH')
            self.nelements = card.field(9,10)
            self.melements = card.field(10,10)
        else:
            self.eid       = data[0]
            self.caero     = data[1]
            self.box1      = data[2]
            self.box2      = data[3]
            self.setg      = data[4]
            self.dz        = data[5]
            self.method    = data[6]
            self.usage     = data[7]
            self.nelements = data[8]
            self.melements = data[9]
            assert len(data)==10,'data = %s' %(data)
        ###

        assert self.box2>=self.box1
        assert self.method in ['IPS','TPS','FPS']
        assert self.usage  in ['FORCE','DISP','BOTH']
    
    def CAero(self):
        if isinstance(self.caero,int):
            return self.caero
        return self.caero.eid

    def Set(self):
        if isinstance(self.setg,int):
            return self.setg
        return self.setg.sid

    def crossReference(self,model):
        self.caero = model.CAero(self.caero)
        self.setg  = model.Set(self.setg)

    def rawFields(self):
        fields = ['SPLINE1',self.eid,self.CAero(),self.box1,self.box2,self.Set(),self.dz,self.method,self.usage,
                            self.nelements,self.melements]
        return fields

    def reprFields(self):
        dz        = self.setBlankIfDefault(self.dz,0.)
        method    = self.setBlankIfDefault(self.method,'IPS')
        usage     = self.setBlankIfDefault(self.usage,'BOTH')
        nelements = self.setBlankIfDefault(self.nelements,10)
        melements = self.setBlankIfDefault(self.melements,10)
        
        fields = ['SPLINE1',self.eid,self.CAero(),self.box1,self.box2,self.Set(),dz,method,usage,
                            nelements,melements]
        fields = self.wipeEmptyFields(fields)
        return fields

class SPLINE2(BaseCard):
    """
    Defines a surface spline for interpolating motion and/or forces for aeroelastic
    problems on aerodynamic geometries defined by regular arrays of aerodynamic
    points
    SPLINE2 EID CAERO ID1 ID2 SETG DZ DTOR CID
    DTHX DTHY None USAGE
    SPLINE2 5 8 12 24 60 0. 1.0 3
    1.
    """
    type = 'SPLINE2'
    def __init__(self,card=None,data=None):
        if card:
            self.eid   = card.field(1)
            self.caero = card.field(2)
            self.id1   = card.field(3)
            self.id2   = card.field(4)
            self.setg  = card.field(5)
            self.dz    = card.field(6,0.0)
            self.dtor  = card.field(7,1.0)
            self.cid   = card.field(8,0)
            self.thx   = card.field(9)
            self.thy   = card.field(10)
            
            self.usage = card.field(12,'BOTH')
            #print self
            #raise Exception(str(self))
        else:
            raise NotImplementedError('not supported')
        ###

    def Cid(self):
        if isinstance(self.cid,int):
            return self.cid
        return self.cid.cid

    def CAero(self):
        if isinstance(self.caero,int):
            return self.caero
        return self.caero.eid

    def Set(self):
        if isinstance(self.setg,int):
            return self.setg
        return self.setg.sid

    def crossReference(self,model):
        self.caero = model.CAero(self.caero)
        self.setg  = model.Set(self.setg)

    def rawFields(self):
        fields = ['SPLINE2',self.eid,self.CAero(),self.id1,self.id2,self.Set(),self.dz,self.dtor,self.Cid(),
                            self.thx,self.thy,None,self.usage]
        return fields

    def reprFields(self):
        dz    = self.setBlankIfDefault(self.dz,0.)
        usage = self.setBlankIfDefault(self.usage,'BOTH')
        fields = ['SPLINE2',self.eid,self.CAero(),self.id1,self.id2,self.Set(),dz,self.dtor,self.Cid(),
                            self.thx,self.thy,None,usage]
        return fields

class TRIM(BaseCard):
    type = 'TRIM'
    def __init__(self,card=None,data=None):
        if card:
            ## Trim set identification number. (Integer > 0)
            self.sid  = card.field(1)
            ## Mach number. (Real > 0.0 and != 1.0)
            self.mach = card.field(2)
            ## Dynamic pressure. (Real > 0.0)
            self.q    = card.field(3)
            ## The label identifying aerodynamic trim variables defined on an AESTAT or AESURF entry.
            self.labels = []
            ## The magnitude of the aerodynamic extra point degree-of-freedom. (Real)
            self.uxs    = []
            ## Flag to request a rigid trim analysis (Real > 0.0 and < 1.0, Default =1.0. A value of 0.0 provides a rigid trim analysis,
            ## not supported
            self.aeqr = 1.0
            fields = card.fields(4)

            i=0
            nFields = len(fields)-1
            while i<nFields: ## @todo doesnt support aeqr
                label = fields[i]
                ux = fields[i+1]
                assert isinstance(label,str),'TRIM card doesnt support AEQR field...iField=%s label=%s fields=%s' %(i,label,card.fields(0))
                self.labels.append(label)
                self.uxs.append(ux)
                if i==2:
                    self.aeqr = card.field(4+i+2,1.0)
                    i+=1
                i+=2
            ###
        else:
            raise NotImplementedError('TRIM not supported')
        ###

    def rawFields(self):
        fields = ['TRIM',self.sid,self.mach,self.q]
        for i,(label,ux) in enumerate(zip(self.labels,self.uxs)):
            fields += [label,ux]
            if i==1:
                fields += [self.aeqr]
        return fields