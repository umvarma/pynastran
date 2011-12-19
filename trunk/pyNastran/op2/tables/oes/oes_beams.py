import sys
from struct import unpack
from oes_objects import stressObject,strainObject #,array
from pyNastran.op2.op2Errors import *

class beamStressObject(stressObject):
    """
    [1,0,0]
                 S T R E S S E S   I N   B E A M   E L E M E N T S        ( C B E A M )
                      STAT DIST/
     ELEMENT-ID  GRID   LENGTH    SXC           SXD           SXE           SXF           S-MAX         S-MIN         M.S.-T   M.S.-C
            1       1   0.000   -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04          
                    2   1.000   -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04 -3.125000E+04          

    """
    def __init__(self,dataCode,iSubcase,dt=None):
        stressObject.__init__(self,dataCode,iSubcase)
        self.eType = 'CBEAM'
        
        self.code = [self.formatCode,self.sortCode,self.sCode]
        self.xxb = {}
        self.grids = {}
        #self.sxc = {}
        #self.sxd = {}
        #self.sxe = {}
        #self.sxf = {}
        self.smax = {}
        self.smin = {}
        self.MS_tension = {}
        self.MS_compression = {}
        
        if self.code in [[1,0,0]]: # ,[1,0,1]
            #self.MS_axial   = {}
            #self.MS_torsion = {}
            self.getLength1     = self.getLength1_format1_sort0
            self.getLength2     = self.getLength2_format1_sort0
            self.getLengthTotal = self.getLengthTotal_format1_sort0

            #self.isImaginary = False
            if dt is not None:
                self.addNewTransient = self.addNewTransient_format1_sort0
                self.addNewEid       = self.addNewEidTransient_format1_sort0
                self.add             = self.addTransient_format1_sort0
            else:
                self.addNewEid = self.addNewEid_format1_sort0
                self.add       = self.add_format1_sort0
            ###
        #elif self.code==[2,1,0]:
        #    self.getLength       = self.getLength_format1_sort0
        #    self.addNewTransient = self.addNewTransient_format2_sort1
        #    self.addNewEid       = self.addNewEidTransient_format2_sort1
        #    #self.isImaginary = True
        else:
            raise InvalidCodeError('beamStress - get the format/sort/stressCode=%s' %(self.code))
        ###
        if dt is not None:
            self.isTransient = True
            self.dt = self.nonlinearFactor
            self.addNewTransient()
        ###

    def getLengthTotal_format1_sort0(self):
        return 444  # 44+10*40   (11 nodes)

    def getLength1_format1_sort0(self):
        return (44,'iifffffffff')

    def getLength2_format1_sort0(self):
        return (40,'ifffffffff')

    def addNewTransient_format1_sort0(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        #print "addNewTransient_beam+1+0"
        if self.dt not in self.smax:
            self.smax[self.dt] = {}
            self.smin[self.dt] = {}
            self.MS_tension[self.dt]     = {}
            self.MS_compression[self.dt] = {}

    def addNewTransient_format2_sort1(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        raise Exception('not supported')
        #print self.dataCode
        self.axial[self.dt]     = {}
        self.torsion[self.dt]   = {}

    def addNewEid_format1_sort0(self,out):
        #print "Beam Stress addNewEid..."
        (eid,grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out
        eid = (eid-self.deviceCode)/10
        #print "eid=%s grid=%s" %(eid,grid)
        assert eid >= 0
        #assert isinstance(eid,int)
        #assert isinstance(grid,int)
        self.grids[eid] = [grid]
        self.xxb[eid]  = [sd]
        self.smax[eid] = [smax]
        self.smin[eid] = [smin]
        self.MS_tension[eid] = [mst]
        self.MS_compression[eid] = [msc]
        return eid

    def addNewEid_format2_sort1(self,out):
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode)/10
        assert eid >= 0
        self.axial[eid]      = [axialReal,axialImag]
        self.torsion[eid]    = [torsionReal,torsionImag]
        return eid

    def addNewEidTransient_format1_sort0(self,out):
        #print "Beam Transient Stress addNewEid..."
        (eid,grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out

        eid = (eid-self.deviceCode)/10
        dt = self.dt
        assert eid  >= 0
        self.grids[eid] = [grid]
        self.xxb[eid] = [sd]
        self.smax[dt][eid] = [smax]
        self.smin[dt][eid] = [smin]
        self.MS_tension[dt][eid] = [mst]
        self.MS_compression[dt][eid] = [msc]
        return eid

    def addNewEidTransient_format2_sort1(self,out):
        raise Exception('not supported')
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode)/10
        dt = self.dt
        assert eid >= 0
        self.axial[dt][eid]      = [axialReal,axialImag]
        self.torsion[dt][eid]    = [torsionReal,torsionImag]
        return eid

    def add_format1_sort0(self,eid,out):
        #print "Beam Stress add..."
        (grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            self.smax[eid].append(smax)
            self.smin[eid].append(smin)
            self.MS_tension[eid].append(mst)
            self.MS_compression[eid].append(msc)
        ###

    def addTransient_format1_sort0(self,eid,out):
        #print "Beam Transient Stress add..."
        (grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out
        dt = self.dt
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            self.smax[dt][eid].append(smax)
            self.smin[dt][eid].append(smin)
            self.MS_tension[dt][eid].append(mst)
            self.MS_compression[dt][eid].append(msc)
        ###

    def __reprTransient_format1_sort0__(self):
        msg = '---BEAM STRESSES---\n'
        msg += '%-6s %6s %6s %7s' %('EID','eType','NID','xxb')
        headers = ['sMax','sMin','MS_tension','MS_compression']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,smax in sorted(self.smax.items()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for eid in sorted(smax):
                for i,nid in enumerate(self.grids[eid]):
                    xxb  = self.xxb[eid][i]
                    sMax = self.smax[dt][eid][i]
                    sMin = self.smin[dt][eid][i]
                    SMt  = self.MS_tension[dt][eid][i]
                    SMc  = self.MS_compression[dt][eid][i]
                    xxb = round(xxb,2)

                    msg += '%-6i %6s %6i %7.2f ' %(eid,self.eType,nid,xxb)
                    vals = [sMax,sMin,SMt,SMc]
                    for val in vals:
                        if abs(val)<1e-6:
                            msg += '%10s ' %('0')
                        else:
                            msg += '%10g ' %(val)
                        ###
                    msg += '\n'
            ###
        #print msg
        #sys.exit('beamT')
        return msg

    def __reprTransient_format2_sort1__(self):
        raise Exception('not implemented...')
        msg = '---COMPLEX BEAM STRESSES---\n'
        msg += '%-10s %10s ' %('EID','eType')
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,axial in sorted(self.axial.items()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for eid in sorted(axial):
                axial   = self.axial[dt][eid]
                torsion = self.torsion[dt][eid]
                msg += '%-6i %6s ' %(eid,self.eType)
                vals = axial + torsion # concatination
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10i ' %(val)
                    ###
                msg += '\n'
                #msg += "eid=%-4s eType=%s axial=%-4i torsion=%-4i\n" %(eid,self.eType,axial,torsion)
            ###
        return msg

    def __repr__(self):
        if   self.isTransient and self.code in [[1,0,0],[1,0,1]]:
            return self.__reprTransient_format1_sort0__()
        elif self.code==[2,1,0]:
            return self.__reprTransient_format2_sort1__()
        #else:
        #    raise Exception('code=%s' %(self.code))
        msg = '---BEAM STRESSES---\n'
        msg += '%-6s %6s %6s %6s' %('EID','eType','NID','xxb')
        headers = ['sMax','sMin','MS_tension','MS_compression']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'
        #print "self.code = ",self.code
        for eid in sorted(self.smax):
            #print self.xxb[eid]
            for i,nid in enumerate(self.grids[eid]):
                #print i,nid
                xxb  = self.xxb[eid][i]
                sMax = self.smax[eid][i]
                sMin = self.smin[eid][i]
                SMt  = self.MS_tension[eid][i]
                SMc  = self.MS_compression[eid][i]

                xxb = round(xxb,2)
                msg += '%-6i %6s %6i %4.2f ' %(eid,self.eType,nid,xxb)
                
                vals = [sMax,sMin,SMt,SMc]
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10g ' %(val)
                    ###
                msg += '\n'
        #print msg
        return msg

class beamStrainObject(strainObject):
    """
    """
    def __init__(self,dataCode,iSubcase,dt=None):
        strainObject.__init__(self,dataCode,iSubcase)
        self.eType = 'CBEAM' #{} # 'CBEAM/CONBEAM'

        self.code = [self.formatCode,self.sortCode,self.sCode]
        
        self.xxb = {}
        self.grids = {}
        #self.sxc = {}
        #self.sxd = {}
        #self.sxe = {}
        #self.sxf = {}
        self.smax = {}
        self.smin = {}
        self.MS_tension = {}
        self.MS_compression = {}
        
        if self.code in [[1,0,10]]:
            self.getLength1     = self.getLength1_format1_sort0
            self.getLength2     = self.getLength2_format1_sort0
            self.getLengthTotal = self.getLengthTotal_format1_sort0

            #self.isImaginary = False
            if dt is not None:
                self.addNewTransient = self.addNewTransient_format1_sort0
                self.addNewEid       = self.addNewEidTransient_format1_sort0
                self.add             = self.addTransient_format1_sort0
            else:
                self.addNewEid = self.addNewEid_format1_sort0
                self.add       = self.add_format1_sort0
            ###
        #elif self.code==[2,1,0]:
        #    self.getLength       = self.getLength_format1_sort0
        #    self.addNewTransient = self.addNewTransient_format2_sort1
        #    self.addNewEid       = self.addNewEidTransient_format2_sort1
        #    #self.isImaginary = True
        else:
            raise InvalidCodeError('beamStress - get the format/sort/stressCode=%s' %(self.code))
        ###
        if dt is not None:
            self.isTransient = True
            self.dt = self.nonlinearFactor
            self.addNewTransient()
        ###

    def getLengthTotal_format1_sort0(self):
        return 444  # 44+10*40   (11 nodes)

    def getLength1_format1_sort0(self):
        return (44,'iifffffffff')

    def getLength2_format1_sort0(self):
        return (40,'ifffffffff')

    def addNewTransient_format1_sort0(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        #print "addNewTransient_beam+1+0"
        if self.dt not in self.smax:
            self.smax[self.dt] = {}
            self.smin[self.dt] = {}
            self.MS_tension[self.dt]     = {}
            self.MS_compression[self.dt] = {}

    def addNewTransient_format2_sort1(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        raise Exception('not supported')
        #print self.dataCode
        if self.dt not in self.smax:
            self.axial[self.dt]     = {}
            self.torsion[self.dt]   = {}

    def addNewEid_format1_sort0(self,out):
        #print "Beam Stress addNewEid..."
        (eid,grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out
        eid = (eid-self.deviceCode)/10
        #print "eid=%s grid=%s" %(eid,grid)
        assert eid >= 0
        #assert isinstance(eid,int)
        #assert isinstance(grid,int)
        self.grids[eid] = [grid]
        self.xxb[eid]  = [sd]
        self.smax[eid] = [smax]
        self.smin[eid] = [smin]
        self.MS_tension[eid] = [mst]
        self.MS_compression[eid] = [msc]
        return eid

    def addNewEid_format2_sort1(self,out):
        raise Exception('not supported')
        assert eid >= 0
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode)/10
        self.axial[eid]      = [axialReal,axialImag]
        self.torsion[eid]    = [torsionReal,torsionImag]

    def addNewEidTransient_format1_sort0(self,out):
        #print "Beam Transient Stress addNewEid..."
        (eid,grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out

        eid = (eid-self.deviceCode)/10
        dt = self.dt
        assert eid  >= 0
        self.grids[eid] = [grid]
        self.xxb[eid] = [sd]
        self.smax[dt][eid] = [smax]
        self.smin[dt][eid] = [smin]
        self.MS_tension[dt][eid] = [mst]
        self.MS_compression[dt][eid] = [msc]
        return eid

    def addNewEidTransient_format2_sort1(self,out):
        raise Exception('not supported')
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode)/10
        assert eid >= 0
        dt = self.dt
        self.axial[dt][eid]      = [axialReal,axialImag]
        self.torsion[dt][eid]    = [torsionReal,torsionImag]

    def add_format1_sort0(self,eid,out):
        #print "Beam Stress add..."
        (grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            self.smax[eid].append(smax)
            self.smin[eid].append(smin)
            self.MS_tension[eid].append(mst)
            self.MS_compression[eid].append(msc)
        ###

    def addTransient_format1_sort0(self,eid,out):
        #print "Beam Transient Stress add..."
        (grid,sd,sxc,sxd,sxe,sxf,smax,smin,mst,msc) = out
        dt = self.dt
        if grid:
            self.grids[eid].append(grid)
            self.xxb[eid].append(sd)
            self.smax[dt][eid].append(smax)
            self.smin[dt][eid].append(smin)
            self.MS_tension[dt][eid].append(mst)
            self.MS_compression[dt][eid].append(msc)
        ###

    def __reprTransient_format2_sort1__(self):
        raise Exception('not supported')
        msg = '---COMPLEX BEAM STRAINS---\n'
        msg += '%-10s %10s ' %('EID','eType')
        headers = ['axialReal','axialImag','torsionReal','torsionImag']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,axial in sorted(self.axial.items()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for eid in sorted(axial):
                axial   = self.axial[dt][eid]
                torsion = self.torsion[dt][eid]
                msg += '%-6i %6s ' %(eid,self.eType)
                vals = axial + torsion # concatination
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10g ' %(val)
                    ###
                msg += '\n'
                #msg += "eid=%-4s eType=%s axial=%-4i torsion=%-4i\n" %(eid,self.eType,axial,torsion)
            ###
        return msg

    def __repr__(self):
        if   self.isTransient and self.code==[1,0,10]:
            return self.__reprTransient_format1_sort0__()
        elif self.code==[2,1,10]:
            return self.__reprTransient_format2_sort1__()

        msg = '---BEAM STRAINS---\n'
        msg += '%-6s %6s %6s %6s' %('EID','eType','NID','xxb')
        headers = ['sMax','sMin','MS_tension','MS_compression']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'
        #print "self.code = ",self.code
        for eid in sorted(self.smax):
            #print self.xxb[eid]
            for i,nid in enumerate(self.grids[eid]):
                #print i,nid
                xxb  = self.xxb[eid][i]
                sMax = self.smax[eid][i]
                sMin = self.smin[eid][i]
                SMt  = self.MS_tension[eid][i]
                SMc  = self.MS_compression[eid][i]

                xxb = round(xxb,2)
                msg += '%-6i %6s %6i %4.2f ' %(eid,self.eType,nid,xxb)
                
                vals = [sMax,sMin,SMt,SMc]
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10.3e ' %(val)
                    ###
                msg += '\n'
        #print msg
        return msg
