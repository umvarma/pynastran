from pyNastran.op2.resultObjects.op2_Objects import scalarObject


class OES_Object(scalarObject):
    def __init__(self,dataCode,iSubcase):
        scalarObject.__init__(self,dataCode,iSubcase)
        self.log.debug("starting OES...elementName=%s iSubcase=%s" %(self.elementName,self.iSubcase))
        #print self.dataCode

    def isCurvature(self):
        if self.stressBits[2]==0:
            return True
        return False

    def isFiberDistance(self):
        return not(self.isCurvature())

    def isVonMises(self):
        return not(self.isMaxShear())

    def isMaxShear(self):
        if self.stressBits[0]==0:
            return True
        return False

class stressObject(OES_Object):
    def __init__(self,dataCode,iSubcase):
        OES_Object.__init__(self,dataCode,iSubcase)

    def updateDt(self,dataCode,dt):
        self.dataCode = dataCode
        self.applyDataCode()
        #assert dt>=0.
        #print "dataCode=",self.dataCode
        self.elementName = self.dataCode['elementName']
        if dt is not None:
            self.log.debug("updating stress...%s=%s elementName=%s" %(self.dataCode['name'],dt,self.elementName))
            self.dt = dt
            self.addNewTransient()
        ###

    def isStrain(self):
        return True

    def isStress(self):
        return False
    

class strainObject(OES_Object):
    def __init__(self,dataCode,iSubcase):
        OES_Object.__init__(self,dataCode,iSubcase)

    def updateDt(self,dataCode,dt):
        self.dataCode = dataCode
        self.applyDataCode()
        #print "dataCode=",self.dataCode
        self.elementName = self.dataCode['elementName']
        #assert dt>=0.
        if dt is not None:
            self.log.debug("updating strain...%s=%s elementName=%s" %(self.dataCode['name'],dt,self.elementName))
            self.dt = dt
            self.addNewTransient()
        ###

    def isStress(self):
        return False
    
    def isStrain(self):
        return True
