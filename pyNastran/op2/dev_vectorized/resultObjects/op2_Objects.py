from __future__ import print_function
#from numpy import array
#from numpy import angle

from pyNastran.op2.op2Codes import Op2Codes
from pyNastran.utils import list_print


class BaseScalarObject(Op2Codes):
    def __init__(self):
        pass

    def name(self):
        return self.__class__.__name__

    def write_f06(self, header, pageStamp, f, pageNum=1, is_mag_phase=False):
        msg = 'write_f06 is not implemented in %s\n' % (
            self.__class__.__name__)
        f.write(msg)
        return pageNum

    def _write_f06_transient(self, header, pageStamp, f, pageNum=1,
                             is_mag_phase=False):
        msg = '_write_f06_transient is not implemented in %s\n' % (
            self.__class__.__name__)
        f.write(msg)
        return pageNum

    def __repr__(self):
        return ''.join(self.get_stats())

    def __str__(self):
        return self.__repr__()


class ScalarObject(BaseScalarObject):
    def __init__(self, data_code, isubcase, read_mode):
        assert 'nonlinear_factor' in data_code, data_code
        BaseScalarObject.__init__(self)
        self.isubcase = isubcase
        self.isTransient = False
        self.dt = None
        self.data_code = {}
        self.apply_data_code()

    def is_imaginary(self):
        return bool(self.sort_bits[1])

    def is_real(self):
        return not self.is_imaginary()

    def _apply_data_code(self):
        for key, value in sorted(self.data_code.iteritems()):
            self.__setattr__(key, value)
            #print("  *key=%s value=%s" % (key, value))
        #print("")

    def _get_data_code(self):
        msg = []
        if 'dataNames' not in self.data_code:
            return []

        for name in self.data_code['dataNames']:
            try:
                if hasattr(self, name + 's'):
                    vals = getattr(self, name + 's')
                    name = name + 's'
                else:
                    vals = getattr(self, name)
                msg.append('  %s = %s\n' % (name, list_print(vals)))
            except AttributeError:  # weird case...
                pass
        return msg

    def get_unsteady_value(self):
        name = self.data_code['name']
        return self.get_var(name)

    def get_var(self, name):
        return getattr(self, name)

    def set_var(self, name, value):
        return self.__setattr__(name, value)

    def _start_data_member(self, var_name, value_name):
        if hasattr(self, var_name):
            return True
        elif hasattr(self, value_name):
            self.set_var(var_name, [])
            return True
        return False

    def _append_data_member(self, varName, valueName):
        """
        this appends a data member to a variable that may or may not exist
        """
        hasList = self._start_data_member(varName, valueName)
        if hasList:
            listA = self.get_var(varName)
            if listA is not None:
                #print "has %s" % varName
                value = self.get_var(valueName)
                try:
                    n = len(listA)
                except:
                    print("listA = ", listA)
                    raise
                listA.append(value)
                assert len(listA) == n + 1

    def _set_data_members(self):
        if 'dataNames' not in self.data_code:
            msg = 'No "transient" variable was set for %s\n' % self.table_name
            raise NotImplementedError(msg + self.code_information())

        for name in self.data_code['dataNames']:
            #print("name = ", name)
            self._append_data_member(name + 's', name)

    def update_data_code(self, data_code):
        #print("self.data_code =", self.data_code)
        if not self.data_code or (data_code['nonlinear_factor'] != self.data_code['nonlinear_factor']):
            self.data_code = data_code
            self._apply_data_code()
            self._set_data_members()
        #else:
            #print('skipping update...')

    def print_data_members(self):
        """
        Prints out the "unique" vals of the case.
        Uses a provided list of data_code['dataNames'] to set the values for
        each subcase.  Then populates a list of self.name+'s' (by using
        setattr) with the current value.  For example, if the variable name is
        'mode', we make self.modes.  Then to extract the values, we build a
        list of of the variables that were set like this and then loop over
        then to print their values.

        This way there is no dependency on one result type having ['mode'] and
        another result type having ['mode','eigr','eigi'].
        """
        keyVals = []
        for name in self.data_code['dataNames']:
            vals = getattr(self, name + 's')
            keyVals.append(vals)
            #print("%ss = %s" % (name, vals))

        msg = ''
        for name in self.data_code['dataNames']:
            msg += '%-10s ' % name
        msg += '\n'

        nModes = len(keyVals[0])
        for i in xrange(nModes):
            for vals in keyVals:
                msg += '%-10g ' % vals[i]
            msg += '\n'
        return msg + '\n'

    def _recast_grid_type(self, grid_type):
        """converts a grid_type integer to a string"""
        if grid_type == 1:
            Type = 'G'  # GRID
        elif grid_type == 2:
            Type = 'S'  # SPOINT
        elif grid_type == 7:
            Type = 'L'  # RIGID POINT (e.g. RBE3)
        elif grid_type == 0:
            Type = 'H'      # SECTOR/HARMONIC/RING POINT
        else:
            raise RuntimeError('grid_type=%s' % grid_type)
        return Type

    def cast_grid_type(self, gridType):
        """converts a gridType integer to a string"""
        if grid_type == 'G':
            Type = 1  # GRID
        elif grid_type == 'S':
            Type = 2  # SPOINT
        elif grid_type == 'L':
            Type = 7  # RIGID POINT (e.g. RBE3)
        elif grid_type == 'H':
            Type = 0      # SECTOR/HARMONIC/RING POINT
        else:
            raise RuntimeError('gridType=%s' % grid_type)
        return Type

    def update_dt(self, data_code, dt):
        """
        this method is called if the object
        already exits and a new time step is found
        """
        self.data_code = data_code
        self.apply_data_code()
        raise RuntimeError('update_dt not implemented in the %s class'
                           % self.__class__.__name__)
        #assert dt>=0.
        #print "updating dt...dt=%s" %(dt)
        if dt is not None:
            self.dt = dt
            self.add_new_transient()