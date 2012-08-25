from numpy import array
from baseCard import BaseCard

class DAREA(BaseCard):
    """
    Defines scale (area) factors for static and dynamic loads. In dynamic analysis, DAREA
    is used in conjunction with ACSRCE, RLOADi and TLOADi entries.
    DAREA SID P1 C1 A1  P2 C2 A2
    DAREA 3   6   2 8.2 15 1  10.1
    """
    type = 'DAERO1'
    def __init__(self,card):
        #Material.__init__(self,card)
        self.sid   =  card.field(1)
        self.p     = [card.field(2),card.field(5)]
        self.c     = [card.field(3),card.field(6)]
        self.a     = [card.field(4),card.field(7)]
        self.units = card.field(3)

    def __repr__(self):
        fields = ['DAREA',self.sid, self.p[0],self.c[0],self.a[0],  self.p[1],self.c[1],self.a[1] ]
        return self.printCard(fields)

class SPLINE1(BaseCard): # not integrated
    """
    Defines a surface spline for interpolating motion and/or forces for aeroelastic
    problems on aerodynamic geometries defined by regular arrays of aerodynamic
    points
    SPLINE1 EID CAERO BOX1 BOX2 SETG DZ METH USAGE
    NELEM MELEM
    
    SPLINE1 3   111    115  122  14   0.
    """
    type = 'SPLINE1'
    def __init__(self,card):
        #Material.__init__(self,card)
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

        assert self.box2>=self.box1
        assert self.method in ['IPS','TPS','FPS']
        assert self.usage  in ['FORCE','DISP','BOTH']

    def __repr__(self):
        method    = self.setBlankIfDefault(self.method,'IPS')
        usage     = self.setBlankIfDefault(self.usage,'BOTH')
        nelements = self.setBlankIfDefault(self.nelements,10)
        melements = self.setBlankIfDefault(self.melements,10)
        fields = ['SPLINE1',self.eid,self.caero,self.box1,self.box2,self.setg,self.dz,method,usage,
                            nelements,melements]
        fields = self.wipeEmptyFields(fields)
        return self.printCard(fields)

class CAERO1(BaseCard): # add helper functions
    """
    Defines an aerodynamic macro element (panel) in terms of two leading edge locations
    and side chords. This is used for Doublet-Lattice theory for subsonic aerodynamics
    and the ZONA51 theory for supersonic aerodynamics.
    CAERO1 EID PID CP NSPAN NCHORD LSPAN LCHORD IGID
    X1 Y1 Z1 X12 X4 Y4 Z4 X43
    """
    type = 'CAERO1'
    def __init__(self,card):
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
        self.p2   =  self.p1+[card.field(12,0.0), 0., 0.]

        self.p4   =  array([card.field(13,0.0), card.field(14,0.0), card.field(15,0.0)])
        self.p3   =  self.p4+[card.field(16,0.0), 0., 0.]

    def points(self):
        raise Exception('not implemented in CAERO1')

    def __repr__(self):
        x12 = self.p2-self.p1
        x43 = self.p4-self.p3
        fields = ['CAERO1',self.eid,self.pid,self.cp,self.nspan,self.nchord,self.lspan,self.lchord,self.igid,
                         ]+list(self.p1)+[x12[0]]+list(self.p4)+[x43[0]]
        return self.printCard(fields)


class AEPARM(BaseCard): # not integrated
    """
    Defines a general aerodynamic trim variable degree-of-freedom (aerodynamic extra
    point). The forces associated with this controller will be derived from AEDW,
    AEFORCE and AEPRESS input data.
    AEPARM ID LABEL UNITS
    AEPARM 5 THRUST LBS
    """
    type = 'AEPARM'
    def __init__(self,card):
        #Material.__init__(self,card)
        self.id    = card.field(1)
        self.label = card.field(2)
        self.units = card.fiedl(3)

    def __repr__(self):
        fields = ['AEPARM',self.id,self.label,self.units]
        return self.printCard(fields)

class AESTAT(BaseCard): # not integrated
    """
    Specifies rigid body motions to be used as trim variables in static aeroelasticity.
    AESTAT ID   LABEL
    AESTAT 5001 ANGLEA
    """
    type = 'AESTAT'
    def __init__(self,card):
        #Material.__init__(self,card)
        self.id    = card.field(1)
        self.label = card.field(2)

    def __repr__(self):
        fields = ['AESTAT',self.id,self.label]
        return self.printCard(fields)

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
    def __init__(self,card):
        #Material.__init__(self,card)
        self.id    = card.field(1)
        self.label = card.field(2)
        self.list1 = card.field(4)
        self.list2 = card.field(6)

    def __repr__(self):
        fields = ['AESURFS',self.id,self.label,None,self.list1,None,self.list2]
        return self.printCard(fields)

class FLFACT(BaseCard):
    """
    FLFACT SID F1 F2 F3 F4 F5 F6 F7
    F8 F9 -etc.-
    
    FLFACT 97 .3 .7 3.5
    
    FLFACT SID F1 THRU FNF NF FMID       # delta quantity approach
    FLFACT 201 .200 THRU .100 11 .133333
    """
    type = 'FLFACT'
    def __init__(self,card):
        #Material.__init__(self,card)
        self.sid     = card.field(1)
        self.factors = card.fields(2)
        if self.factors[1]=='THRU':
            raise Exception('embedded THRUs not supported yet on FLFACT card\n')
            #(a,thru,b,n,dn) = factors
            #for i in range(

    def __repr__(self):
        fields = ['FLFACT',self.sid]+self.factors
        return self.printCard(fields)

class GUST(BaseCard):
    """
    Defines a stationary vertical gust for use in aeroelastic response analysis.
    GUST SID DLOAD WG  X0   V
    GUST 133 61    1.0 0.   1.+4
    """
    type = 'GUST'
    def __init__(self,card):
        self.sid   = card.field(1)
        self.dload = card.field(2)
        self.wg    = card.field(3)
        self.x0    = card.field(4)
        self.V     = card.field(5)
        #angle = self.wg*self.t*(t-(x-self.x0)/self.V) # T is the tabular function

    def __repr__(self):
        fields = ['GUST',self.sid,self.dload,self.wg,self.x0,self.V]
        return self.printCard(fields)


class Aero(BaseCard):
    """Base class for AERO and AEROS cards."""
    def __init__(self,card):
        pass

    def isSymmetricalXY(self):
        if self.symXY==1:
            return True
        return False

    def isSymmetricalXZ(self):
        if self.symXZ==1:
            return True
        return False

    def setGroundEffect(self):
        self.symXY = -1

    def isAntiSymmetricalXY(self):
        if self.symXY==-1:
            return True
        return False

    def isAntiSymmetricalXZ(self):
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
    def __init__(self,card):
        Aero.__init__(self,card)
        self.acsid    = card.field(1)
        self.velocity = card.field(2)
        self.cRef     = card.field(3)
        self.rhoRef   = card.field(4)
        self.symXZ    = card.field(5,0)
        self.symXY    = card.field(6,0)
        #angle = self.wg*self.t*(t-(x-self.x0)/self.V) # T is the tabular function

    def __repr__(self):
        symXZ = self.setBlankIfDefault(self.symXZ,0)
        symXY = self.setBlankIfDefault(self.symXY,0)
        fields = ['AERO',self.acsid,self.velocity,self.cRef,self.rhoRef,symXZ,symXY]
        return self.printCard(fields)

class AEROS(Aero):
    """
    Gives basic aerodynamic parameters for unsteady aerodynamics.
    AEROS ACSID RCSID REFC REFB REFS SYMXZ SYMXY
    AEROS 10   20     10.  100. 1000. 1
    """
    type = 'AEROS'
    def __init__(self,card):
        Aero.__init__(self,card)
        self.acsid  = card.field(1)
        self.rcsid  = card.field(2)
        self.cRef   = card.field(3)
        self.bRef   = card.field(4)
        self.Sref   = card.field(4)
        self.symXZ  = card.field(5,0)
        self.symXY  = card.field(6,0)

    def __repr__(self):
        symXZ = self.setBlankIfDefault(self.symXZ,0)
        symXY = self.setBlankIfDefault(self.symXY,0)
        fields = ['AEROS',self.acsid,self.rcsid,self.cRef,self.bRef,self.Sref,symXZ,symXY]
        return self.printCard(fields)

class GRAV(BaseCard):
    """
    Defines acceleration vectors for gravity or other acceleration loading
    GRAV SID CID A     N1  N2 N3    MB
    GRAV 1   3   32.2 0.0 0.0 -1.0
    """
    type = 'GRAV'
    def __init__(self,card):
        #BaseCard.__init__(self,card)
        self.sid  = card.field(1)
        self.cid  = card.field(2,0)
        self.a    = card.field(3)
        self.N    = card.fields(4,7,[0.,0.,0.]) # measured in cid
        assert max(self.N) != min(self.N)
        self.mb     = card.field(7,0)

    def __repr__(self):
        N = []
        for n in self.N:
            N.append(self.setBlankIfDefault(n,0.0))
        fields = ['GRAV',self.sid,self.cid,self.a]+N+[self.mb]
        return self.printCard(fields)

class FLUTTER(BaseCard):
    """
    Defines data needed to perform flutter analysis.
    FLUTTER SID METHOD DENS MACH RFREQ IMETH NVALUE/OMAX EPS
    FLUTTER 19  K      119  219  319       S 5           1.-4
    """
    type = 'FLUTTER'
    def __init__(self,card):
        #BaseCard.__init__(self,card)
        self.sid      = card.field(1)
        self.method   = card.field(2)
        assert self.method in ['K','PK','PKNL','PKS','PKNLS','KE']
        self.density  = card.field(3)
        self.mach     = card.field(4)
        self.rfreqVel = card.field(5)

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

    def _reprNValueOMax(self):
        if self.method in ['K','KE']:
            imethod = self.setBlankIfDefault(self.imethod,'L')
            return (imethod,self.nValue)
            assert self.imethod in ['L','S']
        elif self.method in ['PKS','PKNLS']:
            return(self.imethod,self.omax)
        else:
            return(self.imethod,self.nValue)
        raise Exception('unsupported...FLUTTER...')

    def __repr__(self):
        (imethod,nValue) = self._reprNValueOMax()
        fields = ['FLUTTER',self.sid,self.method,self.density,self.mach,self.rfreqVel,imethod,nValue,self.epsilon]
        return self.printCard(fields)