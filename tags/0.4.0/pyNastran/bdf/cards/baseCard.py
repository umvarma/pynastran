## GNU Lesser General Public License
## 
## Program pyNastran - a python interface to NASTRAN files
## Copyright (C) 2011-2012  Steven Doyle, Al Danial
## 
## Authors and copyright holders of pyNastran
## Steven Doyle <mesheb82@gmail.com>
## Al Danial    <al.danial@gmail.com>
## 
## This file is part of pyNastran.
## 
## pyNastran is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## pyNastran is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with pyNastran.  If not, see <http://www.gnu.org/licenses/>.
## 
from __future__ import print_function
import sys

import pyNastran
import pyNastran.bdf

from pyNastran.bdf.errors                import *
from pyNastran.bdf.fieldWriter           import printCard,setBlankIfDefault,setDefaultIfBlank,isSame
from pyNastran.bdf.bdfInterface.BDF_Card import BDF_Card

class BaseCard(BDF_Card):
    #def __init__(self,card):
    #    pass

    #def wipeEmptyFields(self,card): # BaseCard

    def writeCodeAster(self):
        return '# skipping %s\n' %(self.type)

    def verify(self,model,iSubcase):
        """
        this method checks performs checks on the cards such as
        that the PBEAML has a proper material type
        """
        pass

    def isSameFields(self,fields1,fields2):
        for (field1,field2) in zip(fields1,fields2):
            if not isSame(field1,field2):
                return False
            ###
        ###
        return True

    def Is(self,typeCheck):
        """retruns True if the card type is the same as the object"""
        if self.type==typeCheck:
            return True
        return False

    def removeTrailingNones(self,fields):
        """removes blank fields at the end of a card object"""
        self.wipeEmptyFields(fields)

    def printCard(self,fields,tol=0.):
        """prints a card object"""
        #print "fields = ",fields
        return printCard(fields,tol)

    def setDefaultIfBlank(self,value,default):
        """used to initialize default values"""
        #raise Exception('time to upgrade...')
        return setDefaultIfBlank(value,default)

    def setBlankIfDefault(self,value,default):
        """used to set default values for object repr functions"""
        return setBlankIfDefault(value,default)

    def crossReference(self,model):
        #self.mid = model.Material(self.mid)
        raise Exception('%s needs to implement this method' %(self.type))

   # def off_expandThru(self,fields):
   #     """
   #     not used...
   #     expands a list of values of the form [1,5,THRU,10,13]
   #     to be [1,5,6,7,8,9,10,13]
   #     """
   #     nFields = len(fields)
   #     fieldsOut = []
   #     for i in range(nFields):
   #         if fields[i]=='THRU':
   #             for j in range(fields[i-1],fields[i+1]):                    
   #                 fieldsOut.append(fields[j])
   #             ###
   #         else:
   #             fieldsOut.append(fields[i])
   #         ###
   #     ###
   #     return fieldsOut

    def expandThru(self,fields):
        """
        expands a list of values of the form [1,5,THRU,9,13]
        to be [1,5,6,7,8,9,13]
        """
        if len(fields)==1: return fields
        #print "expandThru"
        #print "fields = ",fields
        out = []
        nFields = len(fields)
        i=0
        while(i<nFields):
            if fields[i]=='THRU':
                for j in range(fields[i-1],fields[i+1]+1):
                    out.append(j)
                ###
                i+=2
            else:
                out.append(fields[i])
                i+=1
            ###
        ###
        #print "out = ",out,'\n'
        return list(set(out))
    
    def expandThruBy(self,fields):
        """
        expands a list of values of the form [1,5,THRU,9,BY,2,13]
        to be [1,5,7,9,13]
        @todo not tested
        @note used for QBDY3, ???
        """
        if len(fields)==1: return fields
        #print "expandThruBy"
        #print "fields = ",fields
        out = []
        nFields = len(fields)
        i=0
        by = 1
        while(i<nFields):
            if fields[i]=='THRU':
                by = 1
                if i+2<nFields and fields[i+2]=='BY':
                    by = fields[i+3]
                    #sys.stderr.write("BY was found...untested...")
                    #raise NotImplementedError('implement BY support\nfields=%s' %(fields))
                else:
                    by = 1
                minValue = fields[i-1]
                maxValue = fields[i+1]
                #print "minValue=%s maxValue=%s by=%s" %(minValue,maxValue,by)
                for j in range(0,(maxValue-minValue)//by+1): # +1 is to include final point
                    value = minValue+by*j
                    out.append(value)
                ###
                if by==1: # null/standard case
                    i+=2
                else:     # BY case
                    i+=3
                ###
            else:
                out.append(fields[i])
                i+=1
            ###
        ###
        #out = list(set(out))
        #out.sort()
        #print "out = ",out,'\n'
        #sys.exit()
        return list(set(out))

    def expandThruExclude(self,fields):
        """
        expands a list of values of the form [1,5,THRU,11,EXCEPT,7,8,13]
        to be [1,5,6,9,10,11,13]
        @todo not tested
        """
        nFields = len(fields)
        for i in range(nFields):
            if fields[i]=='THRU':
                storedList = []
                for j in range(fields[i-1],fields[i+1]):
                    storedList.append(fields[j])
                ###
            elif field[i]=='EXCLUDE':
                storedSet = set(storedList)
                while fields[i]<max(storedList):
                    storedSet.remove(field[i])
                storedList = list(storedSet)
            else:
                if storedList:
                    fieldsOut += storedList
                fieldsOut.append(fields[i])
            ###
        ###

    def collapseThru(self,fields):
        return fields

    def collapseThruBy(self,fields):
        return fields

    def _collapseThru(self,fields):
        """
        1,THRU,10
        1,3,THRU,19,15
        @warning doesnt work
        """
        fields = list(set(fields))
        
        #assumes sorted...

        pre,i = self._preCollapse(fields,dnMax=dnMax)
        mid = self._midCollapse(pre,dnMax=dnMax)
        #out = self._postCollapse(mid)
        #sys.exit()
        dnMax = 1

        out = []
        print("running post...")
        for data in mid:
            print("data = ",data)
            nData = len(data)
            if nData == 1:
                out.append(data[0]) # 1 field only
            else:
                assert data[2]==1 # dn
                out += [data[0],'THRU',data[1]]
            ###
        ###
        print("dataOut = ",out)
        return out
        ###

    def _midCollapse(self,preCollapse,dnMax=10000000):
        """
        input is lists of [[1,3,5,7],2]  dn=2
        dNmax = 2
        output is [1,7,2]
        """
        out = []
        print(preCollapse)
        for collapse in preCollapse:
            print("collapse = ",collapse)
            (data,dn) = collapse
            print("data = ",data)
            print("dn = ",dn)
            if len(data)>1:
                if dn<=dnMax: # 1:11:2 - patran syntax
                    fields = [data[0],data[-1],dn]
                    out.append(fields)
                ###
                else: # bigger than dn
                    for field in data:
                        out.append(field)
                    ###
                ###
            else: # 1 item
                out.append([data[0]])
            ###
        return out
    
    def _preCollapse(self,fields,dnMax=10000000): # assumes sorted
        out = []
        nFields = len(fields)-1
        i=0
        while(i<nFields):
            dn = fields[i+1]-fields[i]
            print("preFields = ",fields[i:])
            (outFields,j) = self._subCollapse(fields[i:],dn,dnMax)
            print("outFields = ",outFields)
            out.append([outFields,dn])
            i+=j
            ###
            #if i==nFields+1:
            #    out.append([[fields[i-1]],1])
            #    print("lastOut = ",out[-1])
            ###
        ###
        
        print("out = ",out,i)
        print("--end of preCollapse")
        return (out,i)

    def _subCollapse(self,fields,dn,dnMax=10000000):
        """
        in  = [1,2,3,  7]
        out = [1,2,3]
        """
        # dn=1
        print("subIn = ",fields)
        out = [fields[0]]
        nFields = len(fields)

        for i in range(1,nFields):
            dn = fields[i]-fields[i-1]
            print("i=%s field[%s]=%s fields[%s]=%s dn=%s dnMax=%s" %(i,i,fields[i],i-1,fields[i-1],dn,dnMax))
            if dn!=dnMax:
                #i+=1
                #out.append(fields[i])
                break
            out.append(fields[i])
            #if i==3:
            #    sys.exit()
        #i-=1
        print("subOut = ",out)
        #i+=1
        print("iSubEnd = %s\n" %(i))
        #sys.exit()
        return (out,i)
    ###
        
    def buildTableLines(self,fields,nStart=1,nEnd=0):
        """
        builds a table of the form:
        'DESVAR' DVID1 DVID2 DVID3 DVID4 DVID5 DVID6 DVID7
                 DVID8 -etc.-
        'UM'     VAL1  VAL2  -etc.-
        and then pads the rest of the fields with None's
        @param fields the fields to enter, including DESVAR
        @param nStart the number of blank fields at the start of the line (default=1)
        @param nEnd the number of blank fields at the end of the line (default=0)
        
        @note will be used for DVPREL2, RBE1, RBE3
        @warning only works for small field format???
        """
        fieldsOut = []
        n = 8-nStart-nEnd

        # pack all the fields into a list.  Only consider an entry as isolated
        for (i,field) in enumerate(fields):
            fieldsOut.append(field)
            if i>0 and i%n==0: # beginning of line
                #print "i=%s" %(i)
                #pad = [None]*(i+j)
                #fieldsOut += pad
                fieldsOut += [None]*(nStart+nEnd)
            ###
        ###
        # make sure they're aren't any trailing None's (from a new line)
        fieldsOut = self.wipeEmptyFields(fieldsOut)
        #print "fieldsOut = ",fieldsOut,len(fieldsOut)

        # push the next key (aka next fields[0]) onto the next line
        nSpaces = 8-(len(fieldsOut))%8  # puts UM onto next line
        #print "nSpaces[%s] = %s max=%s" %(fields[0],nSpaces,nSpaceMax)
        if nSpaces<8:
            fieldsOut += [None]*(nSpaces)
        #print ""
        return fieldsOut

    def isSameCard(self,card):
        fields1 = self.rawFields()
        fields2 = card.rawFields()
        return self.isSameFields(fields1,fields2)

    def printRawFields(self):
        """A card's raw fields include all defaults for all fields"""
        fields = self.rawFields()
        return self.printCard(fields)
        
    def reprFields(self):
        return self.rawFields()

    def __repr__(self):  # ,tol=1e-8
        """
        Prints a card in the simplest way possible
        (default values are left blank).
        """
        #print "tol = ",tol
        self.rawFields()
        fields = self.reprFields()
        try:
            return self.printCard(fields)
        except:
            print('problem printing %s card' %(self.type))
            print("fields = ",fields)
            raise
###

def Mid(self):
    #print str(self)
    if isinstance(self.mid,int):
        return self.mid
    else:
        return self.mid.mid
    ###

class Property(BaseCard):
    def __init__(self,card,data):
        assert card is None or data is None
        pass

    def Mid(self):
        return Mid(self)

    def isSameCard(self,prop):
        if self.type!=prop.type:  return False
        fields1 = self.rawFields()
        fields2 = prop.rawFields()
        return self.isSameFields(fields1,fields2)

    def crossReference(self,model):
        self.mid = model.Material(self.mid)

class Material(BaseCard):
    """Base Material Class"""
    def __init__(self,card,data):
        pass
        #self.type = card[0]

    def isSameCard(self,mat):
        if self.type!=mat.type:  return False
        fields1 = self.rawFields()
        fields2 = mat.rawFields()
        return self.isSameFields(fields1,fields2)

    def crossReference(self,model):
        pass

    def Mid(self):
        return self.mid

class Element(BaseCard):
    pid = 0 # CONM2, rigid
    def __init__(self,card,data):
        assert card is None or data is None
        ## the list of node IDs for an element (default=None)
        self.nodes = None
        #self.nids = []
        pass

    def isSameCard(self,element):
        return False

    def Pid(self):
        """returns the property ID of an element"""
        if isinstance(self.pid,int):
            return self.pid
        else:
            return self.pid.pid
        ###

    def nodePositions(self,nodes=None):
        """returns the positions of multiple node objects"""
        if not nodes:
           nodes = self.nodes
        return [node.Position() for node in nodes]

    def nodeIDs(self,nodes=None):
        """returns nodeIDs for repr functions"""
        if not nodes:
           nodes = self.nodes
        if isinstance(nodes[0],int):
            return [node     for node in nodes]
        else:
            return [node.nid for node in nodes]
        ###

    def prepareNodeIDs(self,nids,allowEmptyNodes=False):
        """verifies all node IDs exist and that they're integers"""
        self.nodes = []
        for nid in nids:
            if isinstance(nid,int):
                self.nodes.append(int(nid))
            elif nid==None and allowEmptyNodes:
                self.nodes.append(nid)
            else: # string???
                self.nodes.append(int(nid))
                #raise Exception('this element may not have missing nodes...nids=%s allowEmptyNodes=False' %(nids))
            ###

    def Centroid(self,nodes,debug=False):
        return None

    #def Normal(self,a,b):
    #    """finds the unit normal vector of 2 vectors"""
    #    return Normal(a,b)

    def CentroidTriangle(self,n1,n2,n3,debug=False):
        if debug:
            print("n1=%s \nn2=%s \nn3=%s" %(n1,n2,n3))
        centroid = (n1+n2+n3)/3.
        return centroid

    def Centroid(self):
        raise NotImplementedMethodError('Centroid not implemented in the %s class' %(self.__class__.__name__))
    def Length(self):
        raise NotImplementedMethodError('Length not implemented in the %s class' %(self.__class__.__name__))
    def Area(self):
        raise NotImplementedMethodError('Area not implemented in the %s class' %(self.__class__.__name__))
    def Volume(self):
        raise NotImplementedMethodError('Volume not implemented in the %s class' %(self.__class__.__name__))
    def Mass(self):
        raise NotImplementedMethodError('Mass not implemented in the %s class' %(self.__class__.__name__))

    def B(self):
        raise NotImplementedMethodError('B matrix not implemented in the %s class' %(self.__class__.__name__))
    def D(self):
        raise NotImplementedMethodError('D matrix not implemented in the %s class' %(self.__class__.__name__))
    def Jacobian(self):
        raise NotImplementedMethodError('Jacobian not implemented for %s' %(self.self.__class__.__name__))

    def stiffnessMatrix(self):
        raise NotImplementedMethodError('stiffnessMatrix not implemented in the %s class' %(self.__class__.__name__))
    def massMatrix(self):
        raise NotImplementedMethodError('massMatrix not implemented in the %s class' %(self.__class__.__name__))


#dnMax = 2
if __name__=='__main__':
    card = BaseCard()

    """
    1,THRU,10
    1,3,THRU,19,15
    """
    card.collapseThru([1,2,3,4,5,10])
    card.collapseThru([1,3,4,5,6,17])
