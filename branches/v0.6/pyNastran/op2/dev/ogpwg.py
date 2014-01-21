from struct import unpack


class OGPWG(object):
    def __init__(self):
        pass

    def _read_ogpwg_3(self, data):
        """
        Grid Point Weight Generator
        ..todo:: find the reference_point...
        """
        #self.show_data(data)
        self.words = [
                 'aCode',       'tCode',    '???',     'isubcase',
                 '???',         '???',      '???',          '???',
                 '???',         'num_wide', '???',          '???',
                 '???',         '???',      '???',          '???',
                 '???',         '???',      '???',          '???',
                 '???',         '???',      '???',          '???',
                 '???', 'Title', 'subtitle', 'label']

        self.parse_approach_code(data)
        if self.debug3():
            self.binary_debug.write('  aCode    = %r\n' % self.aCode)
            self.binary_debug.write('  tCode    = %r\n' % self.tCode)
            self.binary_debug.write('  isubcase = %r\n' % self.isubcase)

        self.read_title(data)
        self.write_debug_bits()

    def _read_ogpwg_4(self, data):
        """
        Grid Point Weight Generator
        """
        MO = array(unpack('36f', data[:4*36]))
        MO = MO.reshape(6,6)
        
        S = array(unpack('9f', data[4*36:4*(36+9)]))
        S = S.reshape(3,3)

        mxyz = array(unpack('12f', data[4*(36+9):4*(36+9+12)]))
        mxyz = mxyz.reshape(3,4)
        mass = mxyz[:, 0]
        cg = mxyz[:, 1:]
        
        IS = array(unpack('9f', data[4*(36+9+12):4*(36+9+12+9)]))
        IS = IS.reshape(3,3)

        IQ = array(unpack('3f', data[4*(36+9+12+9):4*(36+9+12+9+3)]))

        Q = array(unpack('9f', data[4*(36+9+12+9+3):4*(36+9+12+9+3+9)]))
        Q = Q.reshape(3,3)

        reference_point = None ## I'm assuming this is set in subtable3
        self.grid_point_weight.set_grid_point_weight(reference_point,
            MO, S, mass, cg, IS, IQ, Q)