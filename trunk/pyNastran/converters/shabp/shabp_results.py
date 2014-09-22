from numpy import zeros

class ShabpOut(object):
    def __init__(self, log=None, debug=False):
        pass

    def readline(self, f, i):
        i += 1
        return f.readline(), i

    def readline_n(self, f, i, n):
        i += n
        for j in xrange(n-1):
            f.readline()
        return f.readline(), i

    def read_shabp_out(self, out_filename):
        npatches = len(self.X)
        istart = zeros(npatches, dtype='int32')
        nelements = 0
        for ipatch in xrange(npatches):
            X = self.X[ipatch]
            nrows, ncols = X.shape
            nelementsi = (nrows-1) * (ncols-1)
            istart[ipatch] = nelements
            nelements += nelementsi

        print "istart =", istart
        print "nelements =", nelements
        Cp = zeros(nelements, dtype='float32')
        delta = zeros(nelements, dtype='float32')

        Cp_dict, delta_dict = self._parse_results(out_filename)
        ncomps = len(self.component_num_to_name)

        components = self.component_name_to_patch.keys()
        print "  istart=%s" % istart
        for name in sorted(components):
            #name = 'nosecone'
            icomp = self.component_name_to_num[name]
            print "Comp %r; num=%i" % (name, icomp)
            patches = self.component_name_to_patch[name]

            Cp_array = Cp_dict[icomp]
            delta_array = delta_dict[icomp]
            print "  len(CpArray) =", len(Cp_array)
            jelement_start = 0
            for i, ipatch in enumerate(patches):  # ipatch starts at 1
                X = self.X[ipatch-1]
                iistart = istart[ipatch-1]

                nrows, ncols = X.shape
                nelementsi = (nrows-1) * (ncols-1)
                Cp[   iistart:iistart+nelementsi] = Cp_array[   jelement_start:jelement_start+nelementsi]
                delta[iistart:iistart+nelementsi] = delta_array[jelement_start:jelement_start+nelementsi]
                print "  ipatch=%i Cp[%i:%i]=CpArray[%i:%i]" % (ipatch, iistart, iistart+nelementsi, jelement_start, jelement_start+nelementsi)
                jelement_start += nelementsi
            #break
        return Cp, delta

    def _parse_results(self, out_filename):
        f = open(out_filename, 'r')
        i = 0
        line,i = self.readline(f, i)
        while '******** MAIN PROGRAM NOW HAS CONTROL OF SYSTEM ********' not in line:
            line,i = self.readline(f, i)
        #print line

        while '*** PRESSURE CALCULATION PROGRAM' not in line:
            line,i = self.readline(f, i)
        #print line

        npatches = 44
        #6
        #0ELEMENT DATA   MACH=  6.000  ALT =  50000.  S REF =196272.0  SPAN =  669.6  IMPACT =  1  IMPACI =  3
        #                XCG = -713.4  YCG =    0.0    ZCG  =    0.0    MAC =  240.0   ISHAD =  1  ISHADI =  3
        #      ANGLE OF ATTACK = 45.00   YAW ANGLE =  0.00   K = 1.83000   ETAC =  1.0000   DELTA E =  0.00

        Cp_dict_components = {}
        delta_dict_components = {}
        for icomponent in xrange(npatches):
            print "icomponent =", icomponent
            mach_line, i = self.readline_n(f, i, 6)
            #print "*mach_line = ", mach_line.rstrip()
            if 'Summation Number' in mach_line:
                break
            #if ipatch == 1:
                #asfdfsadfas
            xcg_line,i   = self.readline(f, i)
            alpha_line,i = self.readline(f, i)

            xcent_line, i = self.readline_n(f, i, 3)
            #0  L      DEL CA        DEL CY        DEL CN       DEL CLL       DEL CLM       DEL CLN       CP             AREA
            #            CA            CY            CN           CLL           CLM            CLN        DELTA
            #           XCENT         YCENT         ZCENT      NX             NY             NZ
            #if ipatch == 1:
                #aaa
            line,i = self.readline(f, i)
            Cp = []
            Delta = []
            while 1:
                while line[0] == '0':
                    del_ca, del_cy, del_cn, del_cll, del_clm, del_cln, cp, area = (
                        line[8 :20], line[21:33],
                        line[35:47], line[49:63],
                        line[63:75], line[77:89],
                        line[91:103], line[105:117],
                    )

                    line,i = self.readline(f, i)
                    ca, cy, cn, cll, clm, cln, delta = (
                        line[8 :20], line[21:33],
                        line[35:47], line[49:63],
                        line[63:75], line[77:89],
                        line[91:103],
                    )

                    line,i = self.readline(f, i)
                    xc, yc, zc, nx, ny, nz = (
                        line[8 :20], line[21:33],
                        line[35:47], line[49:63],
                        line[63:75], line[77:89],
                    )

                    #print '%r' % line[:61]
                    #print '0=%r 1=%r 2=%r 3=%r 4=%r 5=%r 6=%r 7=%r' % (del_ca, del_cy, del_cn, del_cll, del_clm, del_cln, cp, area)
                    Cp.append(cp)
                    Delta.append(delta)
                    line,i = self.readline(f, i)

                #print '%r' % line
                #4 check on COMPONENT
                line,i = self.readline_n(f, i, 4)
                #print '---%r' % line.strip()
                if '*AIR' in line:
                    # keep going
                    line,i = self.readline_n(f, i, 7)
                elif 'COMPONENT' in line:
                    #npanels = None
                    while 1:
                        #PANELS:  patch32             patch33             patch41
                        #patch44
                        print line.strip()
                        line, i = self.readline(f, i)
                        panels = line.strip().split()
                        #npanels = len(panels)
                        #print "npanels =",len(panels)
                        if len(panels) == 0:
                            break
                        #print line.strip()
                        #npanels_old = npanels

                    while 'Mach   Velocity   Reynolds #   Altitude   -Freestream Conditions-   Gas' not in line:
                        line, i = self.readline(f, i)
                    #nskip = 0
                    #if npanels_old == 3:
                        #nskip = -2
                    line,i = self.readline_n(f, i, 9)
                    #print line
                    break
                    #print '%r' % line
                    #aaaa
            Cp_dict_components[icomponent] = Cp
            delta_dict_components[icomponent] = Delta
            #print '^%r' % line.strip()
        print "done"
        return Cp_dict_components, delta_dict_components


if __name__ == '__main__':
    s = ShabpOut()
    s.read_shabp_out('SHABP.OUT')
