from struct import unpack

class FortranFormat(object):
    def __init__(self):
        self.n = 0
        self.f = None
        self.obj = None
        self.data_code = None
        self.table_name = None
        self.isubcase = None
        self._table_mapper = {}

        #: stores if the user entered [] for iSubcases
        self.isAllSubcases = True
        self.valid_subcases = []

    def show(self, n):
        assert self.n == self.f.tell()
        nints = n // 4
        data = self.f.read(n)
        strings, ints, floats = self.show_data(data)
        self.f.seek(self.n)
        return strings, ints, floats

    def show_data(self, data):
        n = len(data)
        nints = n // 4
        strings = unpack(b'%is' % n, data)
        ints    = unpack(b'%ii' % nints, data)
        floats  = unpack(b'%if' % nints, data)
        print "strings =", strings
        print "ints    =", ints, '\n'
        print "floats  =", floats
        return strings, ints, floats

    def skip_block(self):
        """
        Skips a block following a pattern of:
            [nbytes, data, nbytes]
        :retval data: since data can never be None, a None value
                      indicates something bad happened.
        """
        data = self.f.read(4)
        ndata, = unpack(b'i', data)
        self.n += 8 + ndata
        self.goto(self.n)
        return None

    def read_block(self):
        """
        Reads a block following a pattern of:
            [nbytes, data, nbytes]
        :retval data: the data in binary
        """
        data = self.f.read(4)
        ndata, = unpack(b'i', data)

        data_out = self.f.read(ndata)
        data = self.f.read(4)
        self.n += 8 + ndata
        return data_out

    def read_markers(self, markers):
        """
        Gets specified markers, where a marker has the form of [4, value, 4].
        The "marker" corresponds to the value, so 3 markers takes up 9 integers.
        These are used to indicate position in the file as well as
        the number of bytes to read.

        :param markers: markers to get; markers = [-10, 1]
        """
        for i, marker in enumerate(markers):
            data = self.read_block()
            imarker, = unpack(b'i', data)
            assert marker == imarker, 'marker=%r imarker=%r; markers=%s i=%s' % (marker, imarker, markers, i)

    def get_nmarkers(self, n, rewind=True):
        """
        Gets n markers, so if n=2, it will get 2 markers.

        :param n: number of markers to get
        :param rewind: should the file be returned to the starting point
        :retval markers: list of [1, 2, 3, ...] markers
        """
        ni = self.n
        markers = []
        for i in xrange(n):
            data = self.read_block()
            marker, = unpack(b'i', data)
            markers.append(marker)
        if rewind:
            self.n = ni
            self.f.seek(self.n)
        return markers

    def _skip_subtables(self):
        self.isubtable = -3
        self.read_markers([-3, 1, 0])

        markers = self.get_nmarkers(1, rewind=True)
        while markers[0] != 0:
            data = self._skip_record()
            self.log.debug("skipping table_name = %r" % self.table_name)
            #if len(data) == 584:
                #self._parse_results_table3(data)
            #else:
                #data = self._parse_results_table4(data)

            self.isubtable -= 1
            self.read_markers([self.isubtable, 1, 0])
            markers = self.get_nmarkers(1, rewind=True)
        self.read_markers([0])

    def passer(self, data):
        """
        dummy function used for unsupported tables
        """
        pass

    def _read_subtables(self):
        self._data_factor = 1
        nstart = self.n
        self.isubtable = -3
        self.read_markers([-3, 1, 0])
        #data = self._read_record()
        #self._parse_results_table3(data)

        #self.isubtable -= 1 # -4
        #self.read_markers([self.isubtable, 1, 0])

        if self.table_name in self._table_mapper:
            if self.read_mode in [0, 1]:
                self.log.debug("table_name = %r" % self.table_name)
            table3_parser, table4_parser = self._table_mapper[self.table_name]
            passer = False
        else:
            #raise NotImplementedError(self.table_name)
            if self.read_mode in [0, 1]:
                self.log.debug("skipping table_name = %r" % self.table_name)
            table3_parser = None
            table4_parser = None
            passer = True

        markers = self.get_nmarkers(1, rewind=True)
        while markers[0] != 0:
            record_len = self._get_record_length()
            if record_len == 584:
                self.data_code = {'log': self.log,}  # resets the logger
                self.obj = None
                data = self._read_record()
                if not passer:
                    table3_parser(data)
            else:
                if passer or not self.is_valid_subcase():
                    data = self._skip_record()
                else:
                    if hasattr(self, 'num_wide'):
                        datai = b''
                        for data in self._stream_record():
                            data = datai + data
                            n = table4_parser(data)
                            assert isinstance(n, int), self.table_name
                            datai = data[n:]

                        if self.read_mode == 1:
                            if hasattr(self, 'obj') and hasattr(self.obj, 'ntimes'):
                                self.obj.ntimes += 1
                                self.obj.ntotal = record_len // (self.num_wide * 4) * self._data_factor
                                #print "ntotal =", self.obj.ntotal, type(self.obj)
                        elif self.read_mode == 2:
                            #print('self.obj.name =', self.obj.__class__.__name__)
                            if hasattr(self, 'obj') and hasattr(self.obj, 'itime'):
                                self.obj.itime += 1
                    else:
                        data = self._read_record()
                        n = table4_parser(data)
                    del n

            self.isubtable -= 1
            self.read_markers([self.isubtable, 1, 0])
            markers = self.get_nmarkers(1, rewind=True)
        self.read_markers([0])
        self.finish()

    def is_valid_subcase(self):
        """
        Lets the code check whether or not to read a subcase

        :param self: the object pointer
        :retval is_valid: should this subcase defined by self.isubcase be read?
        """
        if not self.isAllSubcases:
            if self.isubcase in self.valid_subcases:
                return True
            return False
        return True

    def goto(self, n):
        """
        Jumps to position n in the file

        :param self: the object pointer
        :param n:    the position to goto
        """
        self.n = n
        self.f.seek(n)

    def _get_record_length(self):
        len_record = 0
        n0 = self.n
        markers0 = self.get_nmarkers(1, rewind=False)

        n = self.n
        record = self.skip_block()
        len_record += self.n - n - 8  # -8 is for the block
        #print "len1 =", len_record

        markers1 = self.get_nmarkers(1, rewind=True)
        # handling continuation blocks
        if markers1[0] > 0:
            #nloop = 0
            while markers1[0] > 0: #, 'markers0=%s markers1=%s' % (markers0, markers1)
                markers1 = self.get_nmarkers(1, rewind=False)
                n = self.n
                record = self.skip_block()
                len_record += self.n - n - 8  # -8 is for the block
                markers1 = self.get_nmarkers(1, rewind=True)
        self.goto(n0)
        return len_record

    def _skip_record(self):
        markers0 = self.get_nmarkers(1, rewind=False)
        record = self.skip_block()

        markers1 = self.get_nmarkers(1, rewind=True)
        # handling continuation blocks
        if markers1[0] > 0:
            #nloop = 0
            while markers1[0] > 0: #, 'markers0=%s markers1=%s' % (markers0, markers1)
                markers1 = self.get_nmarkers(1, rewind=False)
                record = self.read_block()
                markers1 = self.get_nmarkers(1, rewind=True)
                #nloop += 1
        return record

    def _stream_record(self, debug=True):
        markers0 = self.get_nmarkers(1, rewind=False)
        if self.debug and debug:
            self.binary_debug.write('marker = [4, %i, 4]\n' % markers0[0])
        record = self.read_block()

        if self.debug and debug:
            nrecord = len(record)
            self.binary_debug.write('record = [%i, recordi, %i]\n' % (nrecord, nrecord))
        assert (markers0[0]*4) == len(record), 'markers0=%s*4 len(record)=%s' % (markers0[0]*4, len(record))
        yield record

        markers1 = self.get_nmarkers(1, rewind=True)

        # handling continuation blocks
        if markers1[0] > 0:
            nloop = 0
            while markers1[0] > 0: #, 'markers0=%s markers1=%s' % (markers0, markers1)
                markers1 = self.get_nmarkers(1, rewind=False)

                record = self.read_block()
                yield record
                markers1 = self.get_nmarkers(1, rewind=True)
                nloop += 1

    def _read_record(self, stream=False, debug=True):
        markers0 = self.get_nmarkers(1, rewind=False)
        if self.debug and debug:
            self.binary_debug.write('marker = [4, %i, 4]\n' % markers0[0])
        record = self.read_block()

        if self.debug and debug:
            nrecord = len(record)
            self.binary_debug.write('record = [%i, recordi, %i]\n' % (nrecord, nrecord))
        assert (markers0[0]*4) == len(record), 'markers0=%s*4 len(record)=%s' % (markers0[0]*4, len(record))

        markers1 = self.get_nmarkers(1, rewind=True)

        # handling continuation blocks
        if markers1[0] > 0:
            nloop = 0
            records = [record]
            while markers1[0] > 0: #, 'markers0=%s markers1=%s' % (markers0, markers1)
                markers1 = self.get_nmarkers(1, rewind=False)
                record = self.read_block()
                records.append(record)
                markers1 = self.get_nmarkers(1, rewind=True)
                nloop += 1

            if nloop > 0:
                record = ''.join(records)
        return record