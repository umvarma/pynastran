from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
import unittest
from numpy import array

from pyNastran.bdf.bdf import PCOMP, MAT1

class TestShells(unittest.TestCase):
    def test_PCOMP_01(self):
        """
        asymmetrical, nsm=0.0 and nsm=1.0
        """
        #self.pid = data[0]
        #self.z0 = data[1]
        #self.nsm = data[2]
        #self.sb = data[3]
        #self.ft = data[4]
        #self.TRef = data[5]
        #self.ge = data[6]
        #self.lam = data[7]
        #Mid = data[8]
        #T = data[9]
        #Theta = data[10]
        #Sout = data[11]

        pid = 1
        z0 = 0.
        nsm = 0.
        sb = 0.
        ft = 0.
        TRef = 0.
        ge = 0.
        lam = 'NO'  # isSymmetrical YES/NO
        Mid = [1,2,3]
        Theta = [0.,10.,20.]
        T = [.1,.2,.3]
        Sout = [1, 1, 0]  # 0-NO, 1-YES
        data = [pid, z0, nsm, sb, ft, TRef, ge, lam, Mid, T, Theta, Sout]
        
        p = PCOMP(data=data)
        self.assertFalse(p.isSymmetrical())
        self.assertEquals(p.nPlies(), 3)

        self.assertAlmostEquals(p.Thickness(), 0.6)
        self.assertAlmostEquals(p.Thickness(0), 0.1)
        self.assertAlmostEquals(p.Thickness(1), 0.2)
        self.assertAlmostEquals(p.Thickness(2), 0.3)
        with self.assertRaises(RuntimeError):
            p.Thickness(3)

        self.assertAlmostEquals(p.Theta(0), 0.)
        self.assertAlmostEquals(p.Theta(1), 10.)
        self.assertAlmostEquals(p.Theta(2), 20.)
        with self.assertRaises(RuntimeError):
            p.Theta(3)
        
        self.assertEquals(p.Mid(0), 1)
        self.assertEquals(p.Mid(1), 2)
        self.assertEquals(p.Mid(2), 3)
        with self.assertRaises(RuntimeError):
            p.Mid(3)

        self.assertEquals(p.Mids(), [1,2,3])

        self.assertEquals(p.sout(0), 'YES')
        self.assertEquals(p.sout(1), 'YES')
        self.assertEquals(p.sout(2), 'NO')
        with self.assertRaises(RuntimeError):
            p.sout(3)

        # material...
        #self.mid = data[0]
        #self.e = data[1]
        #self.g = data[2]
        #self.nu = data[3]
        #self.rho = data[4]
        #self.a = data[5]
        #self.TRef = data[6]
        #self.ge = data[7]
        #self.St = data[8]
        #self.Sc = data[9]
        #self.Ss = data[10]
        #self.Mcsid = data[11]
        mid = 1
        E = None
        G = None
        nu = None
        rho = 1.0
        a = None
        St = None
        Sc = None
        Ss = None
        Mcsid = None
        mat1 = [mid,E,G,nu,rho,a,TRef, ge, St, Sc, Ss, Mcsid]
        m = MAT1(data=mat1)
        for iply in xrange(len(p.plies)):
            mid = p.plies[iply][0]
            p.plies[iply][0] = m # MAT1
            #p.mids = [m, m, m]
        
        #Rho
        self.assertAlmostEquals(p.Rho(0), 1.0)
        self.assertAlmostEquals(p.Rho(1), 1.0)
        self.assertAlmostEquals(p.Rho(2), 1.0)
        with self.assertRaises(RuntimeError):
            p.Rho(3)

        # MassPerArea
        self.assertAlmostEquals(p.MassPerArea(), 0.6)
        self.assertAlmostEquals(p.MassPerArea(0), 0.1)
        self.assertAlmostEquals(p.MassPerArea(1), 0.2)
        self.assertAlmostEquals(p.MassPerArea(2), 0.3)
        with self.assertRaises(RuntimeError):
            p.MassPerArea(3)

        #----------------------
        # change the nsm to 1.0
        p.nsm = 1.0

        self.assertEquals(p.Nsm(), 1.0)
        # MassPerArea
        self.assertAlmostEquals(p.MassPerArea(), 1.6)
        self.assertAlmostEquals(p.MassPerArea(0, method='nplies'), 0.1+1/3.)
        self.assertAlmostEquals(p.MassPerArea(1, method='nplies'), 0.2+1/3.)
        self.assertAlmostEquals(p.MassPerArea(2, method='nplies'), 0.3+1/3.)

        self.assertAlmostEquals(p.MassPerArea(0, method='rho*t'), 0.1+1/6.)
        self.assertAlmostEquals(p.MassPerArea(1, method='rho*t'), 0.2+2/6.)
        self.assertAlmostEquals(p.MassPerArea(2, method='rho*t'), 0.3+3/6.)

        self.assertAlmostEquals(p.MassPerArea(0, method='t'), 0.1+1/6.)
        self.assertAlmostEquals(p.MassPerArea(1, method='t'), 0.2+2/6.)
        self.assertAlmostEquals(p.MassPerArea(2, method='t'), 0.3+3/6.)
        with self.assertRaises(RuntimeError):
            p.MassPerArea(3, method='nplies')
        
        z = p.get_z_locations()
        z_expected = array([0., T[0], T[0]+T[1], T[0]+T[1]+T[2]])
        for za, ze in zip(z, z_expected):
            self.assertAlmostEquals(za, ze)
        
        #z0  = 
        p.z0 = 1.0
        z_expected = 1.0 + z_expected
        z = p.get_z_locations()
        for za, ze in zip(z, z_expected):
            self.assertAlmostEquals(za, ze)

    def test_PCOMP_02(self):
        """
        symmetrical, nsm=0.0 and nsm=1.0
        """
        pid = 1
        z0 = 0.
        nsm = 0.
        sb = 0.
        ft = 0.
        TRef = 0.
        ge = 0.
        lam = 'SYM'  # isSymmetrical SYM
        Mid = [1,2,3]
        Theta = [0.,10.,20.]
        T = [.1,.2,.3]
        Sout = [1, 1, 0]  # 0-NO, 1-YES
        data = [pid, z0, nsm, sb, ft, TRef, ge, lam, Mid, T, Theta, Sout]
        p = PCOMP(data=data)
        self.assertTrue(p.isSymmetrical())
        self.assertEquals(p.nPlies(), 6)
        
        self.assertAlmostEquals(p.Thickness(), 1.2)
        self.assertAlmostEquals(p.Thickness(0), 0.1)
        self.assertAlmostEquals(p.Thickness(1), 0.2)
        self.assertAlmostEquals(p.Thickness(2), 0.3)
        self.assertAlmostEquals(p.Thickness(3), 0.1)
        self.assertAlmostEquals(p.Thickness(4), 0.2)
        self.assertAlmostEquals(p.Thickness(5), 0.3)
        with self.assertRaises(RuntimeError):
            p.Thickness(6)

        self.assertAlmostEquals(p.Theta(0), 0.)
        self.assertAlmostEquals(p.Theta(1), 10.)
        self.assertAlmostEquals(p.Theta(2), 20.)
        self.assertAlmostEquals(p.Theta(3), 0.)
        self.assertAlmostEquals(p.Theta(4), 10.)
        self.assertAlmostEquals(p.Theta(5), 20.)
        with self.assertRaises(RuntimeError):
            p.Theta(6)
        
        self.assertEquals(p.Mid(0), 1)
        self.assertEquals(p.Mid(1), 2)
        self.assertEquals(p.Mid(2), 3)
        self.assertEquals(p.Mid(3), 1)
        self.assertEquals(p.Mid(4), 2)
        self.assertEquals(p.Mid(5), 3)
        with self.assertRaises(RuntimeError):
            p.Mid(6)

        self.assertEquals(p.Mids(), [1,2,3,1,2,3])

        self.assertEquals(p.sout(0), 'YES')
        self.assertEquals(p.sout(1), 'YES')
        self.assertEquals(p.sout(2), 'NO')
        self.assertEquals(p.sout(3), 'YES')
        self.assertEquals(p.sout(4), 'YES')
        self.assertEquals(p.sout(5), 'NO')
        with self.assertRaises(RuntimeError):
            p.sout(6)


        mid = 1
        E = None
        G = None
        nu = None
        rho = 1.0
        a = None
        St = None
        Sc = None
        Ss = None
        Mcsid = None
        mat1 = [mid,E,G,nu,rho,a,TRef, ge, St, Sc, Ss, Mcsid]
        m = MAT1(data=mat1)
        for iply in xrange(len(p.plies)):
            mid = p.plies[iply][0]
            p.plies[iply][0] = m # MAT1

        #Rho
        self.assertAlmostEquals(p.Rho(0), 1.0)
        self.assertAlmostEquals(p.Rho(1), 1.0)
        self.assertAlmostEquals(p.Rho(2), 1.0)
        self.assertAlmostEquals(p.Rho(3), 1.0)
        self.assertAlmostEquals(p.Rho(4), 1.0)
        self.assertAlmostEquals(p.Rho(5), 1.0)
        with self.assertRaises(RuntimeError):
            p.Rho(6)

        # MassPerArea
        self.assertAlmostEquals(p.MassPerArea(), 1.2)
        self.assertAlmostEquals(p.MassPerArea(0), 0.1)
        self.assertAlmostEquals(p.MassPerArea(1), 0.2)
        self.assertAlmostEquals(p.MassPerArea(2), 0.3)
        self.assertAlmostEquals(p.MassPerArea(3), 0.1)
        self.assertAlmostEquals(p.MassPerArea(4), 0.2)
        self.assertAlmostEquals(p.MassPerArea(5), 0.3)
        with self.assertRaises(RuntimeError):
            p.MassPerArea(6)
        
        self.assertEquals(p.Nsm(), 0.0)
        #----------------------
        # change the nsm to 1.0
        p.nsm = 1.0

        self.assertEquals(p.Nsm(), 1.0)
        # MassPerArea
        self.assertAlmostEquals(p.MassPerArea(), 2.2)
        self.assertAlmostEquals(p.MassPerArea(0, method='nplies'), 0.1+1/6.)
        self.assertAlmostEquals(p.MassPerArea(1, method='nplies'), 0.2+1/6.)
        self.assertAlmostEquals(p.MassPerArea(2, method='nplies'), 0.3+1/6.)
        self.assertAlmostEquals(p.MassPerArea(3, method='nplies'), 0.1+1/6.)
        self.assertAlmostEquals(p.MassPerArea(4, method='nplies'), 0.2+1/6.)
        self.assertAlmostEquals(p.MassPerArea(5, method='nplies'), 0.3+1/6.)
        with self.assertRaises(RuntimeError):
            p.MassPerArea(6)        

if __name__ == '__main__':
    unittest.main()