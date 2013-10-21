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
import copy
from datetime import date

import pyNastran


def make_stamp(Title):
    #pageStamp = '1    MSC.NASTRAN JOB CREATED ON 10-DEC-07 AT 09:21:23                      NOVEMBER  14, 2011  MSC.NASTRAN  6/17/05   PAGE '
    #Title = 'MSC.NASTRAN JOB CREATED ON 10-DEC-07 AT 09:21:23'
    t = date.today()
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    today = '%-9s %s, %s' % (months[t.month - 1], t.day, t.year)

    release_date = '02/08/12'  # pyNastran.__releaseDate__
    release_date = ''
    build = 'pyNastran v%s %s' % (pyNastran.__version__, release_date)
    out = '1    %-67s %20s  %-22s PAGE ' % (Title, today, build)
    return out


def make_f06_header():
    n = ''
    lines1 = [
        n + '/* -------------------------------------------------------------------  */\n',
        n + '/*                              PYNASTRAN                               */\n',
        n + '/*                      - NASTRAN FILE INTERFACE -                      */\n',
        n + '/*                                                                      */\n',
        n + '/*              A Python reader/editor/writer for the various           */\n',
        n + '/*                        NASTRAN file formats.                         */\n',
        n + '/*                  Copyright (C) 2011-2013 Steven Doyle                */\n',
        n + '/*                                                                      */\n',
        n + '/*    This program is free software; you can redistribute it and/or     */\n',
        n + '/*    modify it under the terms of the GNU Lesser General Public        */\n',
        n + '/*    License as published by the Free Software Foundation;             */\n',
        n + '/*    version 3 of the License.                                         */\n',
        n + '/*                                                                      */\n',
        n + '/*    This program is distributed in the hope that it will be useful,   */\n',
        n + '/*    but WITHOUT ANY WARRANTY; without even the implied warranty of    */\n',
        n + '/*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the      */\n',
        n + '/*    GNU Lesser General Public License for more details.               */\n',
        n + '/*                                                                      */\n',
        n + '/*    You should have received a copy of the GNU Lesser General Public  */\n',
        n + '/*    License along with this program; if not, write to the             */\n',
        n + '/*    Free Software Foundation, Inc.,                                   */\n',
        n + '/*    675 Mass Ave, Cambridge, MA 02139, USA.                           */\n',
        n + '/* -------------------------------------------------------------------  */\n',
        '\n']

    n = 46 * ' '
    lines2 = [
        n + '* * * * * * * * * * * * * * * * * * * *\n',
        n + '* * * * * * * * * * * * * * * * * * * *\n',
        n + '* *                                 * *\n',
        n + '* *            pyNastran            * *\n',
        n + '* *                                 * *\n',
        n + '* *                                 * *\n',
        n + '* *                                 * *\n',
        n + '* *        Version %8s       * *\n' % (pyNastran.__version__),
        n + '* *                                 * *\n',
        n + '* *                                 * *\n',
        n + '* *          %15s        * *\n' % (pyNastran.__releaseDate2__),
        n + '* *                                 * *\n',
        n + '* *            Questions            * *\n',
        n + '* *        mesheb82@gmail.com       * *\n',
        n + '* *                                 * *\n',
        n + '* *                                 * *\n',
        n + '* * * * * * * * * * * * * * * * * * * *\n',
        n + '* * * * * * * * * * * * * * * * * * * *\n\n\n']
    return ''.join(lines1 + lines2)


def make_end(end_flag=False):
    lines = []
    lines2 = []
    if end_flag:
        lines = ['','',
        '0                                   * * * *  A N A L Y S I S  S U M M A R Y  T A B L E  * * * *',
        '0 SEID  PEID PROJ VERS APRCH      SEMG SEMR SEKR SELG SELR MODES DYNRED SOLLIN PVALID SOLNL LOOPID DESIGN CYCLE SENSITIVITY',
        ' --------------------------------------------------------------------------------------------------------------------------']
    #     0     0    1    1 '        '    T    T    T    T    T     F      F      T      0     F     -1            0           F

        seid = 0
        peid = 0
        proj = 1
        vers = 1
        approach = '        '

        SELG = 'T'
        SEMG = 'T'
        SEMR = 'T'
        SEKR = 'T'
        SELR = 'T'
        MODES = 'F'
        DYNRED = 'F'

        SOLLIN = 'T'
        PVALID = 0
        SOLNL = 'F'
        LOOPID = -1
        CYCLE = 0
        SENSITIVITY = 'F'

        msg = '     %s     %s    %s    %s %8r    %s    %s    %s    %s    %s     %s      %s      %s      %s     %s     %s            %s           %s' % (
            seid, peid, proj, vers, approach, SEMG, SEMR, SEKR, SELG, SELR, MODES, DYNRED, SOLLIN, PVALID, SOLNL,
            LOOPID, CYCLE, SENSITIVITY)
        lines.append(msg)

        lines2 = ['0SEID = SUPERELEMENT ID.',
        ' PEID = PRIMARY SUPERELEMENT ID OF IMAGE SUPERELEMENT.',
        ' PROJ = PROJECT ID NUMBER.',
        ' VERS = VERSION ID.',
        ' APRCH = BLANK FOR STRUCTURAL ANALYSIS.  HEAT FOR HEAT TRANSFER ANALYSIS.',
        ' SEMG = STIFFNESS AND MASS MATRIX GENERATION STEP.',
        ' SEMR = MASS MATRIX REDUCTION STEP (INCLUDES EIGENVALUE SOLUTION FOR MODES).',
        ' SEKR = STIFFNESS MATRIX REDUCTION STEP.',
        ' SELG = LOAD MATRIX GENERATION STEP.',
        ' SELR = LOAD MATRIX REDUCTION STEP. ',
        ' MODES = T (TRUE) IF NORMAL MODES OR BUCKLING MODES CALCULATED.',
        ' DYNRED = T (TRUE) MEANS GENERALIZED DYNAMIC AND/OR COMPONENT MODE REDUCTION PERFORMED.',
        ' SOLLIN = T (TRUE) IF LINEAR SOLUTION EXISTS IN DATABASE.',
        ' PVALID = P-DISTRIBUTION ID OF P-VALUE FOR P-ELEMENTS',
        ' LOOPID = THE LAST LOOPID VALUE USED IN THE NONLINEAR ANALYSIS.  USEFUL FOR RESTARTS.',
        ' SOLNL = T (TRUE) IF NONLINEAR SOLUTION EXISTS IN DATABASE.',
        ' DESIGN CYCLE = THE LAST DESIGN CYCLE (ONLY VALID IN OPTIMIZATION).',
        ' SENSITIVITY = SENSITIVITY MATRIX GENERATION FLAG.',
        ' ',
        ' No PARAM values were set in the Control File.']

    lines3 = [' ',
             '1                                        * * * END OF JOB * * *',
             ' ',
             ' ']
    return '\n'.join(lines+lines2+lines3)


class F06WriterDeprecated(object):
    def writeF06(self, f06OutName, is_mag_phase=False, makeFile=True,
                 deleteObjects=True):
        """.. seealso:: write_f06"""
        self.write_f06(f06OutName, is_mag_phase, makeFile, deleteObjects)

    def loadOp2(self, isTesting=False):
        """.. seealso:: load_op2"""
        self.load_op2(isTesting)

class F06Writer(object):
    def __init__(self, model='tria3'):
        self.Title = ''
        self.pageNum = 1
        self.set_f06_name(model)

    def set_f06_name(self, model):
        self.model = model
        self.f06OutName = '%s.f06.out' % self.model

    def load_op2(self, isTesting=False):
        print("self.class = ",self.__class__.__name__)
        if isTesting == False:  # TODO implement in way that doesnt require a variable (e.g. check parent class)
            raise RuntimeError("Don't call this method unless you're testing the F06Writer.  It breaks the F06 and OP2 classes.")
        from pyNastran.op2.op2 import OP2
        self.op2Name = model + '.op2'
        op2 = OP2(self.op2Name)
        op2.readOP2()

        # oug
        self.eigenvectors = op2.eigenvectors
        self.displacements = op2.displacements
        self.temperatures = op2.temperatures

        # oes
        #CBEAM
        #CSHEAR
        #CELASi
        self.rodStress = op2.rodStress
        self.rodStrain = op2.rodStrain
        self.barStress = op2.barStress
        self.barStrain = op2.barStrain
        self.plateStress = op2.plateStress
        self.plateStrain = op2.plateStrain
        self.compositePlateStress = op2.compositePlateStress
        self.compositePlateStrain = op2.compositePlateStrain

    def make_f06_header(self):
        """If this class is inherited, the F06 Header may be overwritten"""
        return make_f06_header()

    def make_stamp(self, Title):
        """If this class is inherited, the PAGE stamp may be overwritten"""
        return make_stamp(Title)

    def writeF06(self, f06OutName, is_mag_phase=False, makeFile=True,
                 deleteObjects=True):
        """
        .. deprecated: will be replaced in version 0.7 with :func:`read_op2`
        """
        warnings.warn('writeF06 has been deprecated; use '
                      'write_f06', DeprecationWarning, stacklevel=2)
        self.write_f06(self, f06OutName, is_mag_phase=is_mag_phase, make_file=makeFile,
                 delete_objects=deleteObjects)

    def make_grid_point_singularity_table(self, failed):
        msg = ''
        if failed:
            msg += '0                                         G R I D   P O I N T   S I N G U L A R I T Y   T A B L E\n'
            msg += '0                             POINT    TYPE   FAILED      STIFFNESS       OLD USET           NEW USET\n'
            msg += '                               ID            DIRECTION      RATIO     EXCLUSIVE  UNION   EXCLUSIVE  UNION\n'
            for (nid, dof) in failed:
                msg += '                                %s        G      %s         0.00E+00          B        F         SB       SB   *\n' % (nid, dof)

        pageStamp = self.make_stamp(self.Title)
        msg += pageStamp+'%i\n' % self.pageNum
        self.pageNum += 1
        return msg

    def write_oload(self, model, Fg):
        msg = ''
        msg += '        *** USER INFORMATION MESSAGE 7310 (VECPRN)\n'
        msg += '            ORIGIN OF SUPERELEMENT BASIC COORDINATE SYSTEM WILL BE USED AS REFERENCE LOCATION.\n'
        msg += '            RESULTANTS ABOUT ORIGIN OF SUPERELEMENT BASIC COORDINATE SYSTEM IN SUPERELEMENT BASIC SYSTEM COORDINATES.\n'
        msg += '       0                                                  OLOAD    RESULTANT       \n'

        nnodes = len(model.nodes)

        msg += '        SUBCASE/    LOAD\n'
        msg += '        DAREA ID    TYPE       T1            T2            T3            R1            R2            R3\n'
        msg += '      0        1     FX    3.000000E+03     ----          ----          ----       0.000000E+00 -6.000000E+04                             \n'
        msg += '                     FY       ----       5.000000E+03     ----       0.000000E+00     ----       2.000000E+05                             \n'
        msg += '                     FZ       ----          ----       0.000000E+00  0.000000E+00  0.000000E+00     ----                                  \n'
        msg += '                     MX       ----          ----          ----       1.300000E+04     ----          ----                                  \n'
        msg += '                     MY       ----          ----          ----          ----       0.000000E+00     ----                                  \n'
        msg += '                     MZ       ----          ----          ----          ----          ----       0.000000E+00                             \n'
        msg += '                   TOTALS  3.000000E+03  5.000000E+03  0.000000E+00  1.300000E+04  0.000000E+00  1.400000E+05\n'

        pageStamp = self.make_stamp(self.Title)
        msg += pageStamp+'%i\n' % self.pageNum
        self.pageNum += 1

        return msg





    def write_summary(self, f, card_count=None):


        summary = '                                        M O D E L   S U M M A R Y\n\n'


        self.cardsToRead = set([

            # rigid elements
            'RBAR', 'RBAR1', 'RBE1', 'RBE2', 'RBE3',

            # spc/mpc constraints
            'SPC', 'SPCADD', 'SPC1', 'SPCD', 'SPCAX',
            'MPC', 'MPCADD',
            'SUPORT', 'SUPORT1',

            # aero cards
            'CAERO1', 'CAERO2', 'CAERO3', 'CAERO4', 'CAERO5',

            # temperature cards
            'CHBDYE', 'CHBDYG', 'CHBDYP',
            'CONV',
        ])



        blocks = [
            ['POINTS', ['GRID', 'GRDSET', ]],
            ['ENTRIES', ['SPOINT']],

            ['ELEMENTS', [# these are sorted
                        # elements
                        'CONM1', 'CONM2', 'CMASS1', 'CMASS2', 'CMASS3', 'CMASS4',

                        # springs
                        'CELAS1', 'CELAS2', 'CELAS3', 'CELAS4', 'CELAS5',

                        # bushings
                        'CBUSH', 'CBUSH1D', 'CBUSH2D',

                        # dampers
                        'CDAMP1', 'CDAMP2', 'CDAMP3', 'CDAMP4', 'CDAMP5',

                        # bar flags
                        'BAROR', 'CBARAO',
                        # bars
                        'CBAR', 'CROD', 'CTUBE', 'CBEAM', 'CBEAM3', 'CONROD', 'CBEND',

                        # shells
                        'CTRIA3', 'CTRIA6', 'CTRIAR', 'CTRIAX', 'CTRIAX6',
                        'CQUAD4', 'CQUAD8', 'CQUADR', 'CQUADX', 'CQUAD',

                        # solids
                        'CTETRA', 'CPENTA', 'CHEXA',

                        # other
                        'CSHEAR', 'CVISC', 'CRAC2D', 'CRAC3D',
                        'CGAP', 'CFAST',

                        # thermal
                        'CHBDYP', 'CHBDYG', 'CONV',
                          ]],
            ['ELEMENTS', ['RBE2', 'RBE3']],
        ]
        #print("self.card_count", self.card_count)
        if card_count is None:
            card_count = self.card_count

        for block in blocks:
            block_name, keys = block
            key_count = 0
            for key in sorted(keys):
                try:
                    value = card_count[key]
                    summary += '                                   NUMBER OF %-8s %-8s = %8s\n' % (key, block_name, value)
                    key_count += 1
                except KeyError:
                    pass
            if key_count:
                summary += ' \n'
        #sys.exit(summary)
        f.write(summary)

        pageStamp = self.make_stamp(self.Title)
        f.write(pageStamp+'%i\n' % self.pageNum)
        self.pageNum += 1
        print(summary)

    def write_f06(self, f06OutName, is_mag_phase=False, make_file=True,
                 delete_objects=True, end_flag=False):
        """
        Writes an F06 file based on the data we have stored in the object

        :self:       the F06 object
        :f06OutName: the name of the F06 file to write
        :is_mag_phase: should complex data be written using Magnitude/Phase
                       instead of Real/Imaginary (default=False; Real/Imag)
                       Real objects don't use this parameter.
        :make_file:
           * True  -> makes a file
           * False -> makes a StringIO object for testing (default=True)
        """
        if isinstance(f06OutName, str):
            f = open(f06OutName, 'wb')
            self.write_summary(f)
        else:
            assert isinstance(f06OutName, file), 'type(f06OutName)= %s' % f06OutName
            f = f06OutName
            f06OutName = f.name
            print 'f06OutName =', f06OutName


        pageStamp = self.make_stamp(self.Title)
        #print "pageStamp = |%r|" %(pageStamp)
        #print "stamp     = |%r|" %(stamp)

        #is_mag_phase = False
        header = ['     DEFAULT                                                                                                                        \n',
                  '\n']
        for isubcase, result in sorted(self.eigenvalues.iteritems()):  # goes first
            (subtitle, label) = self.iSubcaseNameMap[isubcase]
            subtitle = subtitle.strip()
            header[0] = '     %s\n' % subtitle
            header[1] = '0                                                                                                            SUBCASE %i\n \n' % (isubcase)
            print(result.__class__.__name__)
            (msg, self.pageNum) = result.write_f06(header, pageStamp,
                                                   pageNum=self.pageNum, f=f, is_mag_phase=is_mag_phase)
            if delete_objects:
                del result
            f.write(msg)
            self.pageNum += 1

        # has a special header
        for isubcase, result in sorted(self.eigenvectors.iteritems()):
            (subtitle, label) = self.iSubcaseNameMap[isubcase]
            subtitle = subtitle.strip()
            header[0] = '     %s\n' % subtitle
            header[1] = '0                                                                                                            SUBCASE %i\n' % isubcase
            print(result.__class__.__name__)
            (msg, self.pageNum) = result.write_f06(header, pageStamp,
                                                   pageNum=self.pageNum, f=f, is_mag_phase=is_mag_phase)
            if delete_objects:
                del result
            f.write(msg)
            pageNum += 1

        # subcase name, subcase ID, transient word & value
        headerOld = ['     DEFAULT                                                                                                                        \n',
                     '\n', ' \n']
        header = copy.deepcopy(headerOld)
        resTypes = [
                    self.displacements, self.displacementsPSD, self.displacementsATO, self.displacementsRMS,
                    self.scaledDisplacements,  # ???
                    self.velocities, self.accelerations, #self.eigenvectors,
                    self.temperatures,
                    self.loadVectors, self.thermalLoadVectors,
                    self.forceVectors,

                    self.spcForces, self.mpcForces,

                    self.barForces, self.beamForces, self.springForces, self.damperForces,
                    self.solidPressureForces,

                    #------------------------------------------
                    # OEF - forces
                    self.rodForces, self.conrodForces, self.ctubeForces,
                    #------------------------------------------
                    # OES - strain

                    # rods
                    self.rodStrain, self.conrodStrain, self.ctubeStrain, self.nonlinearRodStress,


                    # bars/beams
                    self.barStrain, self.beamStrain,

                    # bush
                    self.bushStrain,

                    # plates
                    self.plateStrain, self.compositePlateStrain,
                    self.nonlinearPlateStrain,
                    self.ctriaxStrain, self.hyperelasticPlateStress,

                    # solids
                    self.solidStrain,

                    #------------------------------------------
                    # OES - stress

                    # rods
                    self.rodStress, self.conrodStress, self.ctubeStress, self.nonlinearRodStrain,

                    # bars/beams
                    self.barStress, self.beamStress,

                    # bush
                    self.bushStress, self.bush1dStressStrain,

                    # plates
                    self.plateStress, self.compositePlateStress,
                    self.nonlinearPlateStress,
                    self.ctriaxStress, self.hyperelasticPlateStrain,
                    #self.shearStrain, self.shearStress,

                    # solids
                    self.solidStress,
                    #------------------------------------------

                    self.gridPointStresses, self.gridPointVolumeStresses,
            #self.gridPointForces,
        ]

        if 1:
            iSubcases = self.iSubcaseNameMap.keys()
            #print("self.iSubcaseNameMap = %s" %(self.iSubcaseNameMap))
            for isubcase in sorted(iSubcases):
                (subtitle, label) = self.iSubcaseNameMap[isubcase]
                subtitle = subtitle.strip()
                label = label.strip()
                #print "label = ",label
                header[0] = '     %-127s\n' % (subtitle)
                header[1] = '0    %-72s                                SUBCASE %-15i\n' % (label, isubcase)
                #header[1] = '0    %-72s                                SUBCASE %-15i\n' %('',isubcase)
                for resType in resTypes:
                    #print "resType = ",resType
                    if isubcase in resType:
                        header = copy.deepcopy(headerOld)  # fixes bug in case
                        result = resType[isubcase]
                        try:
                            print(result.__class__.__name__)
                            (msg, self.pageNum) = result.write_f06(header, pageStamp, pageNum=self.pageNum, f=f, is_mag_phase=False)
                        except:
                            #print "result name = %s" %(result.name())
                            raise
                        if delete_objects:
                            del result
                        f.write(msg)
                        self.pageNum += 1
        if 0:
            for res in resTypes:
                for isubcase, result in sorted(res.iteritems()):
                    (msg, self.pageNum) = result.write_f06(header, pageStamp, pageNum=self.pageNum, f=f, is_mag_phase=False)
                    if delete_objects:
                        del result
                    f.write(msg)
                    self.pageNum += 1
        f.write(make_end(end_flag))
        if not make_file:
            print(f.getvalue())
        f.close()

if __name__ == '__main__':
    #Title = 'MSC.NASTRAN JOB CREATED ON 10-DEC-07 AT 09:21:23'
    #stamp = make_stamp(Title) # doesnt have pageNum
    #print "|%s|" %(stamp+'22')

    model = sys.argv[1]
    f06 = F06Writer(model)
    f06.load_op2(isTesting=True)
    f06.write_f06()
