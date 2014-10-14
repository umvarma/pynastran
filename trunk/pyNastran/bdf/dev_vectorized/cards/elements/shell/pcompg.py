from numpy import array, zeros, arange, concatenate, searchsorted, where, unique

from pyNastran.bdf.fieldWriter import print_card
from pyNastran.bdf.bdfInterface.assign_type import (integer, integer_or_blank,
    double_or_blank, integer_double_or_blank, blank)


class PCOMPG(object):
    type = 'PCOMPG'
    def __len__(self):
        return self.n

    def __init__(self, model):
        self.n = 0

    def add(self, card, comment):
        pass

    def build(self):
        self.property_id = array([], dtype='int32')

    def write_bdf(self, f, size=8, property_ids=None):
        pass

    def __repr__(self):
        asdf
