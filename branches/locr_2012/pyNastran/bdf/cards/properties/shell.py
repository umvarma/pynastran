#pylint: disable=C0103,C0111
"""
All shell properties are defined in this file.  This includes:
 * PCOMP
 * PCOMPG
 * PSHEAR
 * PSHELL

All shell properties are ShellProperty and Property objects.
"""
from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
#import sys
from itertools import izip

from pyNastran.bdf.fieldWriter import set_blank_if_default
from pyNastran.bdf.cards.baseCard import Property, Material

    
class ShellProperty(Property):
    type = 'ShellProperty'

    def __init__(self, card=None, data=None):
        Property.__init__(self, card, data)



class PCOMP(ShellProperty):
    """
    @code
    PCOMP     701512   0.0+0 1.549-2                   0.0+0   0.0+0     SYM
              300704   3.7-2   0.0+0     YES  300704   3.7-2     45.     YES
              300704   3.7-2    -45.     YES  300704   3.7-2     90.     YES
              300705      .5   0.0+0     YES
    @endcode
    """
    type = 'PCOMP'

    def __init__(self, card=None, data=None):  # not done, cleanup
        ShellProperty.__init__(self, card, data)

        if card:
            ## Property ID
            self.pid = card.field(1)
            ## Non-Structural Mass
            self.nsm = card.field(3, 0.0)
            self.sb = card.field(4, 0.0)
            self.ft = card.field(5)
            self.TRef = card.field(6, 0.0)
            self.ge = card.field(7, 0.0)

            ## symmetric flag - default = No Symmetry (NO)
            self.lam = card.field(8)

            # -8 for the first 8 fields (1st line)
            nPlyFields = card.nFields() - 9

            # counting plies
            nMajor = nPlyFields // 4
            nLeftover = nPlyFields % 4
            if nLeftover:
                nMajor += 1
            nplies = nMajor
            #print "nplies = ",nplies

            plies = []
            midLast = None
            tLast = None
            ply = None
            iPly = 1
            ## supports single ply per line
            for i in xrange(9, 9 + nplies * 4, 4):
                defaults = [midLast, tLast, 0.0, 'NO']
                actual = card.fields(i, i + 4)
                (mid, t, theta, sout) = card.fields(i, i + 4, defaults)

                if not t > 0.:
                    msg = ('thickness of PCOMP layer is invalid pid=%s'
                           ' iLayer=%s t=%s ply=[mid,t,theta,'
                           'sout]=%s' % (self.pid, iPly, t, ply))
                    raise RuntimeError(msg)

                # if this card has 2 plies on the line
                if actual != [None, None, None, None]:
                    ply = [mid, t, theta, sout]
                    plies.append(ply)
                    iPly += 1
                midLast = mid
                tLast = t
            #print "nplies = ",nplies

            ## list of plies
            self.plies = plies

            #self.plies = []
            #if self.lam == 'SYM':
            #    if nplies%2 == 1:  # 0th layer is the core layer
            #       # cut the thickness in half to make the ply have an
            #       # even number of plies, is there a better way???
            #       plies[0][1] = plies[0][1]/2.
            #
            #    pliesLower = plies.reverse()
            #    self.plies = pliesLower+plies
            #    #print str(self)
            self.z0 = card.field(2, -0.5 * self.Thickness())
        else:
            #print "len(data) = ",len(data)
            self.pid = data[0]
            self.z0 = data[1]
            self.nsm = data[2]
            self.sb = data[3]
            self.ft = data[4]
            self.TRef = data[5]
            self.ge = data[6]
            self.lam = data[7]
            Mid = data[8]
            T = data[9]
            Theta = data[10]
            Sout = data[11]

            self.plies = []
            #ply = [mid,t,theta,sout]
            for (mid, t, theta, sout) in izip(Mid, T, Theta, Sout):
                if sout == 1:  # TODO not sure  0=NO,1=YES (most likely)
                    sout = 'YES'
                elif sout == 0:
                    sout = 'NO'
                else:
                    raise RuntimeError('unsupported sout...needs debugging...'
                                       '\nPCOMP = %s' % data)
                self.plies.append([mid, t, theta, sout])

    def hasCoreLayer(self):
        """is there a center layer (matters most for a symmetrical ply)"""
        return self.nPlies() % 2 == 1  # True if has a core, False otherwise

    def nPlies(self):
        """
        returns the number of plies including the core
        @code
        if Lam=SYM:
          returns nPlies*2   (even)
          returns nPlies*2-1 (odd)
        else:
          returns nPlies
        @endcode
        """
        nPlies = len(self.plies)
        if self.isSymmetrical():
            if nPlies % 2 == 0:
                return nPlies * 2
            return nPlies * 2 - 1
        return nPlies

    def isSymmetrical(self):
        """is the laminate symmetrical"""
        if self.lam == 'SYM':
            return True
        return False

    def isSameCard(self, prop, debug=False):
        if self.type != prop.type:
            return False
        fields2 = [prop.nsm, prop.sb, prop.ft, prop.TRef, prop.ge, prop.lam]
        fields1 = [self.nsm, self.sb, self.ft, self.TRef, self.ge, self.lam]

        for ply in self.plies:
            fields1 += ply
        for ply in prop.plies:
            fields2 += ply

        if debug:
            print("fields1=%s fields2=%s" % (fields1, fields2))

        for (field1, field2) in izip(fields1, fields2):
            if not self.isSame(field1, field2):
                return False
        return True

    def cross_reference(self, model):
        """
        links the material ID to the materials
        @param self the object pointer
        @param model a BDF object
        """
        for iPly in xrange(len(self.plies)):
            mid = self.plies[iPly][0]
            self.plies[iPly][0] = model.Material(mid)  # mid

    def Nsm(self):
        return self.nsm

    def Mid(self, iPly):
        """
        gets the material ID of the ith ply
        @param self the object pointer
        @param iPly the ply ID (starts from 0)
        """
        Mid = self.Material(iPly)
        if isinstance(Mid, int):
            return Mid
        return Mid.mid

    def Mids(self):
        """
        gets the material IDs of all the plies
        @param self the object pointer
        @retval mids the material IDs
        """
        mids = []
        for iPly in xrange(len(self.plies)):
            mids.append(self.Mid(iPly))
        return mids

    def Rho(self, iPly):
        """
        gets the density of the ith ply
        @param self the object pointer
        @param iPly the ply ID (starts from 0)
        """
        mid = self.Material(iPly)
        return mid.rho

    def Material(self, iPly):
        """
        gets the material of the ith ply (not the ID unless it's not
        cross-referenced)
        @param self the object pointer
        @param iPly the ply ID (starts from 0)
        """
        Mid = self.plies[iPly][0]
        return Mid

    def Thickness(self, iPly='all'):
        """
        gets the thickness of the ith ply
        @param self the object pointer
        @param iPly the string 'all' (default) or the mass per area of the ith
         ply
        """
        if iPly == 'all':  # get all layers
            t = 0.
            for iply in xrange(len(self.plies)):
                t += self.Thickness(iply)

            if self.isSymmetrical():
                return t * 2.
            return t
        else:
            t = self.plies[iPly][1]
            return t

    def Theta(self, iPly):
        """
        Gets the ply angle of the ith ply (not the ID)
        @param self the object pointer
        @param iPly the ply ID (starts from 0)
        """
        Theta = self.plies[iPly][2]
        return Theta

    def sout(self, iPly):
        Sout = self.plies[iPly][3]
        return Sout

    def MassPerArea(self, iPly='all'):
        r"""
        \f[ \large  m = A ( \rho t + nsm ) \f]
        mass = rho*A*t
        but area comes from the element, so:
        \f[ \large  \frac{m}{A} =\rho t + nsm \f]
        mass/A = rho*t for the various layers
        the final mass calculation will be done later
        @param self
          the PCOMP object
        @param iPly
          the string 'all' (default) or the mass per area of the ith ply
        """
        if iPly == 'all':  # get all layers
            massPerArea = 0.
            nplies = len(self.plies)
            for iply in xrange(nplies):
                rho = self.Rho(iply)
                t = self.plies[iply][1]
                massPerArea += rho * t

            if self.isSymmetrical():
                return 2. * massPerArea + self.nsm
            return massPerArea + self.nsm
        else:
            rho = self.Rho(iPly)
            t = self.plies[iPly][1]
            return rho * t + self.nsm

    def rawFields(self):
        fields = ['PCOMP', self.pid, self.z0, self.nsm, self.sb, self.ft,
                  self.TRef, self.ge, self.lam, ]
        for (iPly, ply) in enumerate(self.plies):
            (_mid, t, theta, sout) = ply
            mid = self.Mid(iPly)
            fields += [mid, t, theta, sout]
        return fields

    def reprFields(self):
        nsm = set_blank_if_default(self.nsm, 0.0)
        sb = set_blank_if_default(self.sb, 0.0)
        TRef = set_blank_if_default(self.TRef, 0.0)
        ge = set_blank_if_default(self.ge, 0.0)
        z0 = set_blank_if_default(self.z0, -0.5 * self.Thickness())

        fields = ['PCOMP', self.pid, z0, nsm, sb, self.ft, TRef, ge, self.lam]
        for (iPly, ply) in enumerate(self.plies):
            (_mid, t, theta, sout) = ply
            mid = self.Mid(iPly)
            #theta = set_blank_if_default(theta,0.0)
            sout = set_blank_if_default(sout, 'NO')
            fields += [mid, t, theta, sout]
        return fields


class PCOMPG(PCOMP):
    type = 'PCOMPG'

    def __init__(self, card=None, data=None):
        ShellProperty.__init__(self, card, data)
        if card:
            self.pid = card.field(1)
            # z0 will be calculated later
            self.nsm = card.field(3, 0.0)
            self.sb = card.field(4, 0.0)
            self.ft = card.field(5)
            self.TRef = card.field(6, 0.0)
            self.ge = card.field(7, 0.0)
            self.lam = card.field(8)
            fields = card.fields(9)

            T = 0.  # thickness
            midLast = None
            tLast = None
            self.plies = []

            i = 0
            n = 0
            while i < len(fields):
                gPlyID = card.field(9 + i)
                mid = card.field(9 + i + 1, midLast)

                # can be blank 2nd time thru
                thickness = card.field(9 + i + 2, tLast)

                theta = card.field(9 + i + 3, 0.0)
                sout = card.field(9 + i + 4, 'NO')
                #print('n=%s gPlyID=%s mid=%s thickness=%s len=%s' %(
                #    n,gPlyID,mid,thickness,len(fields)))

                ply = [mid, thickness, theta, sout, gPlyID]
                #print("ply = %s" %(ply))
                self.plies.append(ply)
                #[mid,t,theta,sout] # PCOMP

                assert mid is not None
                assert thickness is not None
                assert isinstance(mid, int), 'mid=%s' % mid
                assert isinstance(thickness, float), 'thickness=%s' % thickness
                midLast = mid
                tLast = thickness
                T += thickness
                i += 8
                n += 1
                self.z0 = card.field(2, -0.5 * T)
        else:
            raise NotImplementedError('PCOMPG data')

    def GlobalPlyID(self, iPly):
        gPlyID = self.plies[iPly][4]
        return gPlyID

    def rawFields(self):
        fields = ['PCOMPG', self.pid, self.z0, self.nsm, self.sb, self.ft,
                  self.TRef, self.ge, self.lam, ]
        for (iPly, ply) in enumerate(self.plies):
            (_mid, t, theta, sout, gPlyID) = ply
            mid = self.Mid(iPly)
            fields += [gPlyID, mid, t, theta, sout, None, None, None]
        return fields

    def reprFields(self):
        nsm = set_blank_if_default(self.nsm, 0.0)
        sb = set_blank_if_default(self.sb, 0.0)
        TRef = set_blank_if_default(self.TRef, 0.0)
        ge = set_blank_if_default(self.ge, 0.0)
        z0 = set_blank_if_default(self.z0, -0.5 * self.Thickness())

        fields = ['PCOMPG', self.pid, z0, nsm, sb, self.ft, TRef, ge, self.lam]

        for (iPly, ply) in enumerate(self.plies):
            (_mid, t, theta, sout, gPlyID) = ply
            mid = self.Mid(iPly)
            #theta = set_blank_if_default(theta,0.0)
            sout = set_blank_if_default(sout, 'NO')
            fields += [gPlyID, mid, t, theta, sout, None, None, None]
        return fields


class PSHEAR(ShellProperty):
    type = 'PSHEAR'

    def __init__(self, card=None, data=None):
        """
        Defines the properties of a shear panel (CSHEAR entry).
        PSHEAR PID MID T NSM F1 F2
        """
        ShellProperty.__init__(self, card, data)
        if card:
            ## Property ID
            self.pid = card.field(1)
            ## Material ID
            self.mid = card.field(2)
            self.t = card.field(3)
            self.nsm = card.field(4, 0.0)
            self.f1 = card.field(5, 0.0)
            self.f2 = card.field(6, 0.0)
        else:
            #(pid,mid,t,nsm,f1,f2) = out
            self.pid = data[0]
            self.mid = data[1]
            self.t = data[2]
            self.nsm = data[3]
            self.f1 = data[4]
            self.f2 = data[5]

    def isSameCard(self, prop, debug=False):
        if self.type != prop.type:
            return False
        fields1 = self.rawFields()
        fields2 = prop.rawFields()
        if debug:
            print("fields1=%s fields2=%s" % (fields1, fields2))
        return self.isSameFields(fields1, fields2)

    def rawFields(self):
        fields = ['PSHEAR', self.pid, self.Mid(), self.t, self.nsm,
                  self.f1, self.f2]
        return fields


class PSHELL(ShellProperty):
    """
    PSHELL PID MID1 T MID2 12I/T**3 MID3 TS/T NSM
    Z1 Z2 MID4
    PSHELL   41111   1      1.0000   1               1               0.02081"""
    type = 'PSHELL'

    def __init__(self, card=None, data=None):
        ShellProperty.__init__(self, card, data)
        if card:
            self.pid = int(card.field(1))
            self.mid1 = card.field(2)
            self.t = card.field(3)

            ## Material identification number for bending
            self.mid2 = card.field(4)
            ## \f$ \frac{12I}{t^3} \f$
            self.twelveIt3 = card.field(5, 1.0)  # poor name
            self.mid3 = card.field(6)
            self.tst = card.field(7, 0.833333)
            self.nsm = card.field(8, 0.0)

            tOver2 = self.t / 2.
            self.z1 = card.field(9, -tOver2)
            self.z2 = card.field(10, tOver2)
            self.mid4 = card.field(11)
            #if self.mid2 is None:
            #    assert self.mid3 is None
            #else: # mid2 is defined
            #    #print "self.mid2 = ",self.mid2
            #    assert self.mid2 >= -1
            #    #assert self.mid3 >   0

            #if self.mid is not None and self.mid2 is not None:
            #    assert self.mid4==None
        else:
            self.pid = data[0]
            self.mid1 = data[1]
            self.t = data[2]
            self.mid2 = data[3]
            self.twelveIt3 = data[4]
            self.mid3 = data[5]
            self.tst = data[6]
            self.nsm = data[7]
            self.z1 = data[8]
            self.z2 = data[9]
            self.mid4 = data[10]
            #maxMid = max(self.mid,self.mid2,self.mid3,self.mid4)

        assert self.t > 0.0, ('the thickness must be defined on the PSHELL'
                              ' card (Ti field not supported)')

    def mid(self):
        if isinstance(self.mid1, Material):
            return self.mid1
        return self.mid2

    def Mid(self):
        if isinstance(self.mid1, Material):
            return self.mid1.mid  # self.Mid1()
        return self.Mid2()

    def Mid1(self):
        if isinstance(self.mid1, Material):
            return self.mid1.mid
        return self.mid1

    def Mid2(self):
        if isinstance(self.mid2, Material):
            return self.mid2.mid
        return self.mid2

    def Mid3(self):
        if isinstance(self.mid3, Material):
            return self.mid3.mid
        return self.mid3

    def Mid4(self):
        if isinstance(self.mid4, Material):
            return self.mid4.mid
        return self.mid4

    def Thickness(self):
        return self.t

    def Rho(self):
        return self.mid().rho

    def Nsm(self):
        return self.nsm

    def MassPerArea(self):
        r"""
        calculates mass per area
        \f[ \large  \frac{mass}{A} = nsm + \rho t \f]
        """
        try:
            massPerArea = self.nsm + self.Rho() * self.t
        except:
            print("nsm=%s rho=%s t=%s" % (self.nsm, self.Rho(), self.t))
            raise
        return massPerArea

    def D(self):
        return self.mid().Dplate()

    def cross_reference(self, model):
        if self.mid1:
            self.mid1 = model.Material(self.mid1)
        if self.mid2 and self.mid2 != -1:
            self.mid2 = model.Material(self.mid2)
        if self.mid3:
            self.mid3 = model.Material(self.mid3)
        if self.mid4:
            self.mid4 = model.Material(self.mid4)

    def writeCalculix(self, marker='markerDummyProp',
                      elementSet='ELsetDummyProp'):
        msg = '*SHELL SECTION,MATERIAL=M%s_%s,ELSET=%s,OFFSET=%s\n' % (
            marker, self.mid, elementSet, self.z1)
        msg += '** THICKNESS\n'
        msg += '%s\n\n' % (self.t)
        return msg

    def writeCodeAster(self):
        """
        * http://www.caelinux.org/wiki/index.php/Contrib:KeesWouters/shell/static
        * http://www.caelinux.org/wiki/index.php/Contrib:KeesWouters/platedynamics
        
        the angle_rep is a direction angle, use either angle(a,b) or
        vecteur(x,y,z)
        coque_ncou is the number of gauss nodes along the thickness, for
        linear analysis one node is sufficient.
        """
        msg = ''
        msg += "    COQUE=_F(GROUP_MA='P%s', # COQUE=PSHELL\n" % self.pid
        msg += "              EPAIS=%g, # EPAIS=thickness\n" % self.t
        msg += "              ANGL_REP=(0.,90.),  # ???\n"  # TODO what is this?
        #msg += "              VECTEUR=(1.0,0.0,0.0,)  #  local coordinate system\n"
        msg += "              EXCENTREMENT=%g,  # offset-Z1\n" % self.z1
        msg += "              COQUE_NCOU=1,  # Number of Integration Layers\n"
        msg += "              CARA=('NSM'), # ???\n"  # TODO check
        msg += "              VALE=(%g),),\n" % self.nsm
        return msg

    def rawFields(self):
        fields = ['PSHELL', self.pid, self.Mid1(), self.t, self.Mid2(),
                  self.twelveIt3, self.Mid3(), self.tst, self.nsm, self.z1,
                  self.z2, self.Mid4()]
        return fields

    def reprFields(self):
        twelveIt3 = set_blank_if_default(self.twelveIt3, 1.0)
        tst = set_blank_if_default(self.tst, 0.833333)
        nsm = set_blank_if_default(self.nsm, 0.0)

        tOver2 = self.t / 2.
        z1 = set_blank_if_default(self.z1, -tOver2)
        z2 = set_blank_if_default(self.z2, tOver2)

        fields = ['PSHELL', self.pid, self.Mid1(), self.t, self.Mid2(),
                  twelveIt3, self.Mid3(), tst, nsm, z1, z2, self.Mid4()]
        return fields