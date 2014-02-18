from pyNastran.op2.resultObjects.tableObject import RealTableObject, ComplexTableObject
from pyNastran.f06.f06_formatting import writeFloats13E


class TemperatureGradientAndFluxObject(RealTableObject):

    def __init__(self, data_code, is_sort1, isubcase, dt=None):
        RealTableObject.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_f06(self, header, pageStamp, pageNum=1, f=None, is_mag_phase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, pageNum, f)
        msg = header + ['                   F I N I T E   E L E M E N T   T E M P E R A T U R E   G R A D I E N T S   A N D   F L U X E S\n',
                        ' \n',
                        '   ELEMENT-ID   EL-TYPE        X-GRADIENT       Y-GRADIENT       Z-GRADIENT        X-FLUX           Y-FLUX           Z-FLUX\n']
        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            grid_type = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            (rx, ry, rz) = rotation
            vals = [dx, dy, dz, rx, ry, rz]
            (vals2, isAllZeros) = writeFloats13E(vals)
            #if not isAllZeros:
            [dx, dy, dz, rx, ry, rz] = vals2
            msg.append('%14i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, grid_type, dx, dy, dz, rx, ry, rz.rstrip()))

        msg.append(pageStamp % pageNum)
        f.write(''.join(msg))
        return pageNum

    def _write_f06_transient(self, header, pageStamp, pageNum=1, f=None, is_mag_phase=False):
        words = ['                   F I N I T E   E L E M E N T   T E M P E R A T U R E   G R A D I E N T S   A N D   F L U X E S\n',
                 ' \n',
                 '   ELEMENT-ID   EL-TYPE        X-GRADIENT       Y-GRADIENT       Z-GRADIENT        X-FLUX           Y-FLUX           Z-FLUX\n']
        return self._write_f06_transient_block(words, header, pageStamp, pageNum, f)


class ComplexTemperatureGradientAndFluxObject(ComplexTableObject):
    def __init__(self, data_code, is_sort1, isubcase, dt=None):
        asdf
        ComplexTableObject.__init__(self, data_code, is_sort1, isubcase, dt)

    def write_f06(self, header, pageStamp, pageNum=1, f=None, is_mag_phase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, pageStamp, pageNum, f, is_mag_phase)
        msg = header + ['                               F O R C E S   O F   S I N G L E - P O I N T   C O N S T R A I N T\n',
                        ' \n',
                        '   ELEMENT-ID   EL-TYPE        X-GRADIENT       Y-GRADIENT       Z-GRADIENT        X-FLUX           Y-FLUX           Z-FLUX\n']
        raise RuntimeError('is this valid...')
        for nodeID, translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            grid_type = self.gridTypes[nodeID]

            (dx, dy, dz) = translation
            #dxr=dx.real; dyr=dy.real; dzr=dz.real;
            #dxi=dx.imag; dyi=dy.imag; dzi=dz.imag

            (rx, ry, rz) = rotation
            #rxr=rx.real; ryr=ry.real; rzr=rz.real
            #rxi=rx.imag; ryi=ry.imag; rzi=rz.imag

            #vals = [dxr,dyr,dzr,rxr,ryr,rzr,dxi,dyi,dzi,rxi,ryi,rzi]
            vals = list(translation) + list(rotation)
            (vals2, isAllZeros) = writeFloats13E(vals)
            #if not isAllZeros:
            [dx, dy, dz, rx, ry, rz] = vals2
            msg.append('%14i %6s     %13s  %13s  %13s  %13s  %13s  %-s\n' % (nodeID, grid_type, dx, dy, dz, rx, ry, rz.rstrip()))
        msg.append(pageStamp % pageNum)
        f.write(''.join(msg))
        return pageNum

    def _write_f06_transient(self, header, pageStamp, pageNum=1, f=None, is_mag_phase=False):
        words = ['                         C O M P L E X   F O R C E S   O F   S I N G L E   P O I N T   C O N S T R A I N T\n']
        return self._write_f06_transient_block(words, header, pageStamp, pageNum, f, is_mag_phase)

