import sys
import copy

# pyNastran
from pyNastran.op2.resultObjects.tableObject import TableObject,complexTableObject

class displacementObject(TableObject): # approachCode=1, thermal=0
    def __init__(self,dataCode,isSort1,iSubcase,dt=None):
        TableObject.__init__(self,dataCode,isSort1,iSubcase,dt)

    def writeF06(self,header,pageStamp,pageNum=1,f=None):
        if self.nonlinearFactor is not None:
            return self.writeF06Transient(header,pageStamp,pageNum,f)
        words = ['                                             D I S P L A C E M E N T   V E C T O R\n',
                 ' \n',
                 '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        words += self.getTableMarker()
        return self._writeF06Block(words,header,pageStamp,pageNum,f)

    def writeF06Transient(self,header,pageStamp,pageNum=1,f=None):
        words = ['                                             D I S P L A C E M E N T   V E C T O R\n',
                 ' \n',
                 '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        words += self.getTableMarker()
        return self._writeF06TransientBlock(words,header,pageStamp,pageNum,f)

    def getTableMarker(self):
        if self.isATO():
            words = self.ATO_words()
        elif self.isCRM():
            words = self.CRM_words()
        elif self.isPSD():
            words = self.PSD_words()
        elif self.isRMS():
            words = self.RMS_words()
        elif self.isZERO():
            return self.ZERO_words()
        else:
            words = ['']
        return words

    def isATO(self):
        """Auto-Correlation Function"""
        if 'ATO' in self.tableName:
            return True
        return False

    def isCRM(self):
        """Correlated Root-Mean Square"""
        if 'CRM' in self.tableName:
            return True
        return False

    def isPSD(self):
        """Power Spectral Density"""
        if 'PSD' in self.tableName:
            return True
        return False

    def isRMS(self):
        """Root-Mean Square"""
        if 'RMS' in self.tableName:
            return True
        return False

    def isZERO(self):
        """Zero Crossings"""
        if 'NO' in self.tableName:
            return True
        return False


    def ATO_words(self):
        words = ['                                                 ( AUTO-CORRELATION FUNCTION )\n',' \n']
        return words

    def CRM_words(self):
        words = ['                                               ( CUMULATIVE ROOT MEAN SQUARE )\n',' \n']
        return words

    def PSD_words(self):
        words = ['                                             ( POWER SPECTRAL DENSITY FUNCTION )\n',' \n']
        return words

    def RMS_words(self):
        words = ['                                                     ( ROOT MEAN SQUARE )\n',' \n']
        return words
        
    def ZERO_words(self):
        words = ['                                                 ( NUMBER OF ZERO CROSSINGS )\n',' \n']
        return words

    def __repr__(self):
        #return ''
        if self.nonlinearFactor is not None:
            return self.__reprTransient__()

        msg = ['---DISPLACEMENTS---\n']
        msg.append(self.writeHeader())

        for nodeID,translation in sorted(self.translations.iteritems()):
            rotation = self.rotations[nodeID]
            gridType = self.gridTypes[nodeID]

            (dx,dy,dz) = translation
            (rx,ry,rz) = rotation

            msg2 = '%-10i %-8s ' %(nodeID,gridType)
            vals = [dx,dy,dz,rx,ry,rz]
            for val in vals:
                if abs(val)<1e-6:
                    msg2 += '%10s ' %(0)
                else:
                    msg2 += '%10.3e ' %(val)
                ###
            msg2 = '\n'
            msg.append(msg2)
        return ''.join(msg)

    def __reprTransient__(self):
        msg = ['---TRANSIENT DISPLACEMENTS---\n']
        msg.append(self.writeHeader())
        
        for dt,translations in sorted(self.translations.iteritems()):
            msg2 = '%s = %g\n' %(self.dataCode['name'],dt)
            for nodeID,translation in sorted(translations.iteritems()):
                rotation = self.rotations[dt][nodeID]
                gridType = self.gridTypes[nodeID]
                (dx,dy,dz) = translation
                (rx,ry,rz) = rotation

                msg2 += '%-10i %8s ' %(nodeID,gridType)
                vals = [dx,dy,dz,rx,ry,rz]
                for val in vals:
                    if abs(val)<1e-6:
                        msg2 += '%10s ' %(0)
                    else:
                        msg2 += '%10.3e ' %(val)
                    ###
                msg2 += '\n'
                msg.append(msg2)
            ###
        return ''.join(msg)

class complexDisplacementObject(complexTableObject): # approachCode=1, sortCode=0, thermal=0
    def __init__(self,dataCode,isSort1,iSubcase,dt=None):
        complexTableObject.__init__(self,dataCode,isSort1,iSubcase,dt)

    def writeF06(self,header,pageStamp,pageNum=1,f=None):
        words = ['                                       C O M P L E X   D I S P L A C E M E N T   V E C T O R\n',
                 '                                                          (REAL/IMAGINARY)\n',
                 ' \n',
                 '      POINT ID.   TYPE          T1             T2             T3             R1             R2             R3\n']
        return self._writeF06TransientBlock(words,header,pageStamp,pageNum,f)

    def __repr__(self):
        return self.writeF06(['','',''],'PAGE ',1)[0]

        msg = '---COMPLEX DISPLACEMENTS---\n'
        #if self.dt is not None:
        #    msg += '%s = %g\n' %(self.dataCode['name'],self.dt)
        headers = ['DxReal','DxImag','DyReal','DyImag','DzReal','DyImag','RxReal','RxImag','RyReal','RyImag','RzReal','RzImag']
        msg += '%-10s ' %('nodeID')
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for freq,translations in sorted(self.translations.iteritems()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)

            for nodeID,translation in sorted(translations.iteritems()):
                rotation = self.rotations[freq][nodeID]

                msg += '%-10i ' %(nodeID)
                vals = translation+rotation
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %(0)
                    else:
                        msg += '%10.3e ' %(val)
                    ###
                msg += '\n'
            ###
        return msg
