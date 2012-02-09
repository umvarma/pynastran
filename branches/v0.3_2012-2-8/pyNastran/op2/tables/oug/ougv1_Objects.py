import sys
from struct import pack
from pyNastran.op2.resultObjects.op2_Objects import scalarObject,array

class complexDisplacementObject(scalarObject): # approachCode=1, sortCode=0, thermal=0
    def __init__(self,dataCode,iSubcase,freq=None):
        scalarObject.__init__(self,dataCode,iSubcase)
        self.freq = freq
        #print "complexDisplacementObject - self.freq=|%s|" %(self.freq)
        self.gridType     = {}
        self.translations = {}
        self.rotations    = {}
        self.addNewTransient()

    def updateDt(self,dataCode,freq):
        self.dataCode = dataCode
        self.applyDataCode()
        if freq is not None:
            self.log.debug("updating %s...%s=%s  iSubcase=%s" %(self.dataCode['name'],self.dataCode['name'],freq,self.iSubcase))
            self.freq = freq
            self.addNewTransient()
        ###

    def addNewTransient(self):
        """initializes the transient variables"""
        if self.dt not in self.translations:
            self.translations[self.freq] = {}
            self.rotations[self.freq]    = {}

    def add(self,nodeID,gridType,v1r,v1i,v2r,v2i,v3r,v3i,v4r,v4i,v5r,v5i,v6r,v6i):
        msg = "nodeID=%s v1r=%s v2r=%s v3r=%s" %(nodeID,v1r,v2r,v3r)
        #print msg
        #msg = ''
        assert 0<nodeID<1000000000, msg
        #assert nodeID not in self.translations,'complexDisplacementObject - static failure'

        self.translations[self.freq][nodeID] = [[v1r,v1i],[v2r,v2i],[v3r,v3i]] # dx,dy,dz
        self.rotations[self.freq][nodeID]    = [[v4r,v4i],[v5r,v5i],[v6r,v6i]] # rx,ry,rz
    ###

    def __repr__(self):
        msg = '---COMPLEX DISPLACEMENTS---\n'
        #if self.dt is not None:
        #    msg += '%s = %g\n' %(self.dataCode['name'],self.dt)
        headers = ['DxReal','DxImag','DyReal','DyImag','DzReal','DyImag','RxReal','RxImag','RyReal','RyImag','RzReal','RzImag']
        msg += '%-10s ' %('nodeID')
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for freq,translations in sorted(self.translations.items()):
            msg += 'freq = %g\n' %(freq)
            #print "freq = ",freq
            #print translations
            for nodeID,translation in sorted(translations.items()):
                rotation = self.rotations[freq][nodeID]
                (dx,dy,dz) = translation
                (rx,ry,rz) = rotation

                msg += '%-10i ' %(nodeID)
                vals = dx+dy+dz+rx+ry+rz
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %(0)
                    else:
                        msg += '%10.3e ' %(val)
                    ###
                msg += '\n'
            ###
        return msg

#---------------------------------------------------------------------------------
#class staticFluxObj(scalarObject): # approachCode=1, tableCode=3 - whatever the static version of this is...

class fluxObject(scalarObject): # approachCode=1, tableCode=3, thermal=1
    def __init__(self,dataCode,iSubcase,dt=None):
        scalarObject.__init__(self,dataCode,iSubcase)

        self.dt = dt
        self.fluxes = {}
        if dt is not None:
            self.fluxes = {}
            self.isTransient = True
            raise Exception('transient is supported yet...')

    def add(self,nodeID,gridType,v1,v2,v3,v4=None,v5=None,v6=None):
        assert 0<nodeID<1000000000, 'nodeID=%s' %(nodeID)
        assert nodeID not in self.fluxes
        self.fluxes[nodeID] = array([v1,v2,v3])

    def writeOp2(self,block3,deviceCode=1):
        """
        creates the binary data for writing the table
        @warning hasnt been tested...
        """
        msg = block3
        for nodeID,flux in sorted(self.fluxes.items()):
            grid = nodeID*10+deviceCode
            msg += pack('iffffff',grid,flux[0],flux[1],flux[2],0,0,0)
        ###
        return msg

    def __repr__(self):
        if self.isTransient:
            return self.__reprTransient__()

        msg = '---HEAT FLUX---\n'
        msg += '%-10s %-8s %-8s %-8s\n' %('NodeID','xFlux','yFlux','zFlux')
        for nodeID,flux in sorted(self.fluxes.items()):
            msg += '%10i ' %(nodeID)

            for val in flux:
                if abs(val)<1e-6:
                    msg += '%10s' %(0)
                else:
                    msg += '%10.3e ' %(val)
                ###
            msg += '\n'
        return msg

