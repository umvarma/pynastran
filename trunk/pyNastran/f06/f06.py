import os
import sys

class EndOfFileError(Exception):
    pass

class DisplacementObject(object):
    def __init__(self,subcaseID,data):
        #print "*******"
        self.subcaseID = subcaseID
        self.grids = []
        self.gridTypes = []
        self.translations = []
        self.rotations = []
        self.addData(data)
        
    def addData(self,data):
        for line in data:
            (gridID,gridType,t1,t2,t3,t4,t5,t6) = line
            self.grids.append(gridID)
            self.gridTypes.append(gridType)
            self.translations.append([t1,t2,t3])
            self.rotations.append([t4,t5,t6])
        ###
        #print "grids = ",self.grids
    
    def __repr__(self):
        msg  = "SubcaseID = %s\n" %(self.subcaseID)
        msg += '%-8s %8s %10s %10s %10s %10s %10s %10s\n' %('gridID','gridType','t1','t2','t3','t4','t5','t6')
        for (gridID,gridType,translation,rotation) in zip(self.grids,self.gridTypes,self.translations,self.rotations):
            (t1,t2,t3) = translation
            (t4,t5,t6) = rotation
            msg += "%-8i %8s %10.4g %10.4g %10.4g %10.4g %10.4g %10.4g\n" %(gridID,gridType,t1,t2,t3,t4,t5,t6)
        ###
        return msg

class TemperatureObject(object):
    def __init__(self,subcaseID,data):
        #print "*******"
        self.subcaseID = subcaseID
        self.grids = []
        self.gridTypes = []
        self.temps = []
        self.addData(data)

    def addData(self,data):
        for line in data:
            (gridID,gridType) = line[0:2]
            temps = line[2:]
            for (i,temp) in enumerate(temps):
                self.grids.append(gridID+i)
                self.gridTypes.append(gridType)
                self.temps.append(temp)
        ###
        #print "grids = ",self.grids

    def __repr__(self):
        msg  = "SubcaseID = %s\n" %(self.subcaseID)
        msg += '%-8s %8s %10s\n' %('gridID','gridType','T')
        for (grid,gridType,temp) in zip(self.grids,self.gridTypes,self.temps):
            msg += "%-8s %8s %10s\n" %(grid,gridType,temp)
            
        return msg

class StressObject(object):
    def __init__(self,subcaseID,data):
        self.subcaseID = subcaseID
        self.grids = []
        #self.gridTypes = []
        #self.translations = []
        #self.rotations = []
        
        self.data = []
        self.addData(data)
        
    def addData(self,data):
        for line in data:
            self.data.append(line)
        return
            #(gridID,gridType,t1,t2,t3,t4,t5,t6) = line
            #self.grids.append(gridID)
            #self.gridTypes.append(gridType)
            #self.translations.append([t1,t2,t3])
            #self.rotations.append([t4,t5,t6])
        ###
        #print "grids = ",self.grids
    
    def __repr__(self):
        msg  = 'Composite Shell Element Stress\n'
        msg += "SubcaseID = %s\n" %(self.subcaseID)
        for line in self.data:
            msg += '%s\n' %(line)
        return msg
            
        msg += '%-8s %8s %10s %10s %10s %10s %10s %10s\n' %('gridID','gridType','t1','t2','t3','t4','t5','t6')
        for (gridID,gridType,translation,rotation) in zip(self.grids,self.gridTypes,self.translations,self.rotations):
            (t1,t2,t3) = translation
            (t4,t5,t6) = rotation
            msg += "%-8i %8s %10.4g %10.4g %10.4g %10.4g %10.4g %10.4g\n" %(gridID,gridType,t1,t2,t3,t4,t5,t6)
        ###
        return msg

class IsoStressObject(object):
    def __init__(self,subcaseID,data,isFiberDistance,isVonMises):
        self.subcaseID = subcaseID
        self.grids = []
        self.isFiberDistance = isFiberDistance
        self.isVonMises = isVonMises

        self.data = []
        self.addData(data)
        
    def addData(self,data):        
        for line in data:
            self.data.append(line)
        return
    
    def __repr__(self):
        msg  = 'Isotropic Shell Element Stress\n'
        msg += "SubcaseID = %s\n" %(self.subcaseID)
        for line in self.data:
            msg += '%s\n' %(line)
        return msg

class BarStressObject(object):
    def __init__(self,subcaseID,data):
        self.subcaseID = subcaseID
        self.grids = []

        self.data = []
        self.addData(data)
        
    def addData(self,data):        
        for line in data:
            self.data.append(line)
        return

    def __repr__(self):
        msg  = 'Bar Element Stress\n'
        msg += "SubcaseID = %s\n" %(self.subcaseID)
        for line in self.data:
            msg += '%s\n' %(line)
        return msg

class SolidStressObject(object):
    def __init__(self,subcaseID,data):
        self.subcaseID = subcaseID
        self.grids = []

        self.data = []
        self.addData(data)
        
    def addData(self,data):        
        for line in data:
            self.data.append(line)
        return

    def __repr__(self):
        msg  = 'solid Element Stress\n'
        msg += "SubcaseID = %s\n" %(self.subcaseID)
        for line in self.data:
            msg += '%s\n' %(line)
        return msg

class F06Reader(object):
    def __init__(self,f06name):
        self.f06name = f06name
        self.i = 0
        self.markerMap = {
          #'N A S T R A N    F I L E    A N D    S Y S T E M    P A R A M E T E R    E C H O':self.fileSystem,
          #'N A S T R A N    E X E C U T I V E    C O N T R O L    E C H O':self.executiveControl,
          #'C A S E    C O N T R O L    E C H O ':self.caseControl,
          #'M O D E L   S U M M A R Y':self.summary,
          
          #'E L E M E N T   G E O M E T R Y   T E S T   R E S U L T S   S U M M A R Y'
          #'O U T P U T   F R O M   G R I D   P O I N T   W E I G H T   G E N E R A T O R'
          #'OLOAD    RESULTANT':self.oload,
          'MAXIMUM  SPCFORCES':self.maxSpcForces,
          'MAXIMUM  DISPLACEMENTS': self.maxDisplacements,
          'MAXIMUM  APPLIED LOADS': self.maxAppliedLoads,
          #'G R I D   P O I N T   S I N G U L A R I T Y   T A B L E': self.gridPointSingularities,


#------------------------
#    N O N - D I M E N S I O N A L   S T A B I L I T Y   A N D   C O N T R O L   D E R I V A T I V E   C O E F F I C I E N T S
#          N O N - D I M E N S I O N A L    H I N G E    M O M E N T    D E R I V A T I V E   C O E F F I C I E N T S
#                               A E R O S T A T I C   D A T A   R E C O V E R Y   O U T P U T   T A B L E S
#                              S T R U C T U R A L   M O N I T O R   P O I N T   I N T E G R A T E D   L O A D S
#------------------------


          'D I S P L A C E M E N T   V E C T O R':self.displacement,
          'F O R C E S   O F   S I N G L E - P O I N T   C O N S T R A I N T':self.spcForces,
          'F O R C E S   O F   M U L T I P O I N T   C O N S T R A I N T': self.mpcForces,
          #'G R I D   P O I N T   F O R C E   B A L A N C E':self.gridPointForces,
          #'S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )': self.quadStress,
          #'S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )': self.triStress,
          
          'S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S   ( Q U A D 4 )': self.quadCompositeStress,


          'S T R E S S E S   I N   B A R   E L E M E N T S          ( C B A R )':self.barStress,
          'S T R E S S E S   I N   H E X A H E D R O N   S O L I D   E L E M E N T S   ( H E X A )':self.solidStressHexa,
          'S T R E S S E S   I N   P E N T A H E D R O N   S O L I D   E L E M E N T S   ( P E N T A )':self.solidStressPenta,
          'S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )        OPTION = BILIN': self.quadStress,
          #'S T R E S S E S   I N   R O D   E L E M E N T S      ( C R O D )'
          'S T R E S S E S   I N    T E T R A H E D R O N   S O L I D   E L E M E N T S   ( C T E T R A )':self.solidStressTetra,
          'S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )': self.triStress,


          'T E M P E R A T U R E   V E C T O R':self.temperatureVector,
          'F I N I T E   E L E M E N T   T E M P E R A T U R E   G R A D I E N T S   A N D   F L U X E S':self.tempGradientsFluxes,

          #'* * * END OF JOB * * *': self.end(),
         }
        self.markers = self.markerMap.keys()
        self.infile = open(self.f06name,'r')
        self.storedLines = []

        self.disp = {}
        self.SpcForces = {}
        self.stress = {}
        self.isoStress = {}
        self.barStress = {}
        self.subcaseIDs = []
        self.solidStress = {}
        self.temperature = {}

    def gridPointSingularities(self):
        """
                    G R I D   P O I N T   S I N G U L A R I T Y   T A B L E
        POINT    TYPE   FAILED      STIFFNESS       OLD USET           NEW USET
         ID            DIRECTION      RATIO     EXCLUSIVE  UNION   EXCLUSIVE  UNION
          1        G      4         0.00E+00          B        F         SB       S    *
          1        G      5         0.00E+00          B        F         SB       S    *
        """
        pass

    def maxSpcForces(self):
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int,float,float,float,float,float,float])
        print "max SPC Forces   ",data
        #self.disp[subcaseID] = DisplacementObject(subcaseID,data)
        #print self.disp[subcaseID]

    def maxDisplacements(self):
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int,float,float,float,float,float,float])
        print "max Displacements",data
        #self.disp[subcaseID] = DisplacementObject(subcaseID,data)
        #print self.disp[subcaseID]
    
    def maxAppliedLoads(self):
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int,float,float,float,float,float,float])
        print "max Applied Loads",data
        #self.disp[subcaseID] = DisplacementObject(subcaseID,data)
        #print self.disp[subcaseID]

    def readSubcaseNameID(self):
        subcaseName = self.storedLines[-3].strip()
        subcaseID   = self.storedLines[-2].strip()[1:]
        subcaseID = int(subcaseID.strip('SUBCASE '))
        #print "subcaseName=%s subcaseID=%s" %(subcaseName,subcaseID)

        transient   = self.storedLines[-1].strip()
        if transient:
            transWord,transValue = transient.split('=')
            transient = [transWord,transValue]
        else:
            transient = None
        return (subcaseName,subcaseID,transient)

    def displacement(self):
        """
                                             D I S P L A C E M E N T   V E C T O R
 
        POINT ID.   TYPE          T1             T2             T3             R1             R2             R3
               1      G      9.663032E-05   0.0           -2.199001E-04   0.0           -9.121119E-05   0.0
               2      G      0.0            0.0            0.0            0.0            0.0            0.0
               3      G      0.0            0.0            0.0            0.0            0.0            0.0
        """
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int,str,float,float,float,float,float,float])
        if subcaseID in self.disp:
            self.disp[subcaseID].addData(data)
        else:
            self.disp[subcaseID] = DisplacementObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)

    def temperatureVector(self):
        """
        LOAD STEP =  1.00000E+00
                                              T E M P E R A T U R E   V E C T O R
 
        POINT ID.   TYPE      ID   VALUE     ID+1 VALUE     ID+2 VALUE     ID+3 VALUE     ID+4 VALUE     ID+5 VALUE
               1      S      1.300000E+03   1.300000E+03   1.300000E+03   1.300000E+03   1.300000E+03   1.300000E+03
               7      S      1.300000E+03   1.300000E+03   1.300000E+03   1.300000E+03
        """
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        #print transient
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTemperatureTable()
        if subcaseID in self.temperature:
            self.temperature[subcaseID].addData(data)
        else:
            self.temperature[subcaseID] = TemperatureObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)

    def readTemperatureTable(self):
        data = []
        Format = [int,str,float,float,float,float,float,float]
        while 1:
            line = self.infile.readline()[1:].rstrip('\r\n ')
            if 'PAGE' in line:
                return data
            sline = [line[0:15],line[15:22].strip(),line[22:40],line[40:55],line[55:70],line[70:85],line[85:100]]
            sline = self.parseLineTemperature(sline,Format)
            data.append(sline)
        return data

    def parseLineTemperature(self,sline,Format):
        out = []
        for entry,iFormat in zip(sline,Format):
            if entry is '':
                return out
            #print "sline=|%r|\n entry=|%r| format=%r" %(sline,entry,iFormat)
            entry2 = iFormat(entry)
            out.append(entry2)
        return out
    
    def tempGradientsFluxes(self):
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        #print transient
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readGradientFluxesTable()
        print data
        if subcaseID in self.temperature:
            self.temperature[subcaseID].addData(data)
        else:
            self.temperature[subcaseID] = TemperatureGradientObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)
    
    def readGradientFluxesTable(self):
        data = []
        Format = [int,str,float,float,float, float,float,float]
        while 1:
            line = self.infile.readline()[1:].rstrip('\r\n ')
            if 'PAGE' in line:
                return data
            sline = [line[0:15],line[15:24].strip(),line[24:44],line[44:61],line[61:78],line[78:95],line[95:112],line[112:129]]
            sline = self.parseLineGradientsFluxes(sline,Format)
            data.append(sline)
        return data

    def parseLineGradientsFluxes(self,sline,Format):
        out = []
        for entry,iFormat in zip(sline,Format):
            if entry.strip() is '':
                out.append(0.0)
            else:
                #print "sline=|%r|\n entry=|%r| format=%r" %(sline,entry,iFormat)
                entry2 = iFormat(entry)
                out.append(entry2)
            ###
        return out
    
    def spcForces(self):
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int,str,float,float,float,float,float,float])

        if subcaseID in self.SpcForces:
            self.SpcForces[subcaseID].addData(data)
        else:
            self.SpcForces[subcaseID] = DisplacementObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)
        #print self.SpcForces[subcaseID]
        
    def mpcForces(self):
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int,str,float,float,float,float,float,float])

        if subcaseID in self.MpcForces:
            self.MpcForces[subcaseID].addData(data)
        else:
            self.MpcForces[subcaseID] = DisplacementObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)
        #print self.SpcForces[subcaseID]
        
    def barStress(self):
        """
                                       S T R E S S E S   I N   B A R   E L E M E N T S          ( C B A R )
        ELEMENT        SA1            SA2            SA3            SA4           AXIAL          SA-MAX         SA-MIN     M.S.-T
          ID.          SB1            SB2            SB3            SB4           STRESS         SB-MAX         SB-MIN     M.S.-C
             12    0.0            0.0            0.0            0.0            1.020730E+04   1.020730E+04   1.020730E+04 
                   0.0            0.0            0.0            0.0                           1.020730E+04   1.020730E+04 
        """
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(2)
        print "headers = %s" %(headers)
        
        #isFiberDistance = False
        #isVonMises = False  # Von Mises/Max Shear
        #if 'DISTANCE' in headers:
        #    isFiberDistance = True
        #if 'VON MISES' in headers:
        #    isVonMises = True

        data = self.readBarStress()
        if subcaseID in self.barStress:
            self.barStress[subcaseID].addData(data)
        else:
            self.barStress[subcaseID] = BarStressObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)
    
    def readBarStress(self):
        """
        ELEMENT        SA1            SA2            SA3            SA4           AXIAL          SA-MAX         SA-MIN     M.S.-T
          ID.          SB1            SB2            SB3            SB4           STRESS         SB-MAX         SB-MIN     M.S.-C
             12    0.0            0.0            0.0            0.0            1.020730E+04   1.020730E+04   1.020730E+04 
                   0.0            0.0            0.0            0.0                           1.020730E+04   1.020730E+04 
        """
        data = []
        while 1:
            line = self.infile.readline()[1:].strip().split()
            if 'PAGE' in line:
                break
            print line
            sline = self.parseLine(line,[int,float,float,float,float, float, float,float,float]) # line 1
            sline = ['CBAR']+sline
            #data.append(sline)
            line = self.infile.readline()[1:].strip().split()
            sline += self.parseLine(line,[    float,float,float,float,        float,float,float]) # line 2
            data.append(sline)
            self.i+=2
            ###
        ###
        #print "--------"
        #for line in data:
        #    print line
        #sys.exit()
        return data

    def quadCompositeStress(self):
        """
                       S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E   E L E M E N T S   ( Q U A D 4 )
        ELEMENT  PLY  STRESSES IN FIBER AND MATRIX DIRECTIONS    INTER-LAMINAR  STRESSES  PRINCIPAL STRESSES (ZERO SHEAR)      MAX
          ID      ID    NORMAL-1     NORMAL-2     SHEAR-12     SHEAR XZ-MAT  SHEAR YZ-MAT  ANGLE    MAJOR        MINOR        SHEAR
            181    1   3.18013E+04  5.33449E+05  1.01480E+03   -7.06668E+01  1.90232E+04   89.88  5.33451E+05  3.17993E+04  2.50826E+05
            181    2   1.41820E+05  1.40805E+05  1.25412E+05   -1.06000E+02  2.85348E+04   44.88  2.66726E+05  1.58996E+04  1.25413E+05
        """
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        data = self.readTable([int,int,float,float,float,float,float,float,float,float,float])
        if subcaseID in self.stress:
            self.stress[subcaseID].addData(data)
        else:
            self.stress[subcaseID] = StressObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)
        #print self.stress[subcaseID]
        
    def triStress(self):
        """
                                 S T R E S S E S   I N   T R I A N G U L A R   E L E M E N T S   ( T R I A 3 )
        ELEMENT      FIBER               STRESSES IN ELEMENT COORD SYSTEM             PRINCIPAL STRESSES (ZERO SHEAR)                 
          ID.       DISTANCE           NORMAL-X       NORMAL-Y      SHEAR-XY       ANGLE         MAJOR           MINOR        VON MISES
              8   -1.250000E-01     -1.303003E+02   1.042750E+04  -1.456123E+02   -89.2100    1.042951E+04   -1.323082E+02   1.049629E+04
                   1.250000E-01     -5.049646E+02   1.005266E+04  -2.132942E+02   -88.8431    1.005697E+04   -5.092719E+02   1.032103E+04
        """
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(2)
        #print "headers = %s" %(headers)
        
        isFiberDistance = False
        isVonMises = False  # Von Mises/Max Shear
        if 'DISTANCE' in headers:
            isFiberDistance = True
        if 'VON MISES' in headers:
            isVonMises = True

        data = self.readTriStress()
        if subcaseID in self.isoStress:
            self.isoStress[subcaseID].addData(data)
        else:
            self.isoStress[subcaseID] = IsoStressObject(subcaseID,data,isFiberDistance,isVonMises)
        self.subcaseIDs.append(subcaseID)

    def readTriStress(self):
        """
                ELEMENT      FIBER               STRESSES IN ELEMENT COORD SYSTEM             PRINCIPAL STRESSES (ZERO SHEAR)                 
                  ID.       DISTANCE           NORMAL-X       NORMAL-Y      SHEAR-XY       ANGLE         MAJOR           MINOR        VON MISES
                      8   -1.250000E-01     -1.303003E+02   1.042750E+04  -1.456123E+02   -89.2100    1.042951E+04   -1.323082E+02   1.049629E+04
                           1.250000E-01     -5.049646E+02   1.005266E+04  -2.132942E+02   -88.8431    1.005697E+04   -5.092719E+02   1.032103E+04
        """
        data = []
        while 1:
            line = self.infile.readline()[1:].strip().split()
            if 'PAGE' in line:
                break
            print line
            sline = self.parseLine(line,[int,float, float,float,float, float,float,float, float]) # line 1
            sline = ['CTRIA3']+sline
            data.append(sline)
            line = self.infile.readline()[1:].strip().split()
            sline = self.parseLine(line,[    float, float,float,float, float,float,float, float]) # line 2
            data.append(sline)
            self.i+=2
            ###
        ###
        return data

    def quadStress(self):
        """
                             S T R E S S E S   I N   Q U A D R I L A T E R A L   E L E M E N T S   ( Q U A D 4 )        OPTION = BILIN

        ELEMENT              FIBER            STRESSES IN ELEMENT COORD SYSTEM         PRINCIPAL STRESSES (ZERO SHEAR)
          ID      GRID-ID   DISTANCE        NORMAL-X      NORMAL-Y      SHEAR-XY      ANGLE        MAJOR         MINOR       VON MISES
              6    CEN/4  -1.250000E-01  -4.278394E+02  8.021165E+03 -1.550089E+02   -88.9493   8.024007E+03 -4.306823E+02  8.247786E+03
                           1.250000E-01   5.406062E+02  1.201854E+04 -4.174177E+01   -89.7916   1.201869E+04  5.404544E+02  1.175778E+04

                       4  -1.250000E-01  -8.871141E+02  7.576036E+03 -1.550089E+02   -88.9511   7.578874E+03 -8.899523E+02  8.060780E+03
                           1.250000E-01  -8.924081E+01  1.187899E+04 -4.174177E+01   -89.8002   1.187913E+04 -8.938638E+01  1.192408E+04
        """
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(3)
        #print "headers = %s" %(headers)
        
        isFiberDistance = False
        isVonMises = False  # Von Mises/Max Shear
        if 'DISTANCE' in headers:
            isFiberDistance = True
        if 'VON MISES' in headers:
            isVonMises = True

        data = self.readQuadBilinear()
        if subcaseID in self.isoStress:
            self.isoStress[subcaseID].addData(data)
        else:
            self.isoStress[subcaseID] = IsoStressObject(subcaseID,data,isFiberDistance,isVonMises)
        self.subcaseIDs.append(subcaseID)

    def readQuadBilinear(self):
        data = []
        while 1:
            if 1: # CEN/4
                line = self.infile.readline()[1:].strip().split()
                if 'PAGE' in line:
                    return data
                sline = self.parseLine(line,[int,str,float, float,float,float, float,float,float, float]) # line 1
                sline = ['CQUAD4']+sline
                data.append(sline)
                line = self.infile.readline()[1:].strip().split()
                sline = self.parseLine(line,[        float, float,float,float, float,float,float, float]) # line 2
                data.append(sline)
                line = self.infile.readline() # blank line
                self.i+=3
            ###
            for i in range(4):
                line = self.infile.readline()[1:].strip().split()
                sline = self.parseLine(line,[int,float, float,float,float, float,float,float, float]) # line 1
                data.append(sline)
                line = self.infile.readline()[1:].strip().split()
                sline = self.parseLine(line,[    float, float,float,float, float,float,float, float]) # line 2
                data.append(sline)
                line = self.infile.readline() # blank line
                self.i+=3
            ###
        ###
        return data

    def solidStressHexa(self):
        return self.readSolidStress('CHEXA',8)
    def solidStressPenta(self):
        return self.readSolidStress('CPENTA',6)
    def solidStressTetra(self):
        return self.readSolidStress('CTETRA',4)

    def readSolidStress(self,eType,n):
        (subcaseName,subcaseID,transient) = self.readSubcaseNameID()
        headers = self.skip(2)
        print "headers = %s" %(headers)
        
        data = self.read3DStress(eType,n)
        if subcaseID in self.solidStress:
            self.solidStress[subcaseID].addData(data)
        else:
            self.solidStress[subcaseID] = SolidStressObject(subcaseID,data)
        self.subcaseIDs.append(subcaseID)

    def read3DStress(self,eType,n):
        data = []
        while 1:
            line = self.infile.readline().rstrip('\n\r') #[1:]
                    #              CENTER         X          #          XY             #        A         #
            sline = [line[1:17],line[17:24],line[24:28],line[28:43],line[43:47],line[47:63],line[63:66],line[66:80],  line[80:83],line[83:88],line[88:93],line[93:98],line[99:113],line[113:130]]
            sline = [s.strip() for s in sline]
            if 'PAGE' in line:
                break
            elif '' is not sline[0]:
                sline = [eType]+sline
            data.append(sline)
        ###
        return data

    def readTable(self,Format):
        """reads displacement, spc/mpc forces"""
        sline = True
        data = []
        while sline:
            sline = self.infile.readline()[1:].strip().split()
            self.i+=1
            sline = self.parseLine(sline,Format)
            if sline is None:
                return data
            data.append(sline)
        return data
    
    def parseLine(self,sline,Format):
        out = []
        for entry,iFormat in zip(sline,Format):
            try:
                entry2 = iFormat(entry)
            except:
                #print "sline=|%s|\n entry=|%s| format=%s" %(sline,entry,iFormat)
                return None
            out.append(entry2)
        return out
        
    def ReadF06(self):
        #print "reading..."
        blank = 0
        while 1:
            if self.i%1000==0:
                print "i=%i" %(self.i)
            line = self.infile.readline()
            marker = line[1:].strip()
            
            #print "marker = %s" %(marker)
            if marker in self.markers:
                blank = 0
                print "\n*marker = %s" %(marker)
                self.markerMap[marker]()
                self.storedLines = []
            elif marker=='':
                blank +=1
                if blank==20:
                    break
            elif self.isMarker(marker): # marker with space in it (e.g. Model Summary)
                print "***marker = |%s|" %(marker)
                
            else:
                blank = 0
            ###
            self.storedLines.append(line)
            self.i+=1
        print "i=%i" %(self.i)
        self.infile.close()

    def isMarker(self,marker):
        """returns True if the word follows the 'N A S T R A N   P A T T E R N'"""
        marker = marker.strip().split('$')[0].strip()

        if len(marker)<2 or marker=='* * * * * * * * * * * * * * * * * * * *':
            return False
        for i,char in enumerate(marker):
            #print "i=%s i%%2=%s char=%s" %(i,i%2,char)
            if i%2==1 and ' ' is not char:
                return False
            elif i%2==0 and ' '==char:
                return False
            ###
        ###
        return True
            
    def skip(self,iskip):
        for i in range(iskip-1):
            self.infile.readline()
        self.i += iskip
        return self.infile.readline()
    
    def __repr__(self):
        msg = ''
        data = [self.disp,self.SpcForces,self.stress,self.isoStress,self.barStress,self.solidStress,self.temperature]
        data = []
        self.subcaseIDs = list(set(self.subcaseIDs))
        for subcaseID in self.subcaseIDs:
            for result in data:
                if subcaseID in result:
                    msg += str(result[subcaseID])
                ###
            ###
        return msg

if __name__=='__main__':
    f06 = F06Reader('cylinder01.f06')
    #f06 = F06Reader('ssb.f06')
    #f06 = F06Reader('quad_bending_comp.f06')
    f06.ReadF06()
    print f06
