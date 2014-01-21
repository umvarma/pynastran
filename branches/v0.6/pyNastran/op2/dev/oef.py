from struct import unpack

class OEF(object):
    def __init__(self):
        pass

    def OEF_ForceCode(self):
        """
        Gets the numwide codes for the element to determine if
        the real or complex result should be found.
        The format and sort codes do not always give the right answer...
        """
        realMapper = {
            1: 3,    # CROD
            2: 1 + (10 - 1) * 11,  # CBEAM
            3: 3,    # CTUBE
            4: 17,   # CSHEAR
            10: 3,    # CONROD
            11: 2,    # CELAS1
            12: 2,    # CELAS2
            13: 2,    # CELAS3
            14: 2,    # CELAS4

            20: 2,    # CDAMP1
            21: 2,    # CDAMP2
            22: 2,    # CDAMP3
            23: 2,    # CDAMP4
            24: 3,    # CVISC
            33: 9,    # CQUAD4
            34: 9,    # CBAR
            35: 7,    # CCONEAX
            38: 9,    # CGAP
            40: 8,    # CBUSH1D ???
            64: 2 + (11 - 2) * 5,  # CQUAD8
            69: 1 + (8 - 1) * 2,  # CBEND
            70: 2 + (11 - 2) * 4,  # CTRIAR
            74: 9,    # CTRIA3
            75: 2 + (11 - 2) * 4,  # CTRIA6


            #76:  16,   # Acoustic Velocity/Pressure CHEXA ???
            76: None,  # dummy so it doesnt go into the real results
            77: 10,   # Acoustic Velocity/Pressure CPENTA
            78: 10,   # Acoustic Velocity/Pressure CTETRA

            82: 2 + (11 - 2) * 5,  # CQUADR
            95: 9,    # composite CQUAD4 ???
            96: 9,    # composite CQUAD8 ???
            97: 9,    # composite CTRIA3 ???
            98: 9,    # composite CTRIA6 ???
            100: 8,    # BARS
            102: 7,    # CBUSH
            144: 2 + (11 - 2) * 5,  # bilinear CQUAD4
            189: 6 + (19 - 6) * 4,  # VUQUAD
            190: 6 + (19 - 6) * 3,  # VUTRIA
            191: 4 + (12 - 4) * 2,  # VUBEAM
            200: 9,    # CWELD
            232: 9,    # composite CQUADR ???
            233: 9,    # composite TRIAR ???
            235: 9,    # punch CQUADR...num_wide in DMAP is wrong...left out first entry...
            236: 8,    # punch CTRIAR
        }
        imagMapper = {
            1: 5,    # CROD
            2: 1 + (17 - 1) * 11,  # CBEAM
            3: 5,    # CTUBE
            4: 33,   # CSHEAR
            10: 5,    # CONROD

            11: 3,    # CELAS1
            12: 3,    # CELAS2
            13: 3,    # CELAS3
            14: 3,    # CELAS4

            20: 3,    # CDAMP1
            21: 3,    # CDAMP2
            22: 3,    # CDAMP3
            23: 3,    # CDAMP4
            24: 5,    # CVISC
            33: 17,   # CQUAD4
            34: 17,   # CBAR
            35: 7,    # CCONEAX # needed to not crash the code...
            38: 9,    # CGAP
            40: 8,    # CBUSH1D ???
            64: 2 + (19 - 2) * 5,  # CQUAD8
            69: 1 + (14 - 1) * 2,  # CBEND
            70: 2 + (19 - 2) * 4,  # CTRIAR
            74: 17,   # CTRIA3
            75: 2 + (19 - 2) * 4,  # CTRIA6

            76: 16,   # Acoustic Velocity/Pressure CHEXA_PR
            77: 16,   # Acoustic Velocity/Pressure CPENTA_PR
            78: 16,   # Acoustic Velocity/Pressure CTETRA_PR

            82: 2 + (19 - 2) * 5,  # CQUADR
            95: 9,    # composite CQUAD4 ???
            96: 9,    # composite CQUAD8 ???
            97: 9,    # composite CTRIA3 ???
            98: 9,    # composite CTRIA6 ???
            100: 14,   # BARS
            102: 13,   # CBUSH
            144: 2 + (19 - 2) * 5,  # bilinear CQUAD4
            189: 6 + (31 - 6) * 4,  # VUQUAD
            190: 6 + (31 - 6) * 3,  # VUTRIA
            191: 4 + (18 - 4) * 2,  # VUBEAM
            200: 17,   # CWELD
            232: 9,    # composite CQUADR ???
            233: 9,    # composite TRIAR ???
            235: 17,   # punch CQUADR...num_wide in DMAP is wrong...left out first entry...
            236: 16,   # punch CTRIAR
        }

        Real = realMapper[self.element_type]
        Imag = imagMapper[self.element_type]
        return (Real, Imag)

    def read_oef1_3(self, data):
        self.words = ['aCode',       'tCode',    'element_type', 'isubcase',
                 '???',         '???',      '???',          '???',
                 'format_code', 'num_wide', 'o_code',       '???',
                 '???',         '???',      '???',          '???',
                 '???',         '???',      '???',          '???',
                 '???',         '???',      '???',          '???',
                 '???', 'Title', 'subtitle', 'label']

        self.parse_approach_code(data)

        #: element type
        self.add_data_parameter( data, 'element_type', 'i', 3, False)

        # dynamic load set ID/random code
        #self.add_data_parameter(data, 'dLoadID', 'i', 8, False)

        #: format code
        self.add_data_parameter( data, 'format_code', 'i', 9, False)

        #: number of words per entry in record
        #: .. note: is this needed for this table ???
        self.add_data_parameter(data, 'num_wide', 'i', 10, False)

        #: undefined in DMAP...
        self.add_data_parameter(data, 'o_code', 'i', 11, False)

        #: thermal flag; 1 for heat ransfer, 0 otherwise
        self.add_data_parameter(data, 'thermal', 'i', 23, False)

        ## assuming tCode=1
        if self.analysis_code == 1:   # statics
            self.add_data_parameter(data, 'loadID', 'i', 5, False)  # load set ID number
            self.apply_data_code_value('dataNames', ['loadID'])
            self.setNullNonlinearFactor()
        elif self.analysis_code == 2:  # normal modes/buckling (real eigenvalues)
            #: mode number
            self.add_data_parameter(data, 'mode', 'i', 5)
            #: eigenvalue
            self.add_data_parameter(data, 'eign', 'f', 6, False)
            self.apply_data_code_value('dataNames', ['mode', 'eigr', 'mode_cycle'])
        elif self.analysis_code == 3:  # differential stiffness 0
            #: load set ID number
            self.add_data_parameter(data, 'loadID', 'i', 5)
            self.apply_data_code_value('dataNames', ['loadID'])
        elif self.analysis_code == 4:  # differential stiffness 1
            #: load set ID number
            self.add_data_parameter(data, 'loadID', 'i', 5)
            self.apply_data_code_value('dataNames', ['loadID'])
        elif self.analysis_code == 5:   # frequency
            self.add_data_parameter(data, 'freq', 'f', 5)  # frequency
            self.apply_data_code_value('dataNames', ['freq'])
        elif self.analysis_code == 6:  # transient
            self.add_data_parameter(data, 'time', 'f', 5)  # time step
            self.apply_data_code_value('dataNames', ['time'])
        elif self.analysis_code == 7:  # pre-buckling
            #: load set ID number
            self.add_data_parameter(data, 'loadID', 'i', 5)
            #self.apply_data_code_value('dataNames',['lsdvmn'])
            self.apply_data_code_value('dataNames', ['loadID'])
        elif self.analysis_code == 8:  # post-buckling
            #: load set ID number
            self.add_data_parameter(data, 'loadID', 'i', 5)
            #: real eigenvalue
            self.add_data_parameter( data, 'eigr', 'f', 6, False)
            self.apply_data_code_value('dataNames', ['lsdvmn', 'eigr'])
        elif self.analysis_code == 9:  # complex eigenvalues
            #: mode number
            self.add_data_parameter(data, 'mode', 'i', 5)
            #: real eigenvalue
            self.add_data_parameter(data, 'eigr', 'f', 6, False)
            #: imaginary eigenvalue
            self.add_data_parameter(data, 'eigi', 'f', 7, False)
            self.apply_data_code_value('dataNames', ['mode', 'eigr', 'eigi'])
        elif self.analysis_code == 10:  # nonlinear statics
            #: load step
            self.add_data_parameter(data, 'load_step', 'f', 5)
            self.apply_data_code_value('dataNames', ['load_step'])
        elif self.analysis_code == 11:  # geometric nonlinear statics
            #: load set ID number
            self.add_data_parameter(data, 'loadID', 'i', 5)
            self.apply_data_code_value('dataNames', ['loadID'])
        else:
            raise RuntimeError('invalid analysis_code...analysis_code=%s' % (str(self.analysis_code) + '\n' + self.code_information()))

        self.element_name = self.element_mapper[self.element_type]
        if self.debug:
            self.binary_debug.write('  element_name = %r\n' % self.element_name)
            self.binary_debug.write('  aCode    = %r\n' % self.aCode)
            self.binary_debug.write('  tCode    = %r\n' % self.tCode)
            self.binary_debug.write('  isubcase = %r\n' % self.isubcase)

        self.read_title(data)
        if self.element_type not in self.element_mapper:
            raise NotImplementedError(self.element_type)

        self.write_debug_bits()

    def read_oef2_3(self, data):
        pass

    def read_oef1_4(self, data):
        (num_wide_real, num_wide_imag) = self.OEF_ForceCode()
        if self.debug4():
            self.binary_debug.write('  num_wide_real = %r\n' % num_wide_real)
            self.binary_debug.write('  num_wide_imag = %r\n' % num_wide_imag)
        

        n = 0
        if self.element_type in []:
            pass
        elif self.element_type in [2]:
            #2-CBEAM
            format1 = b'i'
            formatAll = b'i8f'  # 36
            
            ntotal = 400  # 1+(10-1)*11=100 ->100*4 = 400
            nelements = len(data) // ntotal
            for i in xrange(nelements):
                edata = data[n:n+4]
                eid_device, = unpack(format1, edata)
                eid = (eid_device - self.device_code) // 10
                n += 4

                for i in xrange(11):
                    edata = data[n:n+36]
                    out = unpack(formatAll, edata)
                    if self.debug4():
                        self.binary_debug.write('OEF_Beam - %s\n' % (str(out)))
                    (nid, sd, bm1, bm2, ts1, ts2, af, ttrq, wtrq) = out
                    #print "eidTemp = ",eidTemp
                    #print "nid = ",nid
                    #print "sd = ",sd

                    dataIn = [eid, nid, sd, bm1, bm2, ts1, ts2, af, ttrq, wtrq]
                    #print "%s        " %(self.get_element_type(self.element_type)),dataIn
                    #eid = self.obj.add_new_eid(out)
                    #if i == 0:  # isNewElement:
                        #self.obj.addNewElement(dt, dataIn)
                        #print
                    #elif sd > 0.:
                        #self.obj.add(dt, dataIn)
                    #print
                    n += 36
                    #else: pass
                #print "len(data) = ",len(self.data)
            #print self.beamForces

        elif self.element_type in [34]:  # bars
            # 34-CBAR
            format1 = b'i8f'  # 9
            ntotal = 36  # 9*4
            n = 0
            nelements = len(data) // ntotal
            for i in xrange(nelements):
                edata = data[n:n+36]
            
                out = unpack(format1, edata)
                if self.debug4():
                    self.binary_debug.write('OEF_CBar - %s\n' % (str(out)))
                (eid_device, bm1a, bm2a, bm1b, bm2b, ts1, ts2, af, trq) = out
                eid = (eid_device - self.device_code) // 10
            
                dataIn = [eid, bm1a, bm2a, bm1b, bm2b, ts1, ts2, af, trq]
                #print "%s" %(self.get_element_type(self.element_type)),dataIn
                #eid = self.obj.add_new_eid(out)
                #self.obj.add(dt, dataIn)
                n += ntotal

        elif self.element_type in [74]: # centroidal shells
            # 33-CQUAD4
            # 74-CTRIA3
            format1 = b'i8f'
            ntotal = 36 # 9*4
            nelements = len(data) // ntotal
            for i in xrange(nelements):
                edata = data[n:n+36]

                out = unpack(format1, edata)
                if self.debug4():
                    self.binary_debug.write('OEF_Plate-%s - %s\n' % (self.element_type, str(out)))
                (eid_device, mx, my, mxy, bmx, bmy, bmxy, tx, ty) = out
                eid = (eid_device - self.device_code) // 10
                assert eid > 0
                #print("eType=%s" % eType)

                dataIn = [eid, mx, my, mxy, bmx, bmy, bmxy, tx, ty]
                #print "%s" %(self.get_element_type(self.element_type)),dataIn
                #eid = self.obj.add_new_eid(out)
                #self.obj.add(dt, dataIn)
                n += ntotal
            #print self.plateForces

        elif self.element_type in [64, 70, 75, 82, 144]: # bilinear shells
            # 64-CQUAD8
            # 70-CTRIAR
            # 75-CTRIA6,
            # 82-CQUAD8,
            # 144-CQUAD4-bilinear
            #dt = self.nonlinear_factor
            if self.element_type in [70, 75]:  # CTRIAR,CTRIA6
                nnodes = 3
            elif self.element_type in [64, 82, 144]:  # CQUAD8,CQUADR,CQUAD4-bilinear
                nnodes = 4
            else:
                raise NotImplementedError(self.code_information())

            allFormat = b'i8f' # 36
            format1 = b'i4s'  # 8

            ntotal = 8 + (nnodes+1) * 36 # centroidal node is the + 1
            assert ntotal == self.num_wide * 4, 'ntotal=%s numwide=%s' % (ntotal, self.num_wide * 4)
            nelements = len(data) // ntotal

            for i in xrange(nelements):
                edata = data[n:n+44]

                out = unpack(format1 + allFormat, edata)
                if self.debug4():
                    self.binary_debug.write('OEF_Plate2-%s - %s\n' % (self.element_type, str(out)))
                (eid_device, term, nid, mx, my, mxy, bmx, bmy, bmxy, tx, ty) = out
                #term= 'CEN\'
                #print "eType=%s" % eType

                eid = (eid_device - self.device_code) // 10
                #print "eid_device=", eid_device
                #print "eid=", eid
                assert eid > 0
                dataIn = [term, nid, mx, my, mxy, bmx, bmy, bmxy, tx, ty]
                #print "%s" %(self.get_element_type(self.element_type)),dataIn
                #self.obj.addNewElement(eid, dt, dataIn)
                n += 44
                for i in xrange(nnodes):
                    edata = data[n:n+36]
                    out = unpack(allFormat, edata)
                    if self.debug4():
                        self.binary_debug.write('%s\n' % (str(out)))
                    (nid, mx, my, mxy, bmx, bmy, bmxy, tx, ty) = out
                    #print "nid=", nid
                    assert nid > 0, 'nid=%s' % nid
                    #dataIn = [nid,mx,my,mxy,bmx,bmy,bmxy,tx,ty]
                    #print "***%s    " %(self.get_element_type(self.element_type)),dataIn
                    #self.obj.add(eid, dt, out)
                    n += 36
        elif self.element_type in [95, 96, 97, 98]: # composites
            # 95 - CQUAD4
            # 96 - CQUAD8
            # 97 - CTRIA3
            # 98 - CTRIA6 (composite)
            return
            ntotal = 9 * 4
            nelements = len(data) // ntotal
            if self.debug:
                self.binary_debug.write('  [cap, element1, element2, ..., cap]\n')
                self.binary_debug.write('  cap = %i  # assume 1 cap when there could have been multiple\n' % len(data))
                #self.binary_debug.write('  #centeri = [eid_device, j, grid, fd1, sx1, sy1, txy1, angle1, major1, minor1, vm1,\n')
                #self.binary_debug.write('  #                                fd2, sx2, sy2, txy2, angle2, major2, minor2, vm2,)]\n')
                #self.binary_debug.write('  #nodeji = [eid, iLayer, o1, o2, t12, t1z, t2z, angle, major, minor, ovm)]\n')
                self.binary_debug.write('  nelements=%i; nnodes=1 # centroid\n' % nelements)

            eid_old = 0
            format1 = 'i8si4f4s' # 9
            for i in xrange(nelements):
                if i % 10000 == 0:
                   print 'i = ', i
                edata = data[n:n+ntotal]  # 4*9
                out = unpack(format1, edata)
                (eid_device, theory, lamid, failure_index_direct_stress, failure_mode_max_shear,
                         failure_index_interlaminar_shear, fmax, failure_flag) = out
                eid = (eid_device - self.device_code) // 10
                if self.debug4():
                    if eid > 0:
                        self.binary_debug.write('  ----------\n')
                        self.binary_debug.write('  eid = %i\n' % eid)
                    self.binary_debug.write('  C = [%s]\n' % ', '.join(['%r' % di for di in out]) )
               
                if eid > 0:
                    #print "eid =", eid
                    #self.obj.add_new_eid(eType, dt, eid, o1, o2, t12, t1z, t2z, angle, major, minor, ovm)
                    pass
                else:
                    pass
                    #self.obj.add(dt, eid, o1, o2, t12, t1z, t2z, angle, major, minor, ovm)
                eid_old = eid
                n += ntotal
        else:
            raise NotImplementedError('sort1 Type=%s num=%s' % (self.element_name, self.element_type))
        assert nelements > 0, nelements
        assert len(data) % ntotal == 0, '%s n=%s len=%s ntotal=%s' % (self.element_name, len(data) % ntotal, len(data), ntotal)
        
        
    def read_oef2_4(self, data):
        pass
        