from numpy import array, zeros, argsort, concatenate, searchsorted, unique, where, nan, arange

from pyNastran.bdf.fieldWriter import print_card
from pyNastran.bdf.bdfInterface.assign_type import (integer, integer_or_blank, double,
    double_or_blank, string_or_blank)


class PropertiesShell(object):
    def __init__(self, model):
        """
        Defines the ShellProperties object.

        :param self: the ShellProperties object
        :param model: the BDF object
        """
        self.model = model

        #: the list of PSHELL cards
        self._pshell = []

        #: the list of PCOMP cards
        self._pcomp = []

        #: the list of PSHEAR cards
        self._pshear = []

        self._pshell_comment = []
        self._pcomp_comment = []
        self._pshear_comment = []

    def build(self):
        self.pshell = PSHELL(self.model, self._pshell)
        self.pcomp = PCOMP(self.model, self._pcomp)
        self.pshear = PSHEAR(self.model, self._pshear)
        
        self._pshell = []
        self._pcomp = []
        self._pshear = []

        self._pshell_comment = []
        self._pcomp_comment = []
        self._pshear_comment = []

        npcomp = len(self.pcomp.pid)
        npshell = len(self.pshell.pid)
        npshear = len(self.pshear.pid)
        
        if npshell and npcomp and pshear:
            asf
        elif npshell and npcomp:
            pid = concatenate(self.pshell.pid, self.pcomp.pid)
            unique_pids = unique(pid)
            print unique_pids
            if len(unique_pids) != len(pid):
                raise RuntimeError('There are duplicate PSHELL/PCOMP IDs...')
        else:
            pass

    def rebuild(self):
        raise NotImplementedError()

    def add_pshell(self, card, comment):
        self._pshell.append(card)
        self._pshell_comment.append(comment)

    def add_pcomp(self, card, comment):
        self._pcomp.append(card)
        self._pcomp_comment.append(comment)

    def add_pshear(self, card, comment):
        self._pshear.append(card)
        self._pshear_comment.append(comment)

    def get_stats(self):
        msg = []
        types = [self.pshell, self.pcomp, self.pshear]
        for prop in types:
            nprop = len(prop.pid)
            if nprop:
                msg.append('  %-8s: %i' % (prop.type, nprop))
        return msg

    def get_thickness(self, pids):
        """
        Gets the thickness of the PSHELLs/PCOMPs.
        
        :param self: the ShellProperties object
        :param pids: the property IDs to consider (default=None -> all)
        """
        _pids = concatenate(self.pshell.pid,
                           self.pcomp.pid)
        t = concatenate(self.pshell.get_thickness(),
                        self.pcomp.get_thickness() )
        i = argsort(_pids)
        
        t2 = t[searchsorted(pids, _pids)]
        return t2

    def write_bdf(self, f, size=8, pids=None):
        f.write('$PROPERTIES\n')
        self.pshell.write_bdf(f, size=size, pids=pids)
        self.pcomp.write_bdf(f, size=size, pids=pids)


class PCOMP(object):
    type = 'PCOMP'
    def __init__(self, model, cards):
        """
        Defines the PCOMP object.

        :param self: the PCOMP object
        :param model: the BDF object
        :param cards: the list of PCOMP cards
        """
        self.model = model

        ncards = len(cards)
        #: Property ID
        self.pid = zeros(ncards, 'int32')
        unique_pids = unique(self.pid)

        if len(unique_pids) != len(self.pid):
            raise RuntimeError('There are duplicate PSHELL IDs...')
        
    def write_bdf(self, f, size=8, pids=None):
        pass

class PSHEAR(object):
    type = 'PSHEAR'
    def __init__(self, model, cards):
        self.pid = []

    def build(self):
        pass

    def write_bdf(self, f, size=8, pids=None):
        pass

class PSHELL(object):
    type = 'PSHELL'
    def __init__(self, model, cards):
        """
        Defines the PSHELL object.

        :param self: the PSHELL object
        :param model: the BDF object
        :param cards: the list of PSHELL cards
        """
        self.model = model

        ncards = len(cards)
        #: Property ID
        self.pid = zeros(ncards, 'int32')
        self.mid = zeros(ncards, 'int32')
        self.thickness = zeros(ncards, 'float32')
        
        self.mid2 = zeros(ncards, 'int32')
        self.twelveIt3 = zeros(ncards, 'float32')
        self.mid3 = zeros(ncards, 'int32')

        self.tst = zeros(ncards, 'float64')
        self.nsm = zeros(ncards, 'float32')
        self.z1 = zeros(ncards, 'float32')
        self.z2 = zeros(ncards, 'float32')
        self.mid4 = zeros(ncards, 'int32')
        
        # ..todo:: incomplete
        for i, card in enumerate(cards):
            self.pid[i] = integer(card, 1, 'pid')
            self.mid[i] = integer(card, 2, 'mid')
            self.thickness[i] = double(card, 3, 'thickness')

            #: Material identification number for bending
            self.mid2[i] = integer_or_blank(card, 4, 'mid2', -1)
            #: Scales the moment of interia of the element based on the
            #: moment of interia for a plate
            #:
            #: ..math:: I = \frac{12I}{t^3} I_{plate}
            self.twelveIt3[i] = double_or_blank(card, 5, '12*I/t^3', 1.0)  # poor name
            self.mid3[i] = integer_or_blank(card, 6, 'mid3', -1)
            self.tst[i] = double_or_blank(card, 7, 'ts/t', 0.833333)
            #: Non-structural Mass
            self.nsm[i] = double_or_blank(card, 8, 'nsm', 0.0)

            tOver2 = self.thickness[i] / 2.
            self.z1[i] = double_or_blank(card, 9,  'z1', -tOver2)
            self.z2[i] = double_or_blank(card, 10, 'z2',  tOver2)
            self.mid4[i] = integer_or_blank(card, 11, 'mid4', -1)

            #if self.mid2 is None:
            #    assert self.mid3 is None
            #else: # mid2 is defined
            #    #print "self.mid2 = ",self.mid2
            #    assert self.mid2 >= -1
            #    #assert self.mid3 >   0

            #if self.mid is not None and self.mid2 is not None:
            #    assert self.mid4==None
            assert len(card) <= 12, 'len(PSHELL card) = %i' % len(card)

        # nan is float specific
        #self.mid[where(self.mid2 == -1)[0]] = nan

        i = self.mid.argsort()
        self.mid = self.mid[i]
        self.thickness = self.thickness[i]
        self.mid2 = self.mid2[i]
        self.twelveIt3 = self.twelveIt3[i]
        self.mid3 = self.mid3[i]
        self.tst = self.tst[i]
        self.nsm = self.nsm[i]
        self.z1 = self.z1[i]
        self.z2 = self.z2[i]
        self.mid4 = self.mid4[i]
        
        # sort the NDARRAYs so we can use searchsorted
        i = self.pid.argsort()
        self.pid = self.pid[i]
        self.mid = self.mid[i]
        self.thickness = self.thickness[i]
        
        if len(unique(self.pid)) != len(self.pid):
            raise RuntimeError('There are duplicate PSHELL IDs...')

    def write_bdf(self, f, size=8, pids=None):
        """
        Writes the PSHELL properties.
        
        :param self:  the PSHELL object
        :param f:     file object
        :param size:  the bdf field size (8/16; default=8)
        :param pids:  the pids to write (default=None -> all)
        """
        if pids is None:
            i = arange(len(self.mid))
            #for (pid, mid, t, mid2, twelveIt3, mid3, tst, nsm, z1, z2, mid4) in zip(
                    #self.pid, self.mid, self.thickness, self.mid2,
                    #self.twelveIt3, self.mid3, self.tst, self.nsm, self.z1,
                    #self.z2, self.mid4):
                #card = ['PSHELL', pid, mid, t]
                #f.write(print_card(card, size=size))
        else:
            i = searchsorted(self.pid, pids)

        Mid2 = [midi if midi > 0 else '' for midi in self.mid2[i]]
        Mid3 = [midi if midi > 0 else '' for midi in self.mid3[i]]
        Mid4 = [midi if midi > 0 else '' for midi in self.mid4[i]]
        Nsm       = ['' if nsmi == 0.0      else nsmi for nsmi in self.nsm[i]]
        Tst       = ['' if tsti == 0.833333 else tsti for tsti in self.tst[i]]
        TwelveIt3 = ['' if tw   == 1.0      else tw   for tw   in self.twelveIt3[i]]

        to2 = self.thickness[i] / 2
        Z1 = ['' if z1i == -to2[j] else z1i for j, z1i in enumerate(self.z1[i])]
        Z2 = ['' if z2i ==  to2[j] else z2i for j, z2i in enumerate(self.z2[i])]

        for (pid, mid, t, mid2, twelveIt3, mid3, tst, nsm, z1, z2, mid4) in zip(
                self.pid[i], self.mid[i], self.thickness[i], Mid2,
                TwelveIt3, Mid3, Tst, Nsm,  Z1, Z2, Mid4):
            card = ['PSHELL', pid, mid, t, mid2, twelveIt3, mid3,
                    tst, nsm, z1, z2, mid4]
            f.write(print_card(card, size=size))


    def get_thickness(self, pids=None):
        """
        Gets the thickness of the PHSELLs.
        
        :param self: the PSHELL object
        :param pids: the property IDs to consider (default=None -> all)
        """
        if pids is None:
            t = self.thickness
        else:
            t = self.thickness[searchsorted(pids, self.pid)]
        return t

    def get_mid(self, pids=None):
        """
        Gets the material IDs of the PSHELLs.
        
        :param self: the PSHELL object
        :param pids: the property IDs to consider (default=None -> all)
        """
        if pids is None:
            mid = self.mid
        else:
            mid = self.mid[searchsorted(pids, self.pid)]
        return t