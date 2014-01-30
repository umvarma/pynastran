import os
import sys
from itertools import izip

from numpy import zeros

from pyNastran.utils import print_bad_path
from pyNastran.utils.log import get_logger

#ComplexEigenvalues,strainEnergyDensity,TemperatureGradientObject
from pyNastran.op2.tables.lama_eigenvalues.lama_objects import RealEigenvalues, ComplexEigenvalues


from pyNastran.f06.tables.oes import OES  # OES
from pyNastran.f06.tables.oug import OUG  # OUG
from pyNastran.f06.tables.oqg import OQG  # OUG
from pyNastran.f06.f06_classes import MaxDisplacement  # classes not in op2
from pyNastran.f06.f06Writer import F06Writer


class FatalError(RuntimeError):
    pass

class F06Deprecated(object):
    def readF06(self):
        """... seealso::: read_f06"""
        self.read_f06(self.f06_filename)


class F06(OES, OUG, OQG, F06Writer, F06Deprecated):
    def stop_after_reading_grid_point_weight(self, stop=True):
        self._stop_after_reading_mass = True

    def __init__(self, f06FileName, debug=False, log=None):
        """
        Initializes the F06 object

        :f06FileName: the file to be parsed
        :makeGeom:    reads the BDF tables (default=False)
        :debug:       prints data about how the F06 was parsed (default=False)
        :log:         a logging object to write debug messages to

        .. seealso:: import logging
        """
        self._subtitle = None
        self.card_count = {}
        self.f06FileName = f06FileName
        self.f06_filename = self.f06FileName
        self._stop_after_reading_mass = False

        if not os.path.exists(self.f06_filename):
            msg = 'cant find f06_filename=%r\n%s' % self.f06FileName, print_bad_path(self.f06_filename)
            raise RuntimeError(msg)
        self.infile = open(self.f06_filename, 'r')
        self.__init_data__(debug, log)

        self.lineMarkerMap = {
            'R E A L   E I G E N V E C T O R   N O': self._real_eigenvectors,
            'C O M P L E X   E I G E N V E C T O R   NO' : self._complex_eigenvectors,
            'News file -' : self._executive_control_echo,
        }
        self.markerMap = {
            #====================================================================
            # debug info
            'N A S T R A N    F I L E    A N D    S Y S T E M    P A R A M E T E R    E C H O' : self._nastran_file_and_system_parameter_echo,
            'N A S T R A N    E X E C U T I V E    C O N T R O L    E C H O':self._executive_control_echo,
            'C A S E    C O N T R O L    E C H O' : self._case_control_echo,
            'G R I D   P O I N T   S I N G U L A R I T Y   T A B L E': self._grid_point_singularity_table,

            # dummy
            'E L E M E N T   G E O M E T R Y   T E S T   R E S U L T S   S U M M A R Y': self._executive_control_echo,
            'M O D E L   S U M M A R Y':self._executive_control_echo,
            'M O D E L   S U M M A R Y          BULK = 0':self._executive_control_echo,
            'F O R C E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )' : self._grid_point_singularity_table,
            'G R I D   P O I N T   F O R C E   B A L A N C E' : self._executive_control_echo,
            'N A S T R A N   S O U R C E   P R O G R A M   C O M P I L A T I O N             SUBDMAP  =  SESTATIC' : self._executive_control_echo,
            #====================================================================
            # useful info
            #'E L E M E N T   G E O M E T R Y   T E S T   R E S U L T S   S U M M A R Y'
            'O U T P U T   F R O M   G R I D   P O I N T   W E I G H T   G E N E R A T O R': self._grid_point_weight_generator,

            # dummy
            'MAXIMUM  SPCFORCES':self.getMaxSpcForces,
            #'OLOAD    RESULTANT':self.getMaxMpcForces,
            'MAXIMUM  MPCFORCES':self.getMaxMpcForces,
            'SPCFORCE RESULTANT':self.getMaxMpcForces,
            'MPCFORCE RESULTANT':self.getMaxMpcForces,
            'MAXIMUM  DISPLACEMENTS': self.getMaxDisplacements,
            'MAXIMUM  APPLIED LOADS': self.getMaxAppliedLoads,


            #====================================================================
            # F06 specific tables
            #'N O N - D I M E N S I O N A L   S T A B I L I T Y   A N D   C O N T R O L   D E R I V A T I V E   C O E F F I C I E N T S' : self._nondimensional_stability_and_control_deriv_coeffs,
            #'N O N - D I M E N S I O N A L    H I N G E    M O M E N T    D E R I V A T I V E   C O E F F I C I E N T S':  self._nondimensional_hinge_moment_derivative_coeffs,
            #'A E R O S T A T I C   D A T A   R E C O V E R Y   O U T P U T   T A B L E S': self._aerostatic_data_recovery_output_tables,
            #'S T R U C T U R A L   M O N I T O R   P O I N T   I N T E G R A T E D   L O A D S': self._structural_monitor_point_integrated_loads,

            'N O N - D I M E N S I O N A L   S T A B I L I T Y   A N D   C O N T R O L   D E R I V A T I V E   C O E F F I C I E N T S' : self._executive_control_echo,
            'N O N - D I M E N S I O N A L    H I N G E    M O M E N T    D E R I V A T I V E   C O E F F I C I E N T S':  self._executive_control_echo,
            'A E R O S T A T I C   D A T A   R E C O V E R Y   O U T P U T   T A B L E S': self._executive_control_echo,
            'S T R U C T U R A L   M O N I T O R   P O I N T   I N T E G R A T E D   L O A D S': self._executive_control_echo,
            'FLUTTER  SUMMARY' : self._executive_control_echo,
            #------------------------
            #'R O T O R   D Y N A M I C S   S U M M A R Y'
            #'R O T O R   D Y N A M I C S   M A S S   S U M M A R Y'
            #'E I G E N V A L U E  A N A L Y S I S   S U M M A R Y   (COMPLEX LANCZOS METHOD)'

            'R O T O R   D Y N A M I C S   S U M M A R Y': self._executive_control_echo,
            'R O T O R   D Y N A M I C S   M A S S   S U M M A R Y': self._executive_control_echo,
            'E I G E N V A L U E  A N A L Y S I S   S U M M A R Y   (COMPLEX LANCZOS METHOD)': self._executive_control_echo,

            #------------------------
            #====================================================================

            # OUG tables
            'R E A L   E I G E N V A L U E S': self._real_eigenvalues,
            'C O M P L E X   E I G E N V A L U E   S U M M A R Y':self._complex_eigenvalue_summary,

            'E L E M E N T   S T R A I N   E N E R G I E S': self._element_strain_energies,
            'D I S P L A C E M E N T   V E C T O R': self._displacement_vector,
            'C O M P L E X   D I S P L A C E M E N T   V E C T O R': self._complex_displacement_vector,
            'F O R C E S   O F   S I N G L E - P O I N T   C O N S T R A I N T': self._forces_of_single_point_constraints,
            'F O R C E S   O F   M U L T I P O I N T   C O N S T R A I N T': self._forces_of_multi_point_constraints,

            'T E M P E R A T U R E   V E C T O R': self._temperature_vector,
            'F I N I T E   E L E M E N T   T E M P E R A T U R E   G R A D I E N T S   A N D   F L U X E S': self._temperature_gradients_and_fluxes,

            #====================================================================
            # OES O-D
            'S T R E S S E S   I N   B A R   E L E M E N T S          ( C B A R )': self._stresses_in_cbar_elements,
            'S T R A I N S    I N   B A R   E L E M E N T S          ( C B A R )': self._strains_in_cbar_elements,

            'S T R E S S E S   I N   R O D   E L E M E N T S      ( C R O D )'     : self._stresses_in_crod_elements,
            'S T R A I N S   I N   R O D   E L E M E N T S      ( C R O D )': self._strains_in_crod_elements,

            'S T R E S S E S   I N   R O D   E L E M E N T S      ( C O N R O D )' : self._stresses_in_crod_elements,
            'S T R A I N S   I N   R O D   E L E M E N T S      ( C O N R O D )': self._strains_in_crod_elements,
            #====================================================================
            # OES 1-D
            'S T R E S S E S   I N   S C A L A R   S P R I N G S        ( C E L A S 1 )': self._stresses_in_celas2_elements,
            'S T R E S S E S   I N   S C A L A R   S P R I N G S        ( C E L A S 2 )': self._stresses_in_celas2_elements,
            'S T R E S S E S   I N   S C A L A R   S P R I N G S        ( C E L A S 3 )': self._stresses_in_celas2_elements,
            'S T R E S S E S   I N   S C A L A R   S P R I N G S        ( C E L A S 4 )': self._stresses_in_celas2_elements,

            'S T R A I N S    I N   S C A L A R   S P R I N G S        ( C E L A S 1 )':self._strains_in_celas2_elements,
            'S T R A I N S    I N   S C A L A R   S P R I N G S        ( C E L A S 2 )':self._strains_in_celas2_elements,
            'S T R A I N S    I N   S C A L A R   S P R I N G S        ( C E L A S 3 )':self._strains_in_celas2_elements,
            'S T R A I N S    I N   S C A L A R   S P R I N G S        ( C E L A S 4 )':self._strains_in_celas2_elements,
            #====================================================================
            # OES 2-D (no support for CQUAD8, CQUAD, CQUADR, CTRIAR, CTRAI6, CTRIAX, CTRIAX6)
            'S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )': self._stresses_in_ctria3_elements,
            'S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )': self._stresses_in_cquad4_elements,
            'S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )        OPTION = BILIN': self._stresses_in_cquad4_bilinear_elements,

            'S T R A I N S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )': self._strains_in_ctria3_elements,
            'S T R A I N S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )': self._strains_in_cquad4_elements,
            'S T R A I N S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )        OPTION = BILIN' : self._strains_in_cquad4_bilinear_elements,

            #==
            # composite partial ??? (e.g. bilinear quad)
            'S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S   ( T R I A 3 )': self._stresses_in_composite_ctria3_elements,
            'S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S   ( Q U A D 4 )': self._stresses_in_composite_cquad4_elements,

            'S T R A I N S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S   ( T R I A 3 )' : self._strains_in_composite_ctria3_elements,
            'S T R A I N S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S   ( Q U A D 4 )' : self._strains_in_composite_cquad4_elements,

            #===
            # ..todo:: not implemented
            'S T R E S S E S   I N   T R I A X 6   E L E M E N T S' : self._executive_control_echo,
            #====================================================================
            # OES 3-D
            'S T R E S S E S   I N    T E T R A H E D R O N   S O L I D   E L E M E N T S   ( C T E T R A )' : self._stresses_in_ctetra_elements,
            'S T R E S S E S   I N   H E X A H E D R O N   S O L I D   E L E M E N T S   ( H E X A )' : self._stresses_in_chexa_elements,
            'S T R E S S E S   I N   P E N T A H E D R O N   S O L I D   E L E M E N T S   ( P E N T A )' : self._stresses_in_cpenta_elements,

            'S T R A I N S   I N    T E T R A H E D R O N   S O L I D   E L E M E N T S   ( C T E T R A )' : self._strains_in_ctetra_elements,
            'S T R A I N S   I N   H E X A H E D R O N   S O L I D   E L E M E N T S   ( H E X A )' : self._strains_in_chexa_elements,
            'S T R A I N S   I N   P E N T A H E D R O N   S O L I D   E L E M E N T S   ( P E N T A )' : self._strains_in_cpenta_elements,
            #====================================================================
            # more not implemented...

            # STRESS
            'S T R E S S E S   I N   H Y P E R E L A S T I C   H E X A H E D R O N   E L E M E N T S  ( HEXA8FD )' : self._executive_control_echo,

            'N O N L I N E A R   S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S    ( Q U A D 4 )' : self._executive_control_echo,
            'N O N L I N E A R   S T R E S S E S   I N   T E T R A H E D R O N   S O L I D   E L E M E N T S   ( T E T R A )' : self._executive_control_echo,
            'N O N L I N E A R   S T R E S S E S   I N   H Y P E R E L A S T I C   Q U A D R I L A T E R A L   E L E M E N T S  ( QUAD4FD )' : self._executive_control_echo,
            'N O N L I N E A R   S T R E S S E S  IN  H Y P E R E L A S T I C   A X I S Y M M.  Q U A D R I L A T E R A L  ELEMENTS (QUADXFD)' : self._executive_control_echo,
            'N O N L I N E A R   S T R E S S E S   I N   T E T R A H E D R O N   S O L I D   E L E M E N T S   ( T E T R A )' : self._executive_control_echo,

            # FORCE
            'F O R C E S   I N   B A R   E L E M E N T S         ( C B A R )' : self._executive_control_echo,
            'F O R C E S   I N   R O D   E L E M E N T S     ( C R O D )': self._executive_control_echo,
            'F O R C E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )':  self._executive_control_echo,
            'F O R C E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )        OPTION = BILIN':  self._executive_control_echo,
            'F O R C E S   I N   S C A L A R   S P R I N G S        ( C E L A S 1 )': self._executive_control_echo,
            'F O R C E S   I N   S C A L A R   S P R I N G S        ( C E L A S 2 )': self._executive_control_echo,
            'F O R C E S   I N   S C A L A R   S P R I N G S        ( C E L A S 3 )': self._executive_control_echo,
            'F O R C E S   I N   S C A L A R   S P R I N G S        ( C E L A S 4 )': self._executive_control_echo,

            'L O A D   V E C T O R' : self._executive_control_echo,
            #'* * * END OF JOB * * *': self.end(),
        }
        self.markers = self.markerMap.keys()

    def __init_data__(self, debug=False, log=None):
        self.i = 0
        self.storedLines = []

        OES.__init__(self)
        OQG.__init__(self)
        OUG.__init__(self)
        F06Writer.__init__(self)

        ## the TITLE in the Case Control Deck
        self.Title = ''
        self.start_log(log, debug)

    def start_log(self, log=None, debug=False):
        """
        Sets up a dummy logger if one is not provided

        :self:  the object pointer
        :log:   a python logging object
        :debug: adds debug messages (True/False)
        """

        self.log = get_logger(log, 'debug' if debug else 'info')

    def getGridPointSingularities(self):  # .. todo:: not done
        """
        ::

                      G R I D   P O I N T   S I N G U L A R I T Y   T A B L E
          POINT    TYPE   FAILED      STIFFNESS       OLD USET           NEW USET
           ID            DIRECTION      RATIO     EXCLUSIVE  UNION   EXCLUSIVE  UNION
            1        G      4         0.00E+00          B        F         SB       S    *
            1        G      5         0.00E+00          B        F         SB       S    *
        """
        pass

    def getMaxSpcForces(self):  # .. todo:: not done
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int, float, float, float, float, float, float])
        #print "max SPC Forces   ",data
        #self.disp[isubcase] = DisplacementObject(isubcase,data)
        #print self.disp[isubcase]

    def getMaxMpcForces(self):  # .. todo:: not done
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int, float, float, float, float, float, float])
        #print "max SPC Forces   ",data
        #self.disp[isubcase] = DisplacementObject(isubcase,data)
        #print self.disp[isubcase]

    def getMaxDisplacements(self):  # .. todo:: not done
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int, float, float, float, float, float, float])
        #print "max Displacements",data
        disp = MaxDisplacement(data)
        #print disp.write_f06()
        #self.disp[isubcase] = DisplacementObject(isubcase,data)
        #print self.disp[isubcase]

    def getMaxAppliedLoads(self):  # .. todo:: not done
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int, float, float, float, float, float, float])
        #print "max Applied Loads",data
        #self.disp[isubcase] = DisplacementObject(isubcase,data)
        #print self.disp[isubcase]

    def _grid_point_weight_generator(self):
        line = ''
        lines = []
        while 'PAGE' not in line:
            line = self.infile.readline()[1:].strip()
            lines.append(line)
            self.i += 1
            self.fatal_check(line)
        #print '\n'.join(lines)
        self.grid_point_weight.read_grid_point_weight(lines)

    def _case_control_echo(self):
        line = ''
        lines = []
        while 'PAGE' not in line:
            line = self.infile.readline()[1:].strip()
            lines.append(line)
            self.i += 1
            self.fatal_check(line)
        #self.grid_point_weight.read_grid_point_weight(lines)

    def _executive_control_echo(self):
        line = ''
        lines = []
        while 'PAGE' not in line:
            line = self.infile.readline()[1:].strip()
            lines.append(line)
            self.i += 1
            self.fatal_check(line)
        #self.grid_point_weight.read_grid_point_weight(lines)

    def fatal_check(self, line):
        if 'FATAL' in line:
            raise FatalError(line)

    def _nastran_file_and_system_parameter_echo(self):
        line = ''
        lines = []
        while 'PAGE' not in line:
            line = self.infile.readline()[1:].strip()
            lines.append(line)
            self.i += 1
            self.fatal_check(line)
        #self.grid_point_weight.read_grid_point_weight(lines)

    def _grid_point_singularity_table(self):
        line = ''
        lines = []
        while 'PAGE' not in line:
            line = self.infile.readline()[1:].strip()
            lines.append(line)
            self.i += 1
            self.fatal_check(line)
        #self.grid_point_weight.read_grid_point_weight(lines)

    def _set_f06_date(self, month, day, year):
        months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
                  'JULY', 'AUGUST' 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
        assert month in months, 'month=%r' % month
        print("month =", month)
        month = months.index(month) + 1
        print("imonth =", month)
        day = int(day)
        year = int(year)
        self.date = (month, day, year)

    def readSubcaseNameID(self):
        """
        -4 -> 1                                                     JANUARY   5, 2014  MSC.NASTRAN 11/25/11   PAGE    14
        -3 -> DEFAULT
        -2 -> xxx             subcase 1
        """
        subtitle = self.storedLines[-3].strip()
        #print(''.join(self.storedLines[-3:]))

        msg = ''
        for i, line in enumerate(self.storedLines[-4:]):
            msg += '%i -> %s\n' % (-4 + i, line.rstrip())

        if self.Title is None or self.Title == '' and len(self.storedLines) > 4:
            title_line = self.storedLines[-4]
            self.Title = title_line[1:75].strip()
            date = title_line[75:93]
            month, day, year = date.split()
            self._set_f06_date(month, day[:-1], year)  # -1 chops the comma
            #assert 'PAGE' not in title_line, '%r' % date
            assert 'D I S P L A C' not in self.Title, msg
        #self.Title = subcaseName  # 'no title'

        subcaseName = ''
        #print("subcaseLine = %r" % subcaseName)
        label, isubcase = _parse_label_isubcase(self.storedLines)

        #subtitle = 'SUBCASE %s' % isubcase
        #label = 'SUBCASE %s' % isubcase

        #self.iSubcaseNameMap[self.isubcase] = [self.subtitle, self.label]

#title      date_stamp  page_stamp
#subtitle
#label      ???

        #print('------------')
        #print("title    = %r" % self.Title)
        #print("subtitle = %r" % subtitle)
        #print("label    = %r" % label)

        #assert self.Title == 'MSC.NASTRAN JOB CREATED ON 12-MAR-13 AT 12:52:23', self.Title
        self._subtitle = subtitle
        self.iSubcaseNameMap[isubcase] = [subtitle, subtitle]
        transient = self.storedLines[-1].strip()
        is_sort1 = False
        if transient:
            transWord, transValue = transient.split('=')
            transWord = transWord.strip()
            transValue = float(transValue)
            transient = [transWord, transValue]

            if transWord == 'LOAD STEP':  # nonlinear statics
                analysis_code = 10
            elif transWord == 'TIME STEP':  # TODO check name
                analysis_code = 6
            elif transWord == 'EIGENVALUE':  # normal modes
                analysis_code = 2
            elif transWord == 'FREQ':  # TODO check name
                analysis_code = 5
            elif transWord == 'FREQUENCY':
                analysis_code = 5
            elif transWord == 'POINT-ID':
                is_sort1 = True
                analysis_code = None
            elif transWord == 'ELEMENT-ID':
                is_sort1 = True
                #is_sort1 = False
                #is_sort2 = True
                analysis_code = None
            else:
                raise NotImplementedError('transientWord=|%r| is not supported...' % (transWord))
        else:
            transient = None
            analysis_code = 1

        dt = None
        if transient is not None:
            dt = transient[1]
        return (subcaseName, isubcase, transient, dt, analysis_code, is_sort1)

    def _real_eigenvalues(self):
        """
        ::

                                                     R E A L   E I G E N V A L U E S
           MODE    EXTRACTION      EIGENVALUE            RADIANS             CYCLES            GENERALIZED         GENERALIZED
            NO.       ORDER                                                                       MASS              STIFFNESS
                1         1        6.158494E+07        7.847607E+03        1.248985E+03        1.000000E+00        6.158494E+07
        """
        (subcaseName, isubcase, transient, dt, analysis_code, is_sort1) = self.readSubcaseNameID()

        headers = self.skip(2)
        data = self.readTable([int, int, float, float, float, float, float])

        if isubcase in self.eigenvalues:
            self.eigenvalues[isubcase].add_f06_data(data)
        else:
            self.eigenvalues[isubcase] = RealEigenvalues(isubcase)
            self.eigenvalues[isubcase].add_f06_data(data)
        self.iSubcases.append(isubcase)

    def _complex_eigenvalue_summary(self):
        """
        ::

                                 C O M P L E X   E I G E N V A L U E   S U M M A R Y
          ROOT     EXTRACTION                  EIGENVALUE                     FREQUENCY              DAMPING
           NO.        ORDER             (REAL)           (IMAG)                (CYCLES)            COEFFICIENT
               1           6          0.0              6.324555E+01          1.006584E+01          0.0
               2           5          0.0              6.324555E+01          1.006584E+01          0.0
        """
        #(subcaseName,isubcase,transient,dt,analysis_code,is_sort1) = self.readSubcaseNameID()
        isubcase = 1  # .. todo:: fix this...

        headers = self.skip(2)
        data = self.readTable([int, int, float, float, float, float])

        if isubcase in self.eigenvalues:
            self.eigenvalues[isubcase].add_f06_data(data)
        else:
            is_sort1 = True
            self.eigenvalues[isubcase] = ComplexEigenvalues(isubcase)
            self.eigenvalues[isubcase].add_f06_data(data)
        self.iSubcases.append(isubcase)

    def _complex_eigenvectors(self, marker):
        headers = self.skip(2)
        self.readTableDummy()

    def _element_strain_energies(self):
        """
        ::

          EIGENVALUE = -3.741384E-04
          CYCLES =  3.078479E-03
                                             E L E M E N T   S T R A I N   E N E R G I E S

                  ELEMENT-TYPE = QUAD4               * TOTAL ENERGY OF ALL ELEMENTS IN PROBLEM     =  -1.188367E-05
                     MODE               1            * TOTAL ENERGY OF ALL ELEMENTS IN SET      -1 =  -1.188367E-05

                                      ELEMENT-ID          STRAIN-ENERGY           PERCENT OF TOTAL    STRAIN-ENERGY-DENSITY
                                               1         -5.410134E-08                -0.0929             -4.328107E-05
                                               2         -3.301516E-09                -0.0057             -2.641213E-06
        """
        isubcase = 1 # TODO not correct
        cycles = self.storedLines[-1][1:].strip()
        cycles = float(cycles.split('=')[1])

        eigenvalue = self.storedLines[-2][1:].strip()
        eigenvalue = float(eigenvalue.split('=')[1])
        #print "eigenvalue=%s cycle=%s" %(eigenvalue,cycles)

        eTypeLine = self.skip(2)[1:]
        eType = eTypeLine[30:40]
        totalEnergy1 = eTypeLine[99:114]

        modeLine = self.skip(1)[1:]
        iMode = modeLine[24:40]
        totalEnergy2 = modeLine[99:114]
        #print "eType=%s totalEnergy1=|%s|" %(eType,totalEnergy1)
        #print "iMode=%s totalEnergy2=|%s|" %(iMode,totalEnergy2)
        headers = self.skip(2)

        data = []
        while 1:
            line = self.infile.readline()[1:].rstrip('\r\n ')
            self.i += 1
            if 'PAGE' in line:
                break
            sline = line.strip().split()
            if sline == []:
                break
            #print sline
            eid = int(sline[0])
            strainEnergy = float(sline[1])
            percentTotal = float(sline[2])
            strainEnergyDensity = float(sline[3])
            out = (eid, strainEnergy, percentTotal, strainEnergyDensity)
            data.append(out)

        if sline == []:
            line = self.infile.readline()[1:].rstrip('\r\n ')
            self.i += 1
            #print line

        return
        if isubcase in self.iSubcases:
            self.strainEnergyDensity[isubcase].readF06Data(data, transient)
        else:
            sed = strainEnergyDensity(data, transient)
            sed.readF06Data(data, transient)
            self.strainEnergyDensity[isubcase] = sed

    def _temperature_gradients_and_fluxes(self):
        (subcaseName, isubcase, transient, dt, analysis_code,
            is_sort1) = self.readSubcaseNameID()
        #print transient
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readGradientFluxesTable()
        #print data
        return
        if isubcase in self.temperatureGrad:
            self.temperatureGrad[isubcase].addData(data)
        else:
            self.temperatureGrad[isubcase] = TemperatureGradientObject(
                isubcase, data)
        self.iSubcases.append(isubcase)

    def readGradientFluxesTable(self):
        data = []
        Format = [int, str, float, float, float, float, float, float]
        while 1:
            line = self.infile.readline()[1:].rstrip('\r\n ')
            self.i += 1
            if 'PAGE' in line:
                return data
            sline = [line[0:15], line[15:24].strip(), line[24:44], line[44:61], line[61:78], line[78:95], line[95:112], line[112:129]]
            sline = self.parseLineGradientsFluxes(sline, Format)
            data.append(sline)
        return data

    def parseLineGradientsFluxes(self, sline, Format):
        out = []
        for entry, iFormat in izip(sline, Format):
            if entry.strip() is '':
                out.append(0.0)
            else:
                #print "sline=|%r|\n entry=|%r| format=%r" %(sline,entry,iFormat)
                entry2 = iFormat(entry)
                out.append(entry2)
        return out

    def readTable(self, Format, debug=False):
        """
        Reads displacement, spc/mpc forces

        :self:   the object pointer
        :Format: .. seealso:: parseLine
        """
        sline = True
        data = []
        while sline:
            sline = self.infile.readline()[1:].strip().split()
            if debug:
                print sline
            self.i += 1
            if 'PAGE' in sline:
                return data
            sline = self.parseLine(sline, Format)
            if sline is None:
                return data
            data.append(sline)
        return data

    def readTableDummy(self):
        sline = True
        data = []
        while sline:
            sline = self.infile.readline()[1:].strip().split()
            self.i += 1
            if 'PAGE' in sline:
                return data
            if sline is None:
                return data
            data.append(sline)
        return data

    def parseLine(self, sline, Format):
        """
        :self:   the object pointer
        :sline:  list of strings (split line)
        :Format: list of types [int,str,float,float,float] that maps to sline
        """
        out = []
        for entry, iFormat in izip(sline, Format):
            try:
                entry2 = iFormat(entry)
            except:
                #print "sline=|%s|\n entry=|%s| format=%s" %(sline, entry, iFormat)
                #raise
                return None
            out.append(entry2)
        return out

    def parseLineBlanks(self, sline, Format):
        """allows blanks"""
        out = []

        for entry, iFormat in izip(sline, Format):
            if entry.strip():
                try:
                    entry2 = iFormat(entry)
                except:
                    print("sline=|%s|\n entry=|%s| format=%s" %(sline,entry,Format))
                    raise
            else:
                entry2 = None
                #print "sline=|%s|\n entry=|%s| format=%s" %(sline,entry,iFormat)
            out.append(entry2)
        return out

    def read_f06(self, f06_filename=None):
        """
        Reads the F06 file

        :self: the object pointer
        """
        if f06_filename is None:
            f06_filename = self.f06_filename

        #print "reading..."
        blank = 0
        while 1:
            #if self.i%1000==0:
                #print "i=%i" %(self.i)
            line = self.infile.readline()
            marker = line[1:].strip()

            if 'FATAL' in marker and 'IF THE FLAG IS FATAL' not in marker:
                msg = '\n' + marker
                fatal_count = 0
                while 1:
                    line = self.infile.readline().rstrip()
                    #print "blank = %s" % blank
                    fatal_count += 1
                    if fatal_count == 20 or '* * * END OF JOB * * *' in line:
                        break
                    #else:
                        #blank = 0
                    msg += line + '\n'
                raise FatalError(msg.rstrip())

            if(marker != '' and 'SUBCASE' not in marker and 'PAGE' not in marker and 'FORTRAN' not in marker
               and 'USER INFORMATION MESSAGE' not in marker and 'TOTAL DATA WRITTEN FOR DATA BLOCK' not in marker
               and marker not in self.markers and marker != self._subtitle):
                #print("marker = %r" % marker)
                pass
                #print('Title  = %r' % self.subtitle)

            if marker in self.markers:
                blank = 0
                #print("\n1*marker = %r" % marker)
                self.markerMap[marker]()
                if(self._stop_after_reading_mass and
                   marker in 'O U T P U T   F R O M   G R I D   P O I N T   W E I G H T   G E N E R A T O R'):
                    break
                self.storedLines = []
                #print("i=%i" % self.i)
            elif 'R E A L   E I G E N V E C T O R   N O' in marker:
                blank = 0
                #print("\n2*marker = %r" % marker)
                self.lineMarkerMap['R E A L   E I G E N V E C T O R   N O'](marker)
                self.storedLines = []
            elif 'C O M P L E X   E I G E N V E C T O R   NO' in marker:
                blank = 0
                #print("\n2*marker = %r" % marker)
                self.lineMarkerMap['C O M P L E X   E I G E N V E C T O R   NO'](marker)
                self.storedLines = []

            elif 'News file -' in marker:
                blank = 0
                self.lineMarkerMap['News file -']()
                self.storedLines = []
            elif marker == '':
                blank += 1
                if blank == 20:
                    break
            elif self.isMarker(marker):  # marker with space in it (e.g. Model Summary)
                print("***marker = %r" % marker)

            else:
                blank = 0

            self.storedLines.append(line)
            self.i += 1
        #print "i=%i" %(self.i)
        self.infile.close()
        self.processF06()

    def processF06(self):
        #data = [self.disp,self.SpcForces,self.stress,self.isoStress,self.barStress,self.solidStress,self.temperature]
        dataPack = [self.solidStress]
        for dataSet in dataPack:
            for key, data in dataSet.iteritems():
                data.processF06Data()

    def isMarker(self, marker):
        """returns True if the word follows the 'N A S T R A N   P A T T E R N'"""
        marker = marker.strip().split('$')[0].strip()

        if len(marker) < 2 or marker == '* * * * * * * * * * * * * * * * * * * *':
            return False
        for i, char in enumerate(marker):
            #print "i=%s i%%2=%s char=%s" %(i,i%2,char)
            if i % 2 == 1 and ' ' is not char:
                return False
            elif i % 2 == 0 and ' ' == char:
                return False
        return True

    def skip(self, iskip):
        for i in xrange(iskip - 1):
            self.infile.readline()
        self.i += iskip
        return self.infile.readline()

    def print_results(self):
        msg = ''
        data = [self.displacements, self.spcForces, self.mpcForces, self.temperatures,
                self.eigenvalues, self.eigenvectors,
                self.rodStress, self.rodStrain,
                self.conrodStress, self.conrodStrain,
                self.barStress, self.barStrain,
                self.plateStress, self.plateStrain,
                self.compositePlateStress, self.compositePlateStrain,
                ]

        self.iSubcases = list(set(self.iSubcases))
        for isubcase in self.iSubcases:
            for result in data:
                if isubcase in result:
                    msg += str(result[isubcase])
        return msg

def _parse_label_isubcase(storedLines):
    label = storedLines[-2][1:65].strip()
    isubcase = storedLines[-2][65:].strip()
    if isubcase:
        isubcase = int(isubcase.split()[-1])
    else:
        isubcase = 1
    return label, isubcase
    #assert isinstance(isubcase,int),'isubcase=|%r|' % (isubcase)
    #print "subcaseName=%s isubcase=%s" % (subcaseName, isubcase)

if __name__ == '__main__':
    from pyNastran.f06.test.test_f06 import main
    main()
